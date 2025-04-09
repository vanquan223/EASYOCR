# Đây là phầm mêm ocr nhỏ dựa theo Tesseract-OCR

### Build
```bash
pyinstaller main.spec
```
#### or
```bash
pyinstaller --add-data "C:\Program Files\Tesseract-OCR;Tesseract-OCR" --onefile --icon=icons.png --name=EASYOCR --noconsole main.py
```
