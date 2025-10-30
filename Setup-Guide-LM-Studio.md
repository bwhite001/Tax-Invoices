# LM Studio Invoice Cataloging - Complete Setup Guide

## Prerequisites

- Windows 10 (build 19041+) or Windows 11
- 16GB RAM minimum (8GB for smaller models)
- 50GB free disk space (for LM Studio + model)
- GPU with 8GB VRAM recommended (NVIDIA/AMD)

## Step 1: Install LM Studio

1. **Download LM Studio**
   - Visit https://lmstudio.ai
   - Click "Download for Windows"
   - Run the installer: `LM-Studio-Setup-*.exe`

2. **Complete Installation**
   - Accept default installation path: `C:\Users\{YourUsername}\AppData\Local\Programs\LM Studio`
   - Allow shortcuts to be created
   - Click "Finish"

3. **Verify Installation**
   - Open PowerShell or Command Prompt
   - Run: `lm-studio --version`
   - Should display version information

## Step 2: Download and Configure a Model

### Recommended Models (in order of preference):

1. **Mistral 7B Instruct** (Recommended for invoices)
   - Best balance of speed and accuracy
   - ~5GB file size
   - Excellent at following structured extraction instructions

2. **Llama 2 7B** (Alternative)
   - Reliable document understanding
   - ~4GB file size
   - Good for diverse document types

3. **Neural Chat 7B** (Lightweight)
   - Smallest model (~5GB)
   - Faster processing
   - Acceptable accuracy for invoices

### Download Process:

1. **Open LM Studio**
   - Double-click LM Studio desktop shortcut or search in Start Menu

2. **Navigate to Discover**
   - Click "Discover" in left sidebar
   - Search for "mistral" in search box

3. **Download Model**
   - Click "Mistral 7B Instruct v0.2"
   - Click "Download" button
   - Wait for download to complete (5-15 minutes depending on internet)

4. **Load Model**
   - Model will automatically appear in "Local Models" after download
   - This is now ready to use

## Step 3: Start LM Studio Server

1. **Open Developer Tab**
   - In LM Studio, click "Developer" in left sidebar
   - You should see "Status" with a toggle (currently OFF)

2. **Enable Server**
   - Click the Status toggle to turn ON
   - Status should show "Running" in green
   - Note the endpoint: `http://localhost:1234/v1`

3. **Enable CORS (Important)**
   - In Developer tab, scroll to "Settings"
   - Toggle "Enable CORS" to ON
   - This allows PowerShell scripts to communicate with LM Studio

4. **Verify Server Running**
   - Open browser and go to: `http://localhost:1234/v1/models`
   - You should see JSON output listing your loaded model
   - Keep LM Studio running in background

## Step 4: Install OCR Support (for Scanned Invoices)

### Option A: Windows 10 Built-in OCR (Simplest)

Windows 10 has native OCR - PowerShell can access it directly without additional installation.

### Option B: Tesseract OCR (More Powerful)

If scanning many scanned documents:

1. **Download Tesseract**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download installer: `tesseract-ocr-w64-setup-v5.x.exe`

2. **Install Tesseract**
   - Run the installer
   - Accept license agreement
   - Choose default installation path: `C:\Program Files\Tesseract-OCR`
   - Ensure "English" is selected in language data
   - Complete installation

3. **Add to Windows PATH** (Important)
   - Press `Win + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables..." button
   - Under "System variables", click "Path"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click OK multiple times

4. **Verify Installation**
   - Open new PowerShell window
   - Run: `tesseract -v`
   - Should display version information

## Step 5: Prepare Invoice Storage

The script uses a **Financial Year-based folder structure** that automatically organizes invoices by year.

1. **Create Invoice Folder Structure**
   ```
   G:\My Drive\Tax Invoices\
   ├── FY2024-2025\              # Current financial year
   │   ├── [Invoice files]       # Your PDF, PNG, JPG, etc.
   │   └── Processed\            # Auto-created by script
   │       ├── Logs\             # Processing logs
   │       └── [Output files]    # CSV and Excel files
   ├── FY2023-2024\              # Previous year
   │   ├── [Invoice files]
   │   └── Processed\
   ├── FY2022-2023\              # Older year
   └── Invoice-Cataloger-LMStudio.ps1
   ```

2. **Create Folder for Current Year**
   ```powershell
   # Create folder for FY 2024-2025
   New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force
   
   # The script will automatically create:
   # - FY2024-2025\Processed\
   # - FY2024-2025\Processed\Logs\
   ```

3. **Move Invoice Files**
   - Place all PDF, PNG, JPG, DOC, DOCX, XLS, XLSX, EML files in the FY folder
   - Example: `G:\My Drive\Tax Invoices\FY2024-2025\`
   - Organize by category if desired (optional - script searches recursively)

## Step 6: Understanding the Financial Year Parameter

The script now uses a **dynamic configuration** based on the Financial Year parameter:

### No Manual Configuration Needed!

```powershell
# The script automatically constructs paths based on the -FinancialYear parameter
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2024-2025"

