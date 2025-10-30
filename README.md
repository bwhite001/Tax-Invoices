# Invoice Cataloger with LM Studio

> **Automated ATO-Compliant Invoice Processing for Australian Tax Returns**

A PowerShell-based invoice cataloging system that uses LM Studio (local AI) to automatically extract data from invoices, categorize expenses, and calculate ATO-compliant tax deductions for work-from-home expenses.

## 🎯 Features

- **AI-Powered Extraction**: Uses local LLM (Mistral 7B) via LM Studio to extract invoice data
- **Multi-Format Support**: Processes PDF, images (PNG/JPG), Word docs, Excel files, and emails
- **OCR Integration**: Built-in Windows OCR + optional Tesseract for scanned documents
- **ATO Compliance**: Automatic deduction calculations following 2024-25 ATO guidelines
- **Multi-Year Support**: Process invoices for different financial years with ease
- **Smart Categorization**: Automatically categorizes expenses (Electricity, Internet, Software, etc.)
- **Excel Export**: Professional reports with summary and detailed breakdowns
- **Privacy First**: All processing happens locally - no cloud services required

## 📁 Project Structure

```
Tax Invoices/
├── FY2024-2025/              # Financial Year folder
│   ├── [Invoice files]       # Your PDF, PNG, JPG, etc. files
│   └── Processed/            # Auto-created output folder
│       ├── Logs/             # Processing logs
│       ├── Invoice_Catalog_*.csv
│       ├── Deduction_Summary_*.csv
│       └── Invoice_Catalog_*.xlsx
├── FY2023-2024/              # Previous year
├── FY2025-2026/              # Future year
└── Invoice-Cataloger-LMStudio.ps1
```

## 🚀 Quick Start

### 1. Prerequisites

