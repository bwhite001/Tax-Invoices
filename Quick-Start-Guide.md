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

### 4. Create Folder (1 minute)
```powershell
mkdir "C:\Invoices\2024-25"
mkdir "C:\Invoices\Processed"
mkdir "C:\Scripts"
```

### 5. Copy Script and Config
- Download: `Invoice-Cataloger-LMStudio.ps1`
- Save to: `C:\Scripts\`
- Update file paths in `$Config` section (see below)

### 6. Move Invoices
- Copy all PDF, PNG, JPG files to `C:\Invoices\2024-25\`

### 7. Run Script
```powershell
# Open PowerShell as Administrator
cd C:\Scripts
.\Invoice-Cataloger-LMStudio.ps1
```

## Configuration Quick Reference

Open `Invoice-Cataloger-LMStudio.ps1` and update the `$Config` section:

```powershell
$Config = @{
    # These folders must exist
    InvoiceFolder = "C:\Invoices\2024-25"     # Put invoice files here
    OutputFolder = "C:\Invoices\Processed"    # Where CSV/Excel created
    
    # Leave these at defaults (unless you know what you're doing)
    LMStudioEndpoint = "http://localhost:1234/v1/chat/completions"
    
    # Your work situation (CRITICAL FOR ATO COMPLIANCE)
    WorkFromHomeDays = 3        # You work from home 3 days/week
    TotalWorkDays = 5           # Out of 5 working days
    WorkUsePercentage = 60      # Automatically calculated as 3/5 = 60%
    FinancialYear = "2024-25"
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
| "No files found" | Put invoices in C:\Invoices\2024-25\ (not subfolder) |
| "Model not responding" | Restart LM Studio, close other apps to free RAM |
| Script won't run | Run PowerShell as Administrator |
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

