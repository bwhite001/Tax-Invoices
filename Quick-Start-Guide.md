# LM Studio Invoice Cataloging - Quick Start Guide

## 60-Second Setup

### 1. Install LM Studio (5 minutes)
```powershell
# Download from https://lmstudio.ai
# Run installer, click Next through defaults
# Takes ~5 minutes total
```

### 2. Download Model (10 minutes)
- Open LM Studio
- Click "Discover"
- Search for "mistral"
- Click "Download" on "Mistral 7B Instruct v0.2"
- Wait for download (shows as "100%" when done)

### 3. Start Server (30 seconds)
- Click "Developer" tab in LM Studio
- Toggle "Status" to ON
- Toggle "Enable CORS" to ON
- Leave LM Studio running

### 4. Create Folder Structure (1 minute)
```powershell
# Create folder for current financial year
New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force

# The script will auto-create the Processed and Logs folders
```

### 5. Copy Script
- The script is already in your Tax Invoices folder
- No configuration needed - it uses dynamic paths based on Financial Year

### 6. Move Invoices
- Copy all PDF, PNG, JPG files to `G:\My Drive\Tax Invoices\FY2024-2025\`
- Organize by category if desired (optional - script searches recursively)

### 7. Run Script
```powershell
# Open PowerShell
cd "G:\My Drive\Tax Invoices"

# Process current year (2024-2025)
.\Invoice-Cataloger-LMStudio.ps1

# Or process a specific year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"
```

## Financial Year Support

The script now supports multiple financial years with a simple parameter:

### Process Current Year (Default)
```powershell
.\Invoice-Cataloger-LMStudio.ps1
```
Processes: `FY2024-2025` folder

### Process Specific Year
```powershell
# Process 2023-2024 financial year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"

# Process 2022-2023 financial year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2022-2023"
```

### Process Multiple Years
```powershell
# Process last 3 years
@("2022-2023", "2023-2024", "2024-2025") | ForEach-Object {
    Write-Host "`nProcessing FY$_..." -ForegroundColor Cyan
    .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear $_
}
```

## Folder Structure

The script automatically organizes files by financial year:

```
G:\My Drive\Tax Invoices\
├── FY2024-2025/                    # Current year
│   ├── [Your invoice files]        # PDF, PNG, JPG, etc.
│   └── Processed/                  # Auto-created by script
│       ├── Logs/                   # Processing logs
│       ├── Invoice_Catalog_*.csv
│       ├── Deduction_Summary_*.csv
│       └── Invoice_Catalog_*.xlsx
├── FY2023-2024/                    # Previous year
│   ├── [Invoice files]
│   └── Processed/
├── FY2022-2023/                    # Older year
│   └── ...
└── Invoice-Cataloger-LMStudio.ps1  # The script
```

## Configuration Quick Reference

The script uses **dynamic configuration** based on the `-FinancialYear` parameter:

```powershell
# No manual configuration needed!
# Just specify the financial year when running:

.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2024-2025"

