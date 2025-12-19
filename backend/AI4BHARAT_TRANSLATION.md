# 🌐 AI4Bharat Translation Integration

## Self-Hosted Urdu/Hindi to English Translation

This project uses **AI4Bharat's IndicTrans2** and **IndicXlit** for high-quality, self-hosted translation of Jammu land records from Urdu/Hindi to English.

> **No external APIs required!** Everything runs locally on your machine.

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAND RECORD OCR PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  Urdu PDF    │───▶│   PyMuPDF    │───▶│  Urdu Text       │   │
│  │  (Input)     │    │   (OCR)      │    │  (Arabic Script) │   │
│  └──────────────┘    └──────────────┘    └────────┬─────────┘   │
│                                                    │             │
│                                                    ▼             │
│                      ┌────────────────────────────────────┐      │
│                      │         IndicXlit (Optional)       │      │
│                      │    Transliteration: urd → Roman    │      │
│                      │         (11M params, ~50MB)        │      │
│                      └────────────────┬───────────────────┘      │
│                                       │                          │
│                                       ▼                          │
│                      ┌────────────────────────────────────┐      │
│                      │          IndicTrans2               │      │
│                      │    Translation: urd_Arab → eng     │      │
│                      │        (200M params, ~800MB)       │      │
│                      └────────────────┬───────────────────┘      │
│                                       │                          │
│                                       ▼                          │
│                      ┌────────────────────────────────────┐      │
│                      │       English Text Output          │      │
│                      │    "Revenue Record of Atmapur"     │      │
│                      └────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt

# Install IndicTransToolkit (for tokenization)
pip install git+https://github.com/VarunGumma/IndicTransToolkit.git

# Optional: Install IndicXlit for transliteration
pip install ai4bharat-transliteration
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env (optional - defaults work fine)
```

### 3. Run Translation Test

```python
from translation import AI4BharatTranslator

# Initialize (first run downloads ~800MB model)
translator = AI4BharatTranslator()

# Translate Urdu to English
result = translator.translate(
    "جمع بندی موضع اتما پور",
    src_lang='ur',
    tgt_lang='en'
)

print(result['translated_text'])
# Output: "Revenue record of Atmapur village"
```

---

## 📦 Model Details

### IndicTrans2 (Translation)

| Property | Value |
|----------|-------|
| **Model** | `ai4bharat/indictrans2-indic-en-dist-200M` |
| **Size** | 200M parameters (~800MB download) |
| **Languages** | 22 Indic → English |
| **Architecture** | Transformer (distilled) |
| **License** | MIT |

### IndicXlit (Transliteration)

| Property | Value |
|----------|-------|
| **Package** | `ai4bharat-transliteration` |
| **Size** | 11M parameters (~50MB) |
| **Languages** | 21 Indic ↔ Roman |
| **Accuracy** | 90%+ on native words |
| **License** | MIT |

---

## 🌍 Supported Languages

### Full Translation Support (Indic → English)

| Language | Code | Script |
|----------|------|--------|
| **Urdu** | `urd_Arab` | Arabic (Nastaliq) |
| **Hindi** | `hin_Deva` | Devanagari |
| Bengali | `ben_Beng` | Bengali |
| Tamil | `tam_Taml` | Tamil |
| Telugu | `tel_Telu` | Telugu |
| Marathi | `mar_Deva` | Devanagari |
| Gujarati | `guj_Gujr` | Gujarati |
| Kannada | `kan_Knda` | Kannada |
| Malayalam | `mal_Mlym` | Malayalam |
| Punjabi | `pan_Guru` | Gurmukhi |
| Odia | `ory_Orya` | Odia |
| Assamese | `asm_Beng` | Bengali |
| Kashmiri | `kas_Arab` | Arabic |
| Sindhi | `snd_Arab` | Arabic |
| Nepali | `npi_Deva` | Devanagari |
| + 7 more | ... | ... |

---

## 💻 API Reference

### AI4BharatTranslator

```python
from translation import AI4BharatTranslator

# Initialize
translator = AI4BharatTranslator(auto_load=False)

# Check availability
translator.is_available()  # Returns True if PyTorch installed

# Load model (called automatically on first translate)
translator.load()

# Translate text
result = translator.translate(
    text="متن اردو",
    src_lang='ur',      # or 'urd_Arab'
    tgt_lang='en'       # or 'eng_Latn'
)

# Result structure
{
    'original_text': 'متن اردو',
    'translated_text': 'Urdu text',
    'source_lang': 'urd_Arab',
    'target_lang': 'eng_Latn',
    'confidence': 95.0,
    'method': 'indictrans2',
    'model': 'ai4bharat/indictrans2-indic-en-dist-200M'
}

# Batch translation
translations = translator.translate_batch(
    texts=["جمع", "موضع", "پٹوار"],
    src_lang='ur',
    tgt_lang='en'
)
```

### IndicXlitTransliterator

```python
from translation import IndicXlitTransliterator