- **Windows 10/11** with PowerShell 5.1+
- **LM Studio** installed and running ([Download](https://lmstudio.ai))
- **16GB RAM** minimum (for AI model)
- **Mistral 7B** or compatible model loaded in LM Studio

### 2. Setup LM Studio

```powershell
# 1. Download and install LM Studio from https://lmstudio.ai
# 2. Open LM Studio → Discover → Search "Mistral 7B"
# 3. Download the model
# 4. Go to Developer tab → Toggle "Status" ON
# 5. Enable CORS in settings
```

### 3. Organize Your Invoices

```powershell
# Create folder for current financial year
New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force

# Copy your invoice files into this folder
# Supported: PDF, PNG, JPG, JPEG, GIF, DOC, DOCX, XLS, XLSX, EML
```

### 4. Run the Script

```powershell
# Process current financial year (2024-2025)
.\Invoice-Cataloger-LMStudio.ps1

# Process a specific financial year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"

# Check environment only (no processing)
.\Invoice-Cataloger-LMStudio.ps1 -CheckOnly
```

## 💡 Usage Examples

### Process Current Year
```powershell
.\Invoice-Cataloger-LMStudio.ps1
```
This processes invoices in `FY2024-2025` folder by default.

### Process Previous Year
```powershell
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"
```

### Process Multiple Years
```powershell
# Process last 3 financial years
@("2022-2023", "2023-2024", "2024-2025") | ForEach-Object {
    Write-Host "Processing FY$_..." -ForegroundColor Cyan
    .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear $_
}
```

### Environment Check
```powershell
# Verify setup without processing files
.\Invoice-Cataloger-LMStudio.ps1 -CheckOnly
```

## 📊 Output Files

The script generates three files in the `Processed` folder:

### 1. Invoice_Catalog_[timestamp].csv
Detailed list of all processed invoices with:
- Vendor information (name, ABN)
- Invoice details (number, date, amounts)
- Expense category
- Deductible amount
- Claim method and notes
- Required documentation

### 2. Deduction_Summary_[timestamp].csv
Summary by expense category:
- Total invoices per category
- Total invoiced amount
- Total deductible amount
- Average deduction

### 3. Invoice_Catalog_[timestamp].xlsx (if Excel installed)
Professional Excel workbook with:
- **Summary Sheet**: Category breakdown with totals
- **Invoices Sheet**: Detailed invoice list
- Formatted and ready for your accountant

## 🏷️ Expense Categories

The system automatically categorizes expenses:

| Category | Examples | Deduction Method |
|----------|----------|------------------|
| **Electricity** | Power bills | 60% work use (Actual Cost) |
| **Internet** | NBN, broadband | 60% work use (Actual Cost) |
| **Phone** | Mobile plans | 60% work use (Actual Cost) |
| **Software & Subscriptions** | GitHub, Azure, IDEs | Immediate (<$300) or Depreciation (>$300) |
| **Computer Equipment** | Laptops, monitors | Immediate (<$300) or Depreciation (>$300) |
| **Professional Development** | Courses, training | 100% deductible |
| **Professional Membership** | IEEE, ACM | 100% deductible |
| **Office Supplies** | Stationery, desk items | 60% work use |
| **Mobile/Communication** | VoIP, Zoom, Teams | 60% work use |

## ⚙️ Configuration

Edit the script to customize settings:

```powershell
# Work from home configuration
WorkFromHomeDays = 3        # Days per week working from home
TotalWorkDays = 5           # Total working days per week
WorkUsePercentage = 60      # Calculated as 3/5 = 60%

# LM Studio endpoint (if running on different machine/port)
LMStudioEndpoint = "http://192.168.0.100:1234/v1/chat/completions"

# OCR settings
UseWindowsOCR = $true       # Use built-in Windows 10+ OCR
TesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 📋 ATO Compliance Notes

### Work Use Percentage
- Based on days working from home: 3/5 days = 60%
- Applied to: Electricity, Internet, Phone, Office Supplies
- **NOT** applied to: Professional Development, Memberships (100% deductible)

### Depreciation Rules
- **Under $300**: Immediate deduction (same year)
- **Over $300**: Decline in value over effective life (2-4 years for computers)
- Use [ATO Depreciation Tool](https://www.ato.gov.au/calculators-and-tools/depreciation-and-capital-allowances-tool/)

### Record Keeping
Keep for **5 years**:
- ✅ Original invoices/receipts
- ✅ Generated CSV/Excel files
- ✅ Bank statements showing payments
- ✅ Time records (if using Fixed Rate Method)

### Alternative: Fixed Rate Method
Instead of Actual Cost Method, you can use:
- **$0.70 per hour** worked from home (2024-25 rate)
- Covers: Electricity, Internet, Phone, Stationery
- Requires: Detailed time records
- **Cannot** claim these expenses separately if using this method

## 🔧 Troubleshooting

### "Cannot connect to LM Studio"
```powershell
# Check LM Studio is running
# Verify model is loaded (Developer tab)
# Test endpoint: http://localhost:1234/v1/models in browser
# Ensure CORS is enabled in LM Studio settings
```

### "Invoice folder not found"
```powershell
# Create the folder for your financial year
New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force

# Verify the path matches your Google Drive location
```

### "No files found to process"
```powershell
# Check files are in the correct folder (not subfolders)
# Verify file extensions are supported
# Ensure files aren't locked/in use
```

### "Model not responding"
```powershell
# Restart LM Studio
# Close other applications to free RAM
# Try a smaller model if memory constrained
# Increase timeout in script configuration
```

## 📚 Documentation

- **[Quick Start Guide](Quick-Start-Guide.md)** - 60-second setup
- **[Setup Guide](Setup-Guide-LM-Studio.md)** - Detailed installation instructions
- **[ATO Guidelines](https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/work-related-deductions/working-from-home-expenses)** - Official work-from-home expense rules

## 🔒 Privacy & Security

- **100% Local Processing**: All AI processing happens on your computer
- **No Cloud Services**: No data sent to external servers
- **No Internet Required**: Works offline (except for LM Studio model download)
- **Your Data Stays Yours**: Invoices never leave your machine

## 🛠️ Technical Details

- **Language**: PowerShell 5.1+
- **AI Engine**: LM Studio (local LLM inference)
- **Recommended Model**: Mistral 7B Instruct v0.2
- **OCR**: Windows 10+ built-in OCR + optional Tesseract
- **Export**: CSV + Excel (via COM automation)

## 📝 License

This project is provided as-is for personal use. Always consult with a qualified tax professional for tax advice.

## ⚠️ Disclaimer

This tool assists with organizing and categorizing invoices. It does not provide tax advice. Always:
- Verify all extracted data for accuracy
- Consult with a registered tax agent or accountant
- Follow current ATO guidelines for your specific situation
- Keep all original documentation

## 🤝 Contributing

Suggestions and improvements welcome! This is a personal project designed for Australian software developers working from home.

## 📞 Support

- **LM Studio**: https://lmstudio.ai/docs
- **ATO Work from Home**: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/work-related-deductions/working-from-home-expenses
- **PowerShell Help**: https://learn.microsoft.com/en-us/powershell/

---

**Made for Australian Software Developers** 🇦🇺 | **ATO 2024-25 Compliant** ✅ | **Privacy First** 🔒