# The script automatically sets:
# - InvoiceFolder: G:\My Drive\Tax Invoices\FY2024-2025
# - OutputFolder: G:\My Drive\Tax Invoices\FY2024-2025\Processed
# - LogFolder: G:\My Drive\Tax Invoices\FY2024-2025\Processed\Logs
```

### Customize Work Situation (Optional)

If you need to change your work-from-home percentage, edit the script:

```powershell
# Open Invoice-Cataloger-LMStudio.ps1 and find:
$Config = @{
    # Your work situation (CRITICAL FOR ATO COMPLIANCE)
    WorkFromHomeDays = 3        # You work from home 3 days/week
    TotalWorkDays = 5           # Out of 5 working days
    WorkUsePercentage = 60      # Automatically calculated as 3/5 = 60%
}
```

## What to Do After Running

### CSV Files Created
1. **Invoice_Catalog_YYYYMMDD_HHMMSS.csv**
   - Detailed list of all invoices
   - Import into Excel if needed

2. **Deduction_Summary_YYYYMMDD_HHMMSS.csv**
   - Summary by category
   - Shows total deductible per category

### Excel File (If Excel installed)
- **Invoice_Catalog_YYYYMMDD_HHMMSS.xlsx**
- Two sheets: Summary + Invoices
- Formatted and ready for accountant

### Next Steps
1. Review the "ClaimMethod" column
2. Check "RequiredDocumentation" for each expense
3. Keep all original invoices
4. Store the CSV/Excel files securely
5. Provide to accountant with original invoices

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Cannot connect to LM Studio" | Ensure LM Studio is running and model is loaded |
| "Invoice folder not found" | Create folder: `New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force` |
| "Invalid Financial Year format" | Use format YYYY-YYYY (e.g., "2024-2025") |
| "No files found" | Put invoices in FY folder (script searches recursively) |
| "Model not responding" | Restart LM Studio, close other apps to free RAM |
| Script won't run | Run PowerShell (no admin needed for this script) |
| Tesseract errors | Optional - install from https://github.com/UB-Mannheim/tesseract/wiki |

## Model Recommendations

| Model | Speed | Accuracy | Size | RAM Needed |
|-------|-------|----------|------|-----------|
| Mistral 7B | Fast | Excellent | 5GB | 8GB |
| Llama 2 7B | Medium | Good | 4GB | 8GB |
| Neural Chat 7B | Medium | Good | 5GB | 8GB |

**Recommended: Mistral 7B** (best balance for invoices)

## ATO Important Notes

✓ **Deductible (You can claim):**
- Electricity (60% of bill)
- Internet/phone (60% of bill)
- Software subscriptions under $300
- Computer equipment under $300
- Professional development courses
- Professional memberships

✗ **NOT Deductible:**
- Coffee, snacks, meals
- Childcare
- Clothing
- Employer-reimbursed expenses
- Private use portions

## Record Keeping

**CRITICAL:** Keep for 5 years:
- Original invoices/receipts
- This spreadsheet/CSV files
- Time records if claiming Fixed Rate Method
- Bank statements showing payments

## Examples

### Example 1: First Time Setup
```powershell
# 1. Create folder for current year
New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force

# 2. Copy your invoices into the folder

# 3. Run the script
cd "G:\My Drive\Tax Invoices"
.\Invoice-Cataloger-LMStudio.ps1

# Output files created in: FY2024-2025\Processed\
```

### Example 2: Process Previous Year
```powershell
# Process last year's invoices
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"

# Output files created in: FY2023-2024\Processed\
```

### Example 3: Batch Process Multiple Years
```powershell
# Process all years at once
$years = @("2021-2022", "2022-2023", "2023-2024", "2024-2025")

foreach ($year in $years) {
    Write-Host "`n=== Processing FY$year ===" -ForegroundColor Green
    .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear $year
    Write-Host "Completed FY$year`n" -ForegroundColor Green
}
```

### Example 4: Check Environment Only
```powershell
# Verify setup without processing files
.\Invoice-Cataloger-LMStudio.ps1 -CheckOnly

# Or check specific year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024" -CheckOnly
```

## Support

**LM Studio Help:**
- Official docs: https://lmstudio.ai/docs
- Download: https://lmstudio.ai

**ATO Guidelines:**
- Work from Home: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/work-related-deductions/working-from-home-expenses
- Software: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/work-related-deductions/tools-computers-and-items-you-use-for-work/computers-laptops-and-software

**PowerShell Help:**
- Run: `Get-Help about_execution_policies`
- Or: https://learn.microsoft.com/en-us/powershell/

## Next Steps

After running the script:
1. Check the `Processed` folder for output files
2. Review the Excel file (or CSV files)
3. Verify extracted data is accurate
4. Keep original invoices for 5 years
5. Provide files to your accountant

For detailed setup instructions, see [Setup-Guide-LM-Studio.md](Setup-Guide-LM-Studio.md)

