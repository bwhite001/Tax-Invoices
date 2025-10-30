# Invoice Cataloger - Python Edition

Professional Invoice Cataloging System using LM Studio (Local LLM) for ATO-Compliant Work Expense Tracking.

## Features

✅ **Robust PDF Text Extraction** - Multi-stage extraction with automatic fallback:
- PyMuPDF (native text extraction)
- pdfplumber (table extraction)
- pypdf (pure Python fallback)
- EasyOCR (deep learning OCR)
- Tesseract OCR (traditional OCR)

✅ **Multi-Format Support**:
- PDF documents
- Images (PNG, JPG, JPEG, GIF)
- Word documents (.doc, .docx)
- Excel spreadsheets (.xls, .xlsx)
- Email files (.eml, .msg)

✅ **AI-Powered Data Extraction** using LM Studio (local LLM)

✅ **Smart Categorization** - 20+ expense categories

✅ **ATO Deduction Calculations** - Automatic work-use percentage calculations

✅ **Duplicate Detection** - MD5 hash-based caching

✅ **Failed File Tracking** - Automatic retry mechanism

✅ **Professional Reports** - Excel and CSV exports with formatting

## Installation

### 1. Install Python Dependencies

```bash
cd invoice_cataloger
pip install -r requirements.txt
```

### 2. Install Optional Dependencies

**For OCR (Recommended):**
```bash
# EasyOCR (no additional setup needed)
pip install easyocr

# Tesseract (requires separate installation)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

**For PDF to Image conversion (for OCR):**
```bash
pip install pdf2image

# Also requires poppler:
# Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
# Mac: brew install poppler
# Linux: sudo apt-get install poppler-utils
```

### 3. Setup LM Studio

1. Download and install [LM Studio](https://lmstudio.ai)
2. Load a model (recommended: Mistral 7B or similar)
3. Start the Developer Server
4. Note the endpoint (default: http://localhost:1234)

## Configuration

Edit `config.py` to customize:

```python
# LM Studio endpoint
lm_studio_endpoint = "http://192.168.0.100:1234/v1/chat/completions"

# Financial year
financial_year = "2024-2025"

# Work from home settings
work_from_home_days = 3
total_work_days = 5
work_use_percentage = 60  # 3/5 = 60%

# Paths
base_path = Path("G:/My Drive/Tax Invoices")
```

## Usage

### Basic Usage

```bash
# Process invoices for current financial year
python invoice_cataloger.py --financial-year 2024-2025

# Check prerequisites only
python invoice_cataloger.py --check-only

# Retry failed files
python invoice_cataloger.py --financial-year 2024-2025 --retry-failed

# Verbose output (debug mode)
python invoice_cataloger.py --financial-year 2024-2025 --verbose
```

### Command Line Arguments

- `--financial-year YYYY-YYYY` - Specify financial year (default: 2024-2025)
- `--retry-failed` - Process only previously failed files
- `--check-only` - Check prerequisites without processing
- `--verbose` - Enable debug logging

## Project Structure

```
invoice_cataloger/
├── invoice_cataloger.py          # Main script
├── config.py                     # Configuration
├── requirements.txt              # Python dependencies
├── extractors/                   # Text extraction modules
│   ├── pdf_extractor.py         # Multi-stage PDF extraction
│   ├── image_extractor.py       # OCR for images
│   ├── document_extractor.py    # Word/Excel extraction
│   └── email_extractor.py       # Email file extraction
├── processors/                   # Data processing modules
│   ├── llm_processor.py         # LM Studio integration
│   ├── categorizer.py           # Expense categorization
│   └── deduction_calculator.py  # ATO calculations
├── utils/                        # Utility modules
│   ├── logger.py                # Logging with colors
│   └── cache_manager.py         # Cache & failed files
└── exporters/                    # Export modules
    ├── excel_exporter.py        # Excel with formatting
    └── csv_exporter.py          # CSV exports
```

## Output Files

The script creates the following in `FY{Year}/Processed/`:

- `Invoice_Catalog_{timestamp}.xlsx` - Excel file with multiple sheets
- `Invoice_Catalog_{timestamp}.csv` - Detailed catalog
- `Deduction_Summary_{timestamp}.csv` - Summary by category
- `cache.json` - Processed files cache
- `failed_files.json` - Failed files tracking
- `Logs/processing_{date}.log` - Processing logs

## PDF Extraction Methods

The system tries multiple extraction methods in order:

1. **PyMuPDF** - Fastest, best for text-based PDFs
2. **pdfplumber** - Better for tables and structured data
3. **pypdf** - Pure Python fallback
4. **EasyOCR** - Deep learning OCR (no Tesseract needed)
5. **Tesseract** - Traditional OCR (if installed)

## Troubleshooting

### No text extracted from PDFs

The new Python version has robust multi-stage extraction. If all methods fail:

1. Check if PDF is password-protected
2. Try opening the PDF manually to verify it's not corrupted
3. Check the logs for specific error messages
4. Install additional OCR dependencies (EasyOCR or Tesseract)

### LM Studio connection failed

1. Ensure LM Studio is running
2. Check that a model is loaded
3. Verify the Developer Server is started
4. Check the endpoint URL in `config.py`
5. Try accessing http://localhost:1234/v1/models in a browser

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## ATO Compliance

This tool calculates deductions based on:
- Work-from-home percentage (default: 60% for 3/5 days)
- ATO fixed rate method ($0.70/hour for 2024-25)
- Actual cost method with work-use percentage

**Important:** Always consult with a tax professional for your specific situation.

## License

This tool is for personal use. Consult the ATO website for official guidance on work expense deductions.

## Support

For issues or questions:
1. Check the logs in `Processed/Logs/`
2. Run with `--verbose` for detailed output
3. Use `--check-only` to verify setup