# Initialize
xlit = IndicXlitTransliterator()

# Transliterate
result = xlit.transliterate(
    text="جموں",
    src_lang='ur'
)

# Result structure
{
    'original_text': 'جموں',
    'transliterated_text': 'jammu',
    'source_lang': 'urd',
    'target_lang': 'roman',
    'confidence': 90.0,
    'method': 'indicxlit'
}
```

### Quick Functions

```python
from translation import quick_translate, quick_transliterate

# One-liner translation
english = quick_translate("اردو متن", src='ur')

# One-liner transliteration  
roman = quick_transliterate("जम्मू", src='hi')
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI4BHARAT_DEVICE` | `auto` | `auto`, `cpu`, or `cuda` |
| `AI4BHARAT_CACHE_DIR` | `./models/ai4bharat` | Model cache directory |
| `TRANSLATION_MODE` | `ai4bharat` | `ai4bharat` or `dictionary` |

### Hardware Requirements

| Mode | RAM | GPU | Storage |
|------|-----|-----|---------|
| CPU-only | 4GB+ | None | 2GB |
| GPU (CUDA) | 4GB+ | 4GB+ VRAM | 3GB |

---

## 📁 Project Structure

```
backend/
├── translation/
│   ├── __init__.py                  # Module exports
│   ├── ai4bharat_translator.py      # IndicTrans2 wrapper ⭐
│   ├── indicxlit_transliterator.py  # IndicXlit wrapper ⭐
│   ├── simple_translator.py         # Dictionary fallback
│   ├── setu_translator.py           # Legacy wrapper
│   └── transliterator.py            # Rule-based fallback
├── config.py                        # Configuration
├── requirements.txt                 # Dependencies
└── .env.example                     # Environment template
```

---

## 🧪 Testing

### Test Translation

```bash
cd backend
python -c "
from translation import AI4BharatTranslator

t = AI4BharatTranslator()
result = t.translate('جمع بندی موضع اتما پور', src_lang='ur')
print('Input:', result['original_text'])
print('Output:', result['translated_text'])
print('Confidence:', result['confidence'])
"
```

### Test with PDF

```bash
cd backend
python test_pipeline.py Documents/Original/Atmapur.pdf
```

---

## 🔗 References

### AI4Bharat Resources

| Resource | Link |
|----------|------|
| IndicTrans2 | https://github.com/AI4Bharat/IndicTrans2 |
| IndicXlit | https://github.com/AI4Bharat/IndicXlit |
| IndicLLMSuite | https://github.com/AI4Bharat/IndicLLMSuite |
| HuggingFace Models | https://huggingface.co/ai4bharat |
| Paper (IndicTrans2) | https://arxiv.org/abs/2305.16307 |
| Paper (IndicXlit) | https://arxiv.org/abs/2205.03018 |

### Citation

```bibtex
@article{gala2023indictrans,
    title={IndicTrans2: Towards High-Quality and Accessible Machine 
           Translation Models for all 22 Scheduled Indian Languages},
    author={Jay Gala and Pranjal A Chitale and A K Raghavan and ...},
    journal={Transactions on Machine Learning Research},
    year={2023}
}

@article{Madhani2022AksharantarTB,
    title={Aksharantar: Towards building open transliteration tools 
           for the next billion users},
    author={Yash Madhani and Sushane Parthan and ...},
    journal={ArXiv},
    year={2022}
}
```

---

## 📝 Comparison: Before vs After

| Aspect | Before (Bhashini API) | After (AI4Bharat Self-Hosted) |
|--------|----------------------|------------------------------|
| **Dependencies** | External API | Local models |
| **Internet Required** | Yes | No (after model download) |
| **API Keys** | Required | Not needed |
| **Rate Limits** | Yes | No |
| **Privacy** | Data sent to cloud | All processing local |
| **Cost** | Free tier limits | Completely free |
| **Latency** | Network dependent | ~100ms/sentence (GPU) |
| **Accuracy** | Good | Excellent (same models) |

---

## 🛠️ Troubleshooting

### Model Download Issues

```bash
# Clear cache and re-download
rm -rf models/ai4bharat
rm -rf ~/.cache/huggingface

# Then run translation again
```

### CUDA Out of Memory

```bash
# Force CPU mode
export AI4BHARAT_DEVICE=cpu
```

### Import Errors

```bash
# Ensure all dependencies are installed
pip install torch transformers
pip install git+https://github.com/VarunGumma/IndicTransToolkit.git
```

---

## 📄 License

- **This Project**: MIT License
- **IndicTrans2**: MIT License  
- **IndicXlit**: MIT License
- **IndicTransToolkit**: MIT License

---

**Built with ❤️ using AI4Bharat's open-source models for Indian languages**