# This automatically sets:
# - InvoiceFolder: G:\My Drive\Tax Invoices\FY2024-2025
# - OutputFolder: G:\My Drive\Tax Invoices\FY2024-2025\Processed
# - LogFolder: G:\My Drive\Tax Invoices\FY2024-2025\Processed\Logs
```

### Financial Year Format

- **Format**: `YYYY-YYYY` (e.g., "2024-2025", "2023-2024")
- **Must be consecutive years**: 2024-2025 ✅, 2024-2026 ❌
- **Default**: "2024-2025" (current financial year)

### Optional: Customize Work Situation

If you need to change your work-from-home percentage, edit the script:

```powershell
# Open Invoice-Cataloger-LMStudio.ps1 and find the $Config section:
$Config = @{
    # Your work situation (CRITICAL FOR ATO COMPLIANCE)
    WorkFromHomeDays = 3        # You work from home 3 days/week
    TotalWorkDays = 5           # Out of 5 working days
    WorkUsePercentage = 60      # Automatically calculated as 3/5 = 60%
    
    # LM Studio endpoint (if running on different machine)
    LMStudioEndpoint = "http://192.168.0.100:1234/v1/chat/completions"
}
```

### Enable PowerShell Execution (If needed)

If you get execution policy error:
```powershell
# Run PowerShell and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 7: Run the Script

### Basic Usage

1. **Open PowerShell**
   - Press `Win + X`, select "Windows PowerShell"
   - No administrator rights needed

2. **Navigate to Script Location**
   ```powershell
   cd "G:\My Drive\Tax Invoices"
   ```

3. **Execute Script**
   ```powershell
   # Process current year (2024-2025)
   .\Invoice-Cataloger-LMStudio.ps1
   
   # Or specify a different year
   .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"
   ```

### Advanced Usage

**Process Multiple Years:**
```powershell
# Process last 3 financial years
@("2022-2023", "2023-2024", "2024-2025") | ForEach-Object {
    Write-Host "`n=== Processing FY$_ ===" -ForegroundColor Green
    .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear $_
}
```

**Check Environment Only:**
```powershell
# Verify setup without processing files
.\Invoice-Cataloger-LMStudio.ps1 -CheckOnly

# Check specific year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024" -CheckOnly
```

**Combine Parameters:**
```powershell
# Check environment for specific year
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2022-2023" -CheckOnly
```

### Monitor Processing

- Script displays progress in PowerShell window
- Shows each file being processed
- Creates CSV/Excel files when complete
- Automatically opens Excel file (if installed)
- Check `Processed\Logs\` folder for detailed logs

## Troubleshooting

### "Cannot connect to LM Studio"
- ✓ Ensure LM Studio is running (Developer tab shows "Running")
- ✓ Verify model is loaded (check Local Models list)
- ✓ Check endpoint: `http://localhost:1234/v1/models` in browser
- ✓ Restart LM Studio and try again

### "Model not responding"
- ✓ Check LM Studio doesn't show any errors
- ✓ Verify GPU/CPU has sufficient memory
- ✓ Wait longer for slow responses (can take 30+ seconds)
- ✓ Try a smaller model (Mistral 7B instead of larger)

### "Invoice folder not found"
- ✓ Create the folder: `New-Item -ItemType Directory -Path "G:\My Drive\Tax Invoices\FY2024-2025" -Force`
- ✓ Verify the Financial Year parameter matches your folder name
- ✓ Check the base path is correct: `G:\My Drive\Tax Invoices`

