# Setu & Setu-Translate Integration Analysis

## 📋 Overview

This document details how to integrate AI4Bharat's **Setu** (OCR/data pipeline) and **Setu-Translate** (translation) into the LandOwners Jamabandi processing system.

---

## 1️⃣ Understanding Setu (AI4Bharat/setu)

### Purpose
Setu is a **comprehensive data cleaning, filtering, and deduplication pipeline** built on Apache Spark. For our use case, we're interested in:

- **Document Preparation Stage**: Extracts text from PDFs using OCR
- **Cleaning & Analysis Stage**: Language identification and noise reduction
- **Filtering Stage**: Removes low-quality documents

### OCR Approach
Setu uses **GCP Cloud Vision SDK** for PDF OCR:
```python
# From setu/text_extraction.py
# Uses google.cloud.vision for OCR
# Outputs JSON with bounding box information
# Filters out pages with recognition issues
```

### Key Files in IndicLLMSuite/setu/setu/:
| File | Purpose |
|------|---------|
| `main.py` | Main pipeline orchestrator |
| `text_extraction.py` | OCR and text extraction stages |
| `clean_analysis.py` | Language detection (IndicLID, NLLB, cld3) |
| `flagging_and_removal.py` | Quality filtering |
| `configs/ocr/spark_urdu_config.json` | Urdu-specific configuration |

### Language Detection Libraries Used:
1. **IndicLID** - AI4Bharat's language identifier
2. **NLLB** - Facebook's language identification model
3. **Google cld3** - Compact Language Detector 3

---

## 2️⃣ Understanding Setu-Translate (AI4Bharat/setu-translate)

### Purpose
Large-scale translation pipeline using **IndicTrans2** for English ↔ 22 Indic Languages.

### Pipeline Stages (6 total):

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SETU-TRANSLATE PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  1. TEMPLATING         2. GLOBAL SENTENCE      3. BINARIZE                      │
│  ┌─────────────┐       ┌─────────────┐        ┌─────────────┐                   │
│  │ Document    │  ───► │ Extract     │  ───►  │ Tokenize    │                   │
│  │ to chunks   │       │ sentences   │        │ sentences   │                   │
│  │ + clean     │       │ by doc_id   │        │ + padding   │                   │
│  └─────────────┘       └─────────────┘        └─────────────┘                   │
│                                                      │                           │
│                                                      ▼                           │
│  6. REPLACE           5. DECODE                4. TRANSLATE                      │
│  ┌─────────────┐      ┌─────────────┐        ┌─────────────┐                    │
│  │ Put back    │ ◄─── │ Decode IDs  │  ◄───  │ IndicTrans2 │                    │
│  │ translations│      │ to text     │        │ inference   │                    │
│  │ in document │      │             │        │             │                    │
│  └─────────────┘      └─────────────┘        └─────────────┘                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Components:

#### A. IndicTransTokenizer (Critical!)
Location: `IndicLLMSuite/setu-translate/setu-translate/IndicTransTokenizer/`

```python
from IndicTransTokenizer import IndicProcessor, IndicTransTokenizer

# Initialize
ip = IndicProcessor(inference=True)
tokenizer = IndicTransTokenizer(direction="indic-en")  # For Urdu→English

# Preprocess
sentences = ip.preprocess_batch(texts, src_lang="urd_Arab", tgt_lang="eng_Latn")

# Tokenize
input_ids, attention_mask = tokenizer(sentences, src=True, padding="max_length")

# Postprocess
translations = ip.postprocess_batch(outputs, lang="eng_Latn", placeholder_entity_maps=ple_maps)
```

#### B. Supported Languages (Relevant for Jammu):
| Code | Language | Script |
|------|----------|--------|
| `urd_Arab` | Urdu | Arabic script |
| `kas_Arab` | Kashmiri | Arabic script |
| `hin_Deva` | Hindi | Devanagari |
| `pan_Guru` | Punjabi | Gurmukhi |
| `dog_Deva` | Dogri | Devanagari |
| `eng_Latn` | English | Latin |

#### C. Translation Model
- **Model**: `ai4bharat/indictrans2-en-indic-dist-200M` (HuggingFace)
- **Distilled**: 200M parameters (lighter than full model)
- **Bidirectional**: Can do Indic→English AND English→Indic

---

## 3️⃣ Integration Strategy for LandOwners

### What We DON'T Need:
- Apache Spark (overkill for single documents)
- Large-scale batch processing
- Cloud Vision SDK (we have our own OCR)
- Deduplication stages

### What We NEED:
1. **IndicTransTokenizer** - For preprocessing text before translation
2. **IndicTrans2 Model** - The actual translation
3. **IndicProcessor** - For pre/post processing
4. **Language codes mapping** - Urdu = `urd_Arab`, English = `eng_Latn`

---

## 4️⃣ Implementation Plan

### Step 1: Install IndicTransTokenizer
```bash
cd C:\Jammu\IndicLLMSuite\setu-translate\setu-translate\IndicTransTokenizer
pip install --editable ./
```

