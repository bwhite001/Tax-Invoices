# Installation Guide

Complete step-by-step installation guide for the Australian Tax Invoice Processing System.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Pre-Installation Checklist](#pre-installation-checklist)
- [Core Installation](#core-installation)
- [Module Installation](#module-installation)
- [Post-Installation Verification](#post-installation-verification)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide walks you through installing all components of the tax invoice processing system. Installation time: **30-45 minutes** for complete setup.

### What You'll Install

1. **Python & Dependencies** - Core runtime and packages
2. **LM Studio** - Local AI model for invoice processing
3. **Optional Tools** - OCR, PDF processing, Java
4. **Google Scripts** - Gmail and WFH automation
5. **Project Files** - All modules and configurations

---

## ✅ Pre-Installation Checklist

Before starting, ensure you have:

- [ ] **Administrator access** to your computer
- [ ] **Internet connection** for downloads
- [ ] **16GB RAM minimum** (32GB recommended)
- [ ] **10GB free disk space**
- [ ] **Google Account** (for automation modules)
- [ ] **1 hour** of uninterrupted time

---

## 🔧 Core Installation

### Step 1: Install Python

#### Windows

**Option A: Official Installer (Recommended)**

1. Download Python 3.11 from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete

**Option B: Windows Package Manager**

```powershell
# Open PowerShell as Administrator
winget install Python.Python.3.11
```

**Verification:**
```powershell
python --version
# Expected: Python 3.11.x

pip --version
# Expected: pip 23.x or higher
```

#### macOS

**Using Homebrew (Recommended):**

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify installation
python3 --version
pip3 --version
```

**Using Official Installer:**

1. Download from [python.org/downloads](https://www.python.org/downloads/)
2. Open the .pkg file
3. Follow installation wizard
4. Verify in Terminal

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3.11 --version
pip3 --version
```

### Step 2: Install LM Studio

LM Studio is required for AI-powered invoice processing.

#### All Platforms

1. **Download LM Studio**
   - Visit [lmstudio.ai](https://lmstudio.ai)
   - Click "Download for [Your OS]"
   - Wait for download (~200MB)

2. **Install LM Studio**
   - **Windows**: Run the .exe installer
   - **macOS**: Open .dmg and drag to Applications
   - **Linux**: Extract and run AppImage

3. **First Launch**
   - Open LM Studio
   - Accept terms and conditions
   - Wait for initial setup

4. **Download AI Model**
   - Click "Discover" tab
   - Search for "Mistral 7B Instruct"
   - Click "Download" on "mistralai/Mistral-7B-Instruct-v0.2"
   - Wait for download (~4GB, takes 10-20 minutes)

5. **Start Developer Server**
   - Click "Developer" tab
   - Toggle "Status" to ON
   - Toggle "Enable CORS" to ON
   - Note the endpoint: `http://localhost:1234`

**Verification:**
```bash
# Test the endpoint
curl http://localhost:1234/v1/models

# Should return JSON with model information
```

### Step 3: Clone/Download Project Files

#### Option A: Using Git (Recommended)

```bash
# Navigate to your desired location
cd "g:/My Drive"

# Clone the repository (if using Git)
git clone [YOUR_REPO_URL] "Tax Invoices"

# Navigate to project
cd "Tax Invoices"
```

#### Option B: Manual Download

1. Download project as ZIP
2. Extract to `g:/My Drive/Tax Invoices`
3. Verify folder structure:
   ```
   Tax Invoices/
   ├── invoice_cataloger/
   ├── tax_report_generator/
   ├── bankstatements/
   ├── google_scripts/
   └── wfh/
   ```

---

## 📦 Module Installation

### Module 1: invoice_cataloger

**Purpose**: AI-powered invoice processing

#### Install Dependencies

```bash
cd "g:/My Drive/Tax Invoices/invoice_cataloger"
pip install -r requirements.txt
```

**This installs:**
- pandas, openpyxl (data processing)
- PyMuPDF, pdfplumber, pypdf (PDF extraction)
- python-docx (Word documents)
- extract-msg (Email files)
- requests (API calls)
- python-dotenv (configuration)

#### Install Optional OCR (Recommended)

**EasyOCR (No additional setup needed):**
```bash
pip install easyocr
```

**Tesseract OCR (Requires separate installation):**

**Windows:**
1. Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer
3. Install to `C:\Program Files\Tesseract-OCR\`
4. Add to PATH or configure in `config.py`

```bash
pip install pytesseract
```

**macOS:**
```bash
brew install tesseract
pip install pytesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
pip install pytesseract
```

#### Install PDF to Image Converter (Optional)

**Poppler (for pdf2image):**

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

**Then install Python package:**
```bash
pip install pdf2image
```

#### Configure Module

1. Open `invoice_cataloger/config.py`
2. Update settings:

```python
# LM Studio endpoint (if not localhost)
lm_studio_endpoint = "http://localhost:1234/v1/chat/completions"

# Financial year
financial_year = "2024-2025"

# Work from home settings
work_from_home_days = 3  # Your WFH days per week
total_work_days = 5
work_use_percentage = 60  # Calculated as 3/5 = 60%

# Tesseract path (Windows only, if installed)
tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"
```

#### Verify Installation

```bash
python invoice_cataloger.py --check-only
```

**Expected output:**
```
✓ Invoice folder exists
✓ Output folder ready
✓ LM Studio connected
✓ Available extraction methods: PyMuPDF, pdfplumber, pypdf, EasyOCR
```

### Module 2: tax_report_generator

**Purpose**: Consolidated tax report generation

#### Install Dependencies

```bash
cd "g:/My Drive/Tax Invoices"
pip install -r tax_report_generator/requirements.txt
```

**This installs:**
- pandas (data processing)
- openpyxl (Excel generation)

#### Configure Module

1. Open `tax_report_generator/config.py`
2. Update if needed:

```python
# Financial year
financial_year = "2024-2025"

# Base directory (usually auto-detected)
base_dir = Path("g:/My Drive/Tax Invoices")
```

#### Verify Installation

```bash
python -c "import pandas, openpyxl; print('tax_report_generator ready')"
```

### Module 3: bankstatements

**Purpose**: Bank statement processing

#### Install Dependencies

```bash
cd "g:/My Drive/Tax Invoices"
pip install -r bankstatements/requirements.txt
```

**This installs:**
- pandas, openpyxl (data processing)
- pdfplumber, PyPDF2 (PDF extraction)

#### Install Optional Java (Legacy Support)

Only needed for legacy `bank_statement_extractor.py` with tabula-py.

**Windows:**
```powershell
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

**Then install tabula-py:**
```bash
pip install tabula-py
```

#### Configure Module

Update paths in scripts if needed:
- `prepare_files.py` - Line ~10: `source_dir`
- `organize_outputs.py` - Line ~10: `fy_dir`

#### Verify Installation

```bash
python -c "import pandas, pdfplumber, PyPDF2; print('bankstatements ready')"
```

### Module 4: google_scripts

**Purpose**: Gmail invoice extraction automation

#### Prerequisites

- Google Account with Gmail
- Google Drive access
- Google Apps Script access

#### Installation Steps

1. **Open Google Apps Script**
   - Go to [script.google.com](https://script.google.com)
   - Sign in with your Google Account

2. **Create New Project**
   - Click "New project"
   - Name it: "Invoice Email Extractor"

3. **Add Script Code**
   - Delete default code
   - Copy contents of `google_scripts/invoice_extract.gs`
   - Paste into editor
   - Save (Ctrl+S / Cmd+S)

4. **Configure Settings**
   - Edit the `CONFIG` object:
   ```javascript
   const CONFIG = {
     searchKeywords: ['invoice', 'receipt', 'tax invoice'],
     parentFolderName: 'Tax Invoices',
     maxEmailsPerRun: 50,
     allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml']
   };
   ```

5. **Grant Permissions**
   - Click Run (▶️)
   - Click "Review permissions"
   - Choose your account
   - Click "Advanced" → "Go to Invoice Email Extractor (unsafe)"
   - Click "Allow"

6. **Test Extraction**
   - Select `testExtraction` function
   - Click Run
   - Check Google Drive for extracted files

7. **Deploy Web App** (Optional)
   - Click Deploy → New deployment
   - Choose Web app
   - Configure and deploy

8. **Set Up Automation** (Optional)
   - Select `createAutomationTrigger`
   - Click Run
   - Script will run daily at 2 AM

#### Verify Installation

- Check Google Drive for "Tax Invoices" folder
- Look for "Extracted Invoices Log" spreadsheet
- Verify test files were extracted

### Module 5: wfh

**Purpose**: Work-from-home location tracking

#### Prerequisites

- Google Account
- Your home and office IP addresses
- Google Apps Script access

#### Installation Steps

1. **Find Your IP Addresses**
   - Home: Visit [whatismyipaddress.com](https://whatismyipaddress.com) from home
   - Office: Visit same site from office
   - Note both IPv4 addresses

2. **Create Apps Script Project**
   - Go to [script.google.com](https://script.google.com)
   - Click "New project"
   - Name it: "IP Location Tracker"

3. **Add Script Files**
   - **File 1**: Copy `wfh/code.gs` content
   - Paste into Code.gs
   - **File 2**: Click + → HTML
   - Name it: `IPLocationTracker`
   - Copy `wfh/IPLocationTracker.html` content
   - Paste and save

4. **Configure IP Addresses**
   - Edit `CONFIG` in code.gs:
   ```javascript
   const CONFIG = {
     locations: {
       home: {
         name: 'Home',
         ipAddresses: ['YOUR_HOME_IP_HERE'],  // Replace!
         ispKeywords: ['SuperLoop', 'Telstra', 'Optus']
       },
       office: {
         name: 'Office',
         ipAddresses: ['YOUR_OFFICE_IP_HERE'],  // Replace!
         ispKeywords: ['CompanyName', 'Office']
       }
     },
     businessHours: {
       startHour: 9,
       endHour: 17,
       daysOfWeek: [1, 2, 3, 4, 5]  // Mon-Fri
     }
   };
   ```

5. **Set Up Spreadsheet**
   - Select `setupSpreadsheet` function
   - Click Run
   - Grant permissions
   - Check for "Location Log" sheet

6. **Deploy Web App**
   - Click Deploy → New deployment
   - Choose Web app
   - Execute as: Me
   - Who has access: Only myself
   - Deploy and copy URL

7. **Test Detection**
   - Open web app URL
   - Click "Check My Location Now"
   - Verify correct location detected

8. **Set Up Automation**
   - Select `createAutomaticTriggers`
   - Click Run
   - Triggers created for 9 AM, 12 PM, 3 PM

#### Verify Installation

- Location Log sheet exists
- Web app detects location correctly
- Triggers are created (check Triggers icon ⏰)

---

## ✅ Post-Installation Verification

### Complete System Check

Run these commands to verify everything is installed:

```bash
# Navigate to project root
cd "g:/My Drive/Tax Invoices"

# Check Python
python --version

# Check invoice_cataloger
cd invoice_cataloger
python invoice_cataloger.py --check-only

# Check tax_report_generator
cd ..
python -c "import sys; sys.path.append('tax_report_generator'); from config import Config; print('Config loaded')"

# Check bankstatements
python -c "import pandas, pdfplumber; print('bankstatements ready')"

# Check LM Studio
curl http://localhost:1234/v1/models
```

### Create Test Folders

```bash
# Create financial year folders
mkdir "FY2024-2025"
mkdir "FY2024-2025/Processed"
mkdir "Statements/FY2024-2025"
mkdir "wfh"
```

### Test Each Module

#### Test invoice_cataloger

```bash
cd invoice_cataloger
python invoice_cataloger.py --check-only
```

Expected: All checks pass ✓

#### Test tax_report_generator

```bash
cd ..
# Create a test WFH log
echo "Date,Location" > wfh/wfh_2024_2025.csv
echo "2024-07-01,Home" >> wfh/wfh_2024_2025.csv

# This will fail gracefully if no invoice catalog exists
python generate_tax_report.py --financial-year 2024-2025
```

#### Test bankstatements

```bash
# Check imports
python -c "from bankstatements import expense_cataloger; print('Module imports OK')"
```

#### Test Google Scripts

1. Open script.google.com
2. Open your projects
3. Run test functions
4. Check for errors

---

## 🐛 Troubleshooting

### Python Installation Issues

**Issue**: "Python not found" or "pip not found"

**Solution**:
```bash
# Windows: Add to PATH
# 1. Search "Environment Variables"
# 2. Edit PATH
# 3. Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311
# 4. Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts

# Or use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe --version
```

**Issue**: "Permission denied" when installing packages

**Solution**:
```bash
# Use --user flag
pip install --user package_name

# Or run as administrator (Windows)
# Right-click PowerShell → Run as Administrator
```

### LM Studio Issues

**Issue**: "Cannot download model"

**Solution**:
- Check internet connection
- Ensure sufficient disk space (5GB+)
- Try different model if download fails
- Check LM Studio logs

**Issue**: "Model won't load"

**Solution**:
- Close other applications to free RAM
- Try smaller model (e.g., 3B instead of 7B)
- Restart LM Studio
- Check system RAM usage

**Issue**: "Server won't start"

**Solution**:
- Check if port 1234 is already in use
- Try different port in settings
- Restart LM Studio
- Check firewall settings

### OCR Installation Issues

**Issue**: "Tesseract not found"

**Solution**:
```bash
# Windows: Specify full path in config.py
tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# Or add to PATH
```

**Issue**: "EasyOCR model download fails"

**Solution**:
- Check internet connection
- Ensure disk space (~100MB)
- Try manual download from GitHub
- Use Tesseract as alternative

### Google Scripts Issues

**Issue**: "Authorization required" loop

**Solution**:
1. Clear browser cache
2. Try incognito mode
3. Use different Google account
4. Check account permissions

**Issue**: "Script timeout"

**Solution**:
- Reduce `maxEmailsPerRun` to 25
- Run multiple times
- Optimize search keywords

**Issue**: "Cannot create trigger"

**Solution**:
- Delete existing triggers first
- Check trigger quota (20 per script)
- Verify permissions granted

### Module-Specific Issues

**Issue**: "Module not found" errors

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python path
python -c "import sys; print(sys.path)"
```

**Issue**: "File not found" errors

**Solution**:
- Verify folder structure
- Check financial year in paths
- Ensure files exist in expected locations
- Review error message for exact path

---

## 📊 Installation Checklist

Use this checklist to track your progress:

### Core Components
- [ ] Python 3.8+ installed and verified
- [ ] pip working correctly
- [ ] LM Studio installed
- [ ] AI model downloaded (Mistral 7B)
- [ ] LM Studio server running
- [ ] Project files downloaded/cloned

### invoice_cataloger Module
- [ ] Dependencies installed
- [ ] EasyOCR or Tesseract installed (optional)
- [ ] pdf2image and Poppler installed (optional)
- [ ] config.py configured
- [ ] Prerequisites check passes
- [ ] Test run successful

### tax_report_generator Module
- [ ] Dependencies installed
- [ ] config.py reviewed
- [ ] Test import successful

### bankstatements Module
- [ ] Dependencies installed
- [ ] Java installed (optional, for legacy)
- [ ] Script paths configured
- [ ] Test import successful

### google_scripts Module
- [ ] Google Apps Script project created
- [ ] Script code added
- [ ] Permissions granted
- [ ] Test extraction successful
- [ ] Automation trigger set (optional)

### wfh Module
- [ ] IP addresses identified
- [ ] Apps Script project created
- [ ] HTML file added
- [ ] IP addresses configured
- [ ] Spreadsheet created
- [ ] Web app deployed
- [ ] Test detection successful
- [ ] Automation triggers set (optional)

### Folder Structure
- [ ] FY folders created
- [ ] Processed folders created
- [ ] Statements folder created
- [ ] wfh folder created

---

## 🎉 Installation Complete!

Congratulations! You've successfully installed the Australian Tax Invoice Processing System.

### Next Steps

1. **Start with Quick Start**
   - See [QUICKSTART.md](QUICKSTART.md) for first-time usage
   - Try processing a few test files

2. **Explore Modules**
   - Read module-specific README files
   - Review configuration options
   - Try example workflows

3. **Customize Settings**
   - Adjust work-from-home percentages
   - Configure expense categories
   - Set up automation schedules

4. **Process Your Data**
   - Start with current financial year
   - Process invoices and statements
   - Generate tax reports

### Getting Help

If you encounter issues:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (if available)
- Review module README files
- Check error logs
- Verify prerequisites

### Resources

- **[QUICKSTART.md](QUICKSTART.md)** - Get started quickly
- **[MODULE_INDEX.md](MODULE_INDEX.md)** - Complete module documentation
- **[PREREQUISITES.md](PREREQUISITES.md)** - Requirements reference

---

**Installation Time**: ~30-45 minutes  
**Difficulty**: Intermediate  
**Support**: See module README files for specific help

---

*Last Updated: December 2024*  
*Version: 1.0*
