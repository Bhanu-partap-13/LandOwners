# Sample Jamabandi Document (Urdu)

## Document 1: Atmapur Village Land Record

```
جمع بندی
موضع: اتما پور
تحصیل: بشنال
ضلع: جموں
خسرہ نمبر: ۱۲۳
مالک: محمد احمد
رقبہ: ۵ کنال
کشت: گندم
```

**English Translation:**
```
Jamabandi
Village: Atmapur
Tehsil: Bishnah
District: Jammu
Khasra Number: 123
Owner: Muhammad Ahmad
Area: 5 Kanal
Cultivation: Wheat
```

---

## Document 2: Simple Land Record

```
جمع بندی
موضع: رام نگر
خسرہ: ۴۵۶
مالک: علی حسن
رقبہ: ۳ کنال
```

**English Translation:**
```
Jamabandi
Village: Ram Nagar
Khasra: 456
Owner: Ali Hassan
Area: 3 Kanal
```

---

## Document 3: Orchard Record

```
باغ
موضع: شالیمار
تحصیل: سرینگر
مالک: فاطمہ بیگم
رقبہ: ۱۰ کنال
نوع: سیب کا باغ
```

**English Translation:**
```
Orchard
Village: Shalimar
Tehsil: Srinagar
Owner: Fatima Begum
Area: 10 Kanal
Type: Apple Orchard
```

---

## Document 4: Multiple Owners

```
جمع بندی
موضع: بڈگام
خسرہ نمبر: ۷۸۹
مالک ۱: احمد شاہ
مالک ۲: رشید خان
رقبہ: ۸ کنال
```

**English Translation:**
```
Jamabandi
Village: Budgam
Khasra Number: 789
Owner 1: Ahmad Shah
Owner 2: Rashid Khan
Area: 8 Kanal
```

---

## Common Terms Used

| Urdu | Roman | English |
|------|-------|---------|
| جمع بندی | Jamabandi | Land Revenue Record |
| موضع | Mauza | Village |
| تحصیل | Tehsil | Sub-district |
| ضلع | Zila | District |
| خسرہ | Khasra | Survey Number |
| مالک | Malik | Owner |
| رقبہ | Raqba | Area |
| کنال | Kanal | Unit of area measurement |
| کشت | Kisht | Cultivation |
| باغ | Bagh | Orchard |
| گندم | Gandum | Wheat |
| سیب | Seb | Apple |

## How to Use These Samples

### For Testing Translation Feature:

1. **Copy Urdu Text**: Select and copy the Urdu text from above
2. **Create Image**: Use an image editor to create a PNG/JPG with the text
3. **Upload**: Go to Translation page and upload the image
4. **Translate**: Click "Translate Document" or "Translate & Download PDF"

### For API Testing:

Save the Urdu text to a file and use with curl:

```bash
# Create test file
echo "جمع بندی موضع: اتما پور تحصیل: بشنال" > test.txt

# Test text translation
curl -X POST http://localhost:5000/api/translate/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text": "جمع بندی موضع: اتما پور", "source_lang": "ur", "target_lang": "en"}'
```

### Creating Test Images:

#### Option 1: Using MS Paint (Windows)
1. Open Paint
2. Select an appropriate Urdu font (e.g., "Jameel Noori Nastaleeq")
3. Type the Urdu text
4. Save as PNG

#### Option 2: Using Online Tools
1. Go to any text-to-image generator
2. Paste Urdu text
3. Select Urdu font
4. Download as PNG/JPG

#### Option 3: Using Python (Automated)
```python
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

text = "جمع بندی موضع: اتما پور"
reshaped_text = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped_text)

img = Image.new('RGB', (800, 400), color='white')
d = ImageDraw.Draw(img)
font = ImageFont.truetype("arial.ttf", 36)
d.text((50, 50), bidi_text, font=font, fill='black')
img.save('jamabandi.png')
```

## Expected Translation Results

### Document 1 Expected Output:
```
Jamabandi
Village: Atmapur
Tehsil: Bishnah
District: Jammu
Khasra Number: 123
Owner: Muhammad Ahmad
Area: 5 Kanal
Cultivation: Wheat
```

**Confidence**: Should be 95%+ due to exact term matches

### Document 2 Expected Output:
```
Jamabandi
Village: Ram Nagar
Khasra: 456
Owner: Ali Hassan
Area: 3 Kanal
```

**Confidence**: 90%+ (Ram Nagar might need custom mapping)

## Testing Checklist

- [ ] Test with Document 1 (complete Jamabandi)
- [ ] Test with Document 2 (simple record)
- [ ] Test with Document 3 (orchard record)
- [ ] Test with Document 4 (multiple owners)
- [ ] Verify all common terms translate correctly
- [ ] Check PDF generation for each document
- [ ] Verify formatting in PDF output
- [ ] Test with actual scanned documents

## Notes for Developers

1. **Font Rendering**: Urdu text requires proper RTL (right-to-left) fonts
2. **OCR Quality**: Clean, typed text will OCR better than handwritten
3. **Image Quality**: 300 DPI recommended for best OCR results
4. **File Format**: PNG generally works better than JPG for text
5. **Contrast**: Black text on white background is ideal

## Additional Test Cases

### Edge Cases:

1. **Numbers in Urdu**: ۱۲۳۴۵۶۷۸۹۰
2. **Mixed Languages**: Some English words in Urdu text
3. **Special Characters**: Punctuation marks
4. **Long Documents**: Multiple pages of text
5. **Poor Quality**: Low resolution or faded scans

### Performance Testing:

- Small file (< 1MB): Should process in ~10 seconds
- Medium file (1-5MB): Should process in ~15 seconds
- Large file (5-16MB): Should process in ~20-30 seconds

## Real-World Document Examples

The translation system is optimized for documents from:

- **Jammu District**: اتما پور (Atmapur), بشنال (Bishnah)
- **Kashmir Valley**: سرینگر (Srinagar), بڈگام (Budgam)
- **Common Crops**: گندم (Wheat), چاول (Rice), مکئی (Maize)
- **Land Types**: زرعی زمین (Agricultural Land), باغ (Orchard)

---

**For questions or to add more sample documents, please contribute to this file.**
