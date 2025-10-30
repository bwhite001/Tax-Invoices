# Quick Start Guide - Invoice Cataloger (Python)

## 🚀 Get Started in 5 Minutes

### Step 1: Install Python Dependencies

```bash
cd "g:/My Drive/Tax Invoices/invoice_cataloger"
pip install -r requirements.txt
```

**Note:** This will install all required libraries. Some optional OCR libraries may take a few minutes.

### Step 2: Verify LM Studio is Running

1. Open LM Studio
2. Load a model (e.g., Mistral 7B)
3. Click "Start Server" in the Developer tab
4. Verify it's running at `http://localhost:1234`

### Step 3: Check Prerequisites

```bash
python invoice_cataloger.py --check-only
```

You should see:
```
✓ Invoice folder exists
✓ Output folder ready
✓ LM Studio connected
✓ Available extraction methods
```

### Step 4: Run Your First Processing

```bash
python invoice_cataloger.py --financial-year 2024-2025
```

The script will:
1. Scan for invoice files
2. Extract text using multiple methods
3. Use AI to extract invoice data
4. Categorize expenses
5. Calculate ATO deductions
6. Export to Excel and CSV

### Step 5: Check Results

Results are saved in:
```
G:/My Drive/Tax Invoices/FY2024-2025/Processed/
├── Invoice_Catalog_YYYYMMDD_HHMMSS.xlsx
├── Invoice_Catalog_YYYYMMDD_HHMMSS.csv
├── Deduction_Summary_YYYYMMDD_HHMMSS.csv
└── Logs/processing_YYYYMMDD.log
```

---

## 🔧 Configuration

Edit `invoice_cataloger/config.py` if needed:

```python
# Change LM Studio endpoint (if not localhost)
lm_studio_endpoint = "http://192.168.0.100:1234/v1/chat/completions"

# Change financial year
financial_year = "2024-2025"

# Change work-from-home settings
work_from_home_days = 3
total_work_days = 5
```

---

## 📋 Common Commands

```bash
# Process current financial year
python invoice_cataloger.py --financial-year 2024-2025

# Retry failed files
python invoice_cataloger.py --financial-year 2024-2025 --retry-failed

# Verbose output (see detailed logs)
python invoice_cataloger.py --financial-year 2024-2025 --verbose

# Check setup only
python invoice_cataloger.py --check-only
```

---

## ❓ Troubleshooting

### "No text extracted" errors

**Solution:** The new Python version has 5 extraction methods! If you see this error:

1. Check if the PDF is password-protected
2. Install additional OCR libraries:
   ```bash
   pip install easyocr pytesseract pdf2image
   ```
3. Check the logs for specific errors:
   ```
   G:/My Drive/Tax Invoices/FY2024-2025/Processed/Logs/processing_YYYYMMDD.log
   ```

### "Cannot connect to LM Studio"

**Solution:**
1. Open LM Studio
2. Load a model
3. Go to Developer tab → Start Server
4. Verify endpoint in `config.py`

### Import errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

---

## 🎯 What's Different from PowerShell Version?

### ✅ Fixed Issues
- **PDF text extraction now works!** (5 different methods with automatic fallback)
- Better error messages
- Faster processing
- Cross-platform support

### 📝 Command Changes
**Old (PowerShell):**
```powershell
.\Invoice-Cataloger-LMStudio.ps1 -FinancialYear "2024-2025"
```

**New (Python):**
```bash
python invoice_cataloger.py --financial-year 2024-2025
```

### 📂 File Structure (Same)
Output files are in the same location:
```
G:/My Drive/Tax Invoices/FY2024-2025/Processed/
```

---

## 📊 Expected Output

After processing, you'll see:

```
=== PROCESSING COMPLETE ===
Successful: 250 files
Failed: 5 files
Cached (Duplicates): 10 files
Skipped (Max retries): 0 files
Total processed: 265 invoices
Time elapsed: 0:15:30

TIP: Run with --retry-failed to retry failed files
```

---

## 🆘 Need Help?

1. **Check the logs:**
   ```
   G:/My Drive/Tax Invoices/FY2024-2025/Processed/Logs/processing_YYYYMMDD.log
   ```

2. **Run with verbose mode:**
   ```bash
   python invoice_cataloger.py --financial-year 2024-2025 --verbose
   ```

3. **Check prerequisites:**
   ```bash
   python invoice_cataloger.py --check-only
   ```

---

## 🎉 Success!

If everything works, you should have:
- ✅ Excel file with formatted invoice catalog
- ✅ CSV files for further analysis
- ✅ Summary report by category
- ✅ ATO-compliant deduction calculations