### "Invalid Financial Year format"
- ✓ Use format YYYY-YYYY (e.g., "2024-2025")
- ✓ Years must be consecutive (2024-2025 ✅, 2024-2026 ❌)
- ✓ Use quotes around the parameter: `-FinancialYear "2024-2025"`

### "No files found to process"
- ✓ Verify files are in the FY folder (e.g., `FY2024-2025\`)
- ✓ Check file extensions are supported: PDF, PNG, JPG, JPEG, GIF, DOC, DOCX, XLS, XLSX, EML
- ✓ Script searches recursively, so subfolders are OK

### "Tesseract OCR command not found"
- ✓ Verify installation in `C:\Program Files\Tesseract-OCR\`
- ✓ Check PATH environment variable includes Tesseract folder
- ✓ Restart PowerShell after modifying PATH
- ✓ Test with: `tesseract -v`

### "JSON parsing error from LM Studio"
- ✓ Ensure LM Studio CORS is enabled (Settings > Enable CORS)
- ✓ Verify model is properly loaded
- ✓ Try simpler test prompt in LM Studio directly first
- ✓ Check model has sufficient VRAM available

## Performance Tips

1. **Faster Processing**
   - Use Mistral 7B (fastest quality model)
   - Close unnecessary applications to free RAM
   - Use GPU if available (check LM Studio Model Info)

2. **Better Accuracy**
   - Use Llama 2 for complex invoices
   - Ensure good OCR quality for scanned documents
   - Pre-organize invoices by category

3. **Resource Management**
   - Monitor LM Studio memory usage
   - Restart LM Studio if processing slows down
   - Process invoices in batches if many files

## Working with Multiple Financial Years

### Scenario 1: Processing Current Year Only
```powershell
# Just run the script with default settings
.\Invoice-Cataloger-LMStudio.ps1

# Output: FY2024-2025\Processed\Invoice_Catalog_*.xlsx
```

### Scenario 2: Processing Previous Years
```powershell
# Process 2023-2024
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2023-2024"

# Process 2022-2023
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2022-2023"

# Each creates output in its own Processed folder
```

### Scenario 3: Batch Processing All Years
```powershell
# Create a processing script
$years = @("2021-2022", "2022-2023", "2023-2024", "2024-2025")

foreach ($year in $years) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Processing Financial Year: $year" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear $year
    
    Write-Host "`nCompleted FY$year" -ForegroundColor Green
    Write-Host "Output: FY$year\Processed\`n" -ForegroundColor Green
}

Write-Host "All years processed successfully!" -ForegroundColor Green
```

### Scenario 4: Verify Before Processing
```powershell
# Check each year's setup before processing
$years = @("2022-2023", "2023-2024", "2024-2025")

foreach ($year in $years) {
    Write-Host "`nChecking FY$year..." -ForegroundColor Yellow
    .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear $year -CheckOnly
}
```

## Next Steps

1. **After running script**, check the generated files in the `Processed` folder:
   - `Invoice_Catalog_[timestamp].csv` - Detailed invoice list
   - `Deduction_Summary_[timestamp].csv` - Category summaries
   - `Invoice_Catalog_[timestamp].xlsx` - Excel workbook (if Excel installed)

2. **Review ATO compliance** for each expense:
   - Check "ClaimMethod" column
   - Note any items requiring further documentation
   - Flag questionable items for accountant review

3. **Organize your records**:
   - Keep original invoice files in their FY folders
   - Each year has its own `Processed` folder with outputs
   - Backup to cloud storage (OneDrive, Google Drive)
   - Maintain records for 5 years per ATO requirements

4. **Year-end workflow**:
   ```powershell
   # At end of financial year, process all invoices
   .\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2024-2025"
   
   # Review the Excel file
   # Provide to accountant with original invoices
   # Archive for 5 years
   ```

## Support Resources

- **LM Studio Documentation**: https://lmstudio.ai/docs
- **Model Information**: https://huggingface.co/models
- **ATO Guidelines**: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/
- **PowerShell Help**: https://learn.microsoft.com/en-us/powershell/

