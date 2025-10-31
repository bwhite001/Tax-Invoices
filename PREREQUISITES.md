# Prerequisites & Requirements

Complete guide to system requirements and dependencies for the Australian Tax Invoice Processing System.

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Software Prerequisites](#software-prerequisites)
- [Python Packages](#python-packages)
- [Optional Dependencies](#optional-dependencies)
- [Google Account Setup](#google-account-setup)
- [Verification Steps](#verification-steps)

---

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Operating System** | Windows 10/11, macOS 10.15+, or Linux | Windows recommended for full feature support |
| **Python** | 3.8 or higher | Python 3.11+ recommended |
| **RAM** | 16GB minimum | For LM Studio AI processing |
| **Storage** | 10GB free space | For models and processed files |
| **Internet** | Broadband connection | For initial setup and Google Scripts |

### Recommended Specifications

- **CPU**: Multi-core processor (4+ cores)
- **RAM**: 32GB for optimal AI performance
- **Storage**: SSD for faster processing
- **GPU**: Optional, but improves OCR performance

---

## 🛠️ Software Prerequisites

### Required Software

#### 1. Python 3.8+

**Installation:**

**Windows:**
```bash
# Download from python.org
# Or use winget:
winget install Python.Python.3.11
```

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip
```

**Verification:**
```bash
python --version  # Should show 3.8 or higher
pip --version
```

#### 2. LM Studio (for AI Processing)

**Purpose**: Local AI model inference for invoice data extraction

**Installation:**
1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Install the application
3. Download a model (recommended: Mistral 7B Instruct)
4. Start the Developer Server

**Configuration:**
- Default endpoint: `http://localhost:1234`
- Enable CORS in settings
- Keep running during invoice processing

**Verification:**
```bash
# Test endpoint (should return model info)
curl http://localhost:1234/v1/models
```

#### 3. Google Account (for Automation Modules)

**Required for:**
- Gmail invoice extraction (`google_scripts/`)
- Work-from-home tracking (`wfh/`)

**Setup:**
- Active Gmail account
- Google Drive access
- Google Sheets access
- Google Apps Script permissions

---

## 📦 Python Packages

### Core Dependencies (All Modules)

```bash
# Install all dependencies at once
pip install -r requirements.txt
```

### Module-Specific Packages

#### invoice_cataloger Module

**Required:**
```bash
pip install pandas openpyxl requests python-dotenv
pip install PyMuPDF pdfplumber pypdf
pip install python-docx openpyxl
pip install extract-msg
```

**Optional (Enhanced OCR):**
```bash
pip install easyocr        # Deep learning OCR (no Tesseract needed)
pip install pytesseract    # Traditional OCR (requires Tesseract)
pip install pdf2image      # PDF to image conversion
```

**Requirements file:** `invoice_cataloger/requirements.txt`

#### tax_report_generator Module

**Required:**
```bash
pip install pandas openpyxl
```

**Requirements file:** `tax_report_generator/requirements.txt`

#### bankstatements Module

**Required:**
```bash
pip install pandas openpyxl pdfplumber PyPDF2
```

**Optional (Legacy support):**
```bash
pip install tabula-py      # Requires Java
```

**Requirements file:** `bankstatements/requirements.txt`

### Complete Installation Command

```bash
# From project root directory
cd "g:/My Drive/Tax Invoices"

# Install invoice_cataloger dependencies
pip install -r invoice_cataloger/requirements.txt

# Install tax_report_generator dependencies
pip install -r tax_report_generator/requirements.txt

# Install bankstatements dependencies
pip install -r bankstatements/requirements.txt
```

---

## 🔧 Optional Dependencies

### 1. Tesseract OCR (Traditional OCR)

**Purpose**: OCR for scanned documents and images

**Installation:**

**Windows:**
1. Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to `C:\Program Files\Tesseract-OCR\`
3. Add to PATH or configure in scripts

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

**Verification:**
```bash
tesseract --version
```

**Configuration:**
```python
# In invoice_cataloger/config.py
tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"  # Windows
# tesseract_path = "/usr/bin/tesseract"  # Linux/macOS
```

### 2. Poppler (PDF to Image Conversion)

**Purpose**: Convert PDF pages to images for OCR

**Installation:**

**Windows:**
1. Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
2. Extract to `C:\Program Files\poppler\`
3. Add `bin` folder to PATH

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt install poppler-utils
```

**Verification:**
```bash
pdftoppm -v
```

### 3. Java (Legacy Bank Processing)

**Purpose**: Required for `tabula-py` (legacy bank statement extractor)

**Note**: Not needed for current Zip Money workflow

**Installation:**

**Windows:**
```bash
winget install Oracle.JDK.17
```

**macOS:**
```bash
brew install openjdk@17
```

**Linux:**
```bash
sudo apt install openjdk-17-jdk
```

**Verification:**
```bash
java -version
```

### 4. EasyOCR (Deep Learning OCR)

**Purpose**: Advanced OCR without Tesseract dependency

**Installation:**
```bash
pip install easyocr
```

**Note**: First run downloads models (~100MB)

**Verification:**
```python
import easyocr
reader = easyocr.Reader(['en'])
print("EasyOCR ready!")
```

---

## 🌐 Google Account Setup

### For google_scripts Module (Invoice Email Extraction)

**Requirements:**
1. Active Gmail account
2. Google Drive with storage space
3. Access to Google Apps Script

**Setup Steps:**
1. Go to [script.google.com](https://script.google.com)
2. Create new project
3. Grant permissions:
   - Read/modify Gmail
   - Create/manage Drive files
   - Create/edit Sheets
   - Send emails

**Verification:**
- Can access script.google.com
- Can create new Apps Script project
- Gmail has invoice emails with attachments

### For wfh Module (Location Tracking)

**Requirements:**
1. Google Account
2. Google Sheets access
3. Google Apps Script access

**Setup Steps:**
1. Same as google_scripts setup
2. Note your home/office IP addresses
3. Configure location settings

**Verification:**
- Can create Google Sheets
- Can deploy web apps
- Know your IP addresses

---

## ✅ Verification Steps

### 1. Verify Python Installation

```bash
# Check Python version
python --version
# Expected: Python 3.8.x or higher

# Check pip
pip --version
# Expected: pip 20.x or higher

# Check Python packages
pip list
# Should show installed packages
```

### 2. Verify LM Studio

```bash
# Test LM Studio endpoint
curl http://localhost:1234/v1/models

# Or in Python:
python -c "import requests; print(requests.get('http://localhost:1234/v1/models').json())"
```

**Expected**: JSON response with model information

### 3. Verify OCR Capabilities

```bash
# Test Tesseract (if installed)
tesseract --version

# Test EasyOCR (if installed)
python -c "import easyocr; print('EasyOCR available')"

# Test pdf2image (if installed)
python -c "from pdf2image import convert_from_path; print('pdf2image available')"
```

### 4. Verify Module Dependencies

**invoice_cataloger:**
```bash
cd invoice_cataloger
python -c "import pandas, openpyxl, PyMuPDF, pdfplumber; print('All core dependencies available')"
```

**tax_report_generator:**
```bash
cd tax_report_generator
python -c "import pandas, openpyxl; print('All dependencies available')"
```

**bankstatements:**
```bash
cd bankstatements
python -c "import pandas, openpyxl, pdfplumber, PyPDF2; print('All dependencies available')"
```

### 5. Verify Google Access

1. Open [script.google.com](https://script.google.com)
2. Create a test project
3. Run a simple function
4. Check for permission prompts

### 6. Verify File Structure

```bash
# Check project structure
ls -la "g:/My Drive/Tax Invoices"

# Should see:
# - invoice_cataloger/
# - tax_report_generator/
# - bankstatements/
# - google_scripts/
# - wfh/
# - FY2024-2025/ (or current FY)
```

---

## 🐛 Common Issues & Solutions

### Python Issues

**Issue**: "Python not found"
```bash
# Windows: Add Python to PATH
# Or use full path:
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe
```

**Issue**: "pip not found"
```bash
# Reinstall pip
python -m ensurepip --upgrade
```

**Issue**: "Permission denied"
```bash
# Use --user flag
pip install --user package_name
```

### LM Studio Issues

**Issue**: "Cannot connect to LM Studio"
- Ensure LM Studio is running
- Check Developer Server is started
- Verify endpoint URL (default: localhost:1234)
- Enable CORS in settings

**Issue**: "Model not loaded"
- Load a model in LM Studio
- Wait for model to fully load
- Check available RAM

### OCR Issues

**Issue**: "Tesseract not found"
```bash
# Windows: Add to PATH or specify full path
# In config.py:
tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"
```

**Issue**: "EasyOCR model download fails"
- Check internet connection
- Ensure sufficient disk space (~100MB)
- Try manual download from GitHub

### Google Scripts Issues

**Issue**: "Authorization required"
- Run script manually first
- Follow authorization prompts
- Grant all requested permissions

**Issue**: "Quota exceeded"
- Google Apps Script has daily quotas
- Wait 24 hours or use different account
- Reduce batch sizes

---

## 📊 Dependency Matrix

| Module | Python | LM Studio | Tesseract | Poppler | Java | Google Account |
|--------|--------|-----------|-----------|---------|------|----------------|
| **invoice_cataloger** | ✅ Required | ✅ Required | ⚠️ Optional | ⚠️ Optional | ❌ Not needed | ❌ Not needed |
| **tax_report_generator** | ✅ Required | ❌ Not needed | ❌ Not needed | ❌ Not needed | ❌ Not needed | ❌ Not needed |
| **bankstatements** | ✅ Required | ❌ Not needed | ❌ Not needed | ❌ Not needed | ⚠️ Optional | ❌ Not needed |
| **google_scripts** | ❌ Not needed | ❌ Not needed | ❌ Not needed | ❌ Not needed | ❌ Not needed | ✅ Required |
| **wfh** | ❌ Not needed | ❌ Not needed | ❌ Not needed | ❌ Not needed | ❌ Not needed | ✅ Required |

**Legend:**
- ✅ Required - Must have for module to work
- ⚠️ Optional - Enhances functionality
- ❌ Not needed - Not used by this module

---

## 🎯 Quick Setup Checklist

Use this checklist to verify you have everything needed:

### Essential (All Users)
- [ ] Python 3.8+ installed
- [ ] pip working
- [ ] Project files downloaded/cloned
- [ ] Core Python packages installed

### For Invoice Processing
- [ ] LM Studio installed
- [ ] Model downloaded (Mistral 7B recommended)
- [ ] LM Studio server running
- [ ] invoice_cataloger dependencies installed

### For Enhanced OCR
- [ ] Tesseract installed (optional)
- [ ] EasyOCR installed (optional)
- [ ] Poppler installed (optional)

### For Google Automation
- [ ] Google Account active
- [ ] Google Apps Script access
- [ ] Permissions granted

### For Bank Processing
- [ ] bankstatements dependencies installed
- [ ] Bank statement PDFs available

### For Tax Reporting
- [ ] tax_report_generator dependencies installed
- [ ] WFH log file available
- [ ] Invoice catalog available

---

## 📞 Getting Help

If you encounter issues during setup:

1. **Check this document** for verification steps
2. **Review error messages** carefully
3. **Check module-specific README** files
4. **Verify all prerequisites** are met
5. **Test each component** individually

**Common Resources:**
- Python: [python.org/downloads](https://www.python.org/downloads/)
- LM Studio: [lmstudio.ai/docs](https://lmstudio.ai/docs)
- Tesseract: [github.com/tesseract-ocr](https://github.com/tesseract-ocr/tesseract)
- Google Apps Script: [developers.google.com/apps-script](https://developers.google.com/apps-script)

---

**Next Steps:**
- ✅ Prerequisites verified → Continue to [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- ❌ Issues found → Review troubleshooting sections above
- 🚀 Ready to start → See [QUICKSTART.md](QUICKSTART.md)

---

*Last Updated: December 2024*
*Version: 1.0*