### Step 2: Install Required Dependencies
```bash
pip install transformers sentencepiece sacremoses nltk indicnlp
```

### Step 3: Create Lightweight Translation Wrapper

```python
# backend/utils/indictrans_translator.py

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransTokenizer import IndicProcessor, IndicTransTokenizer

class IndicTranslator:
    """Simplified IndicTrans2 wrapper for single document translation"""
    
    def __init__(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            "ai4bharat/indictrans2-indic-en-dist-200M",  # Indic→English
            trust_remote_code=True
        )
        self.ip = IndicProcessor(inference=True)
        self.tokenizer = IndicTransTokenizer(direction="indic-en")
        
    def translate(self, text: str, src_lang: str = "urd_Arab") -> str:
        """Translate single text from Indic language to English"""
        
        # Preprocess
        sentences = self.ip.preprocess_batch([text], src_lang=src_lang, tgt_lang="eng_Latn")
        
        # Tokenize
        inputs = self.tokenizer(sentences, src=True, padding=True, return_tensors="pt")
        
        # Generate translation
        outputs = self.model.generate(**inputs, max_length=256, num_beams=5)
        
        # Decode
        decoded = self.tokenizer.batch_decode(outputs, src=False)
        
        # Postprocess
        translations = self.ip.postprocess_batch(decoded, lang="eng_Latn")
        
        return translations[0] if translations else ""
```

### Step 4: Update setu_translator.py to use Real Model

Replace the fallback rule-based translation with actual IndicTrans2 model.

---

## 5️⃣ Language Mapping for Jamabandi

| Jamabandi Content | Setu Language Code | Script |
|-------------------|-------------------|--------|
| Urdu text | `urd_Arab` | Arabic |
| Kashmiri names | `kas_Arab` | Arabic |
| Hindi text (if any) | `hin_Deva` | Devanagari |
| Dogri names | `doi_Deva` | Devanagari |

### Direction for Translation:
- **Urdu → English**: `direction="indic-en"`, model: `indictrans2-indic-en-dist-200M`
- **English → Urdu**: `direction="en-indic"`, model: `indictrans2-en-indic-dist-200M`

---

## 6️⃣ Files to Create/Modify

### New Files:
1. `backend/utils/indictrans_translator.py` - Real IndicTrans2 integration
2. `backend/config/translation_config.py` - Translation settings

### Modify:
1. `backend/utils/setu_translator.py` - Use IndicTranslator instead of fallback
2. `backend/routes/translation_routes.py` - Add language selection options

---

## 7️⃣ Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | Not required (CPU works) | NVIDIA GPU with CUDA |
| RAM | 8GB | 16GB |
| Disk | 2GB (model cache) | 5GB |

The 200M distilled model runs on CPU, but GPU is 5-10x faster.

---

## 8️⃣ Testing Strategy

### Test 1: Basic Translation
```python
from utils.indictrans_translator import IndicTranslator

translator = IndicTranslator()
result = translator.translate("موضع اتما پور", src_lang="urd_Arab")
print(result)  # Should output: "Mauza Atmapur" or similar
```

### Test 2: Land Record Terms
```python
terms = [
    "جمع بندی",      # Jamabandi
    "خسرہ نمبر",     # Khasra Number
    "مالک",          # Owner
    "رقبہ",          # Area
]
for term in terms:
    print(f"{term} → {translator.translate(term)}")
```

### Test 3: Full Document
```python
# Use actual Jamabandi text from OCR
ocr_text = """موضع اتما پور تحصیل بشنال ضلع جموں
نمبر خسرہ: ۱۲۳
مالک: محمد علی ولد کریم"""

translation = translator.translate(ocr_text)
```

---

## 9️⃣ Quick Start Commands

```bash
# 1. Install IndicTransTokenizer
cd C:\Jammu\IndicLLMSuite\setu-translate\setu-translate\IndicTransTokenizer
pip install --editable ./

# 2. Install dependencies
pip install transformers sentencepiece sacremoses nltk
pip install indic-nlp-library

# 3. Download NLTK data
python -c "import nltk; nltk.download('punkt')"

# 4. Test import
python -c "from IndicTransTokenizer import IndicProcessor; print('Success!')"
```

---

## 🔟 Next Steps

1. [ ] Install IndicTransTokenizer package
2. [ ] Create `indictrans_translator.py` wrapper
3. [ ] Update `setu_translator.py` to use real model
4. [ ] Test with actual Jamabandi PDFs
5. [ ] Tune translation for land record terminology
6. [ ] Add caching for repeated terms

---

## References

- [AI4Bharat Setu GitHub](https://github.com/AI4Bharat/setu)
- [AI4Bharat Setu-Translate GitHub](https://github.com/AI4Bharat/setu-translate)
- [IndicTrans2 HuggingFace](https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M)
- [IndicNLP Library](https://github.com/anoopkunchukuttan/indic_nlp_library)
