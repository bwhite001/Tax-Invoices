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

1. **Create Invoice Folder Structure**
   ```
   C:\Invoices\
   ├── 2024-25\
   │   ├── Electricity\
   │   ├── Internet\
   │   ├── Software\
   │   └── (other categories)
   └── Processed\
   ```

2. **Move Invoice Files**
   - Place all PDF, PNG, JPG, DOC, DOCX, XLS, XLSX, EML files in `C:\Invoices\2024-25\`
   - Organize by category if desired (optional)

## Step 6: Configure PowerShell Script

1. **Download Script**
   - Save the `Invoice-Cataloger-LMStudio.ps1` script to: `C:\Scripts\`

2. **Edit Configuration**
   - Open `Invoice-Cataloger-LMStudio.ps1` in Notepad or VSCode
   - Update the `$Config` section:
     ```powershell
     $Config = @{
         LMStudioEndpoint = "http://localhost:1234/v1/chat/completions"
         InvoiceFolder = "C:\Invoices\2024-25"
         OutputFolder = "C:\Invoices\Processed"
         # ... other settings
     }
     ```

3. **Enable PowerShell Execution** (If needed)
   - If you get execution policy error, run PowerShell as Administrator:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## Step 7: Run the Script

1. **Open PowerShell as Administrator**
   - Right-click PowerShell in Start Menu
   - Select "Run as administrator"

2. **Navigate to Script Location**
   ```powershell
   cd C:\Scripts
   ```

3. **Execute Script**
   ```powershell
   .\Invoice-Cataloger-LMStudio.ps1
   ```

4. **Monitor Processing**
   - Script will process each file
   - Display progress in PowerShell window
   - Creates CSV file when complete
   - Automatically opens CSV in Excel

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

### "No files found to process"
- ✓ Check folder path in $Config is correct
- ✓ Verify files are PDF, PNG, JPG, JPEG, GIF, DOC, DOCX, XLS, XLSX, or EML
- ✓ Ensure files are in `C:\Invoices\2024-25\` not subfolder

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

## Next Steps

1. After running script, check the generated CSV files:
   - `Invoice_Catalog_*.csv` - Detailed invoice list
   - `Deduction_Summary_*.csv` - Category summaries

2. Review ATO compliance for each expense:
   - Check "ClaimMethod" column
   - Note any items requiring further documentation
   - Flag questionable items for accountant review

3. Store archival:
   - Keep original invoice files in `C:\Invoices\2024-25\`
   - Backup CSV files to cloud storage (OneDrive, Google Drive)
   - Maintain records for 5 years per ATO requirements

## Support Resources

- **LM Studio Documentation**: https://lmstudio.ai/docs
- **Model Information**: https://huggingface.co/models
- **ATO Guidelines**: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/
- **PowerShell Help**: https://learn.microsoft.com/en-us/powershell/

