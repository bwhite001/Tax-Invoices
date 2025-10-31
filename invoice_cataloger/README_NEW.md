# Invoice Cataloger - SOLID & DRY Refactored Edition

Professional Invoice Cataloging System with Modular Tax Calculation for ATO-Compliant Work Expense Tracking.

## 🎯 New Architecture (Phases 1-4 Complete)

This system now follows **SOLID principles** with a clean separation between:
1. **Invoice Cataloging** - Extract and categorize invoices
2. **Tax Calculation** - Calculate deductions using pluggable strategies
3. **WFH Integration** - Dynamic work-use percentage from actual WFH logs

## ✨ Key Features

### Core Functionality
✅ **Robust Multi-Format Extraction**:
- PDF documents (multi-stage extraction with fallback)
- Images (PNG, JPG, JPEG, GIF) with OCR
- Word documents (.doc, .docx)
- Excel spreadsheets (.xls, .xlsx)
- Email files (.eml, .msg)

✅ **AI-Powered Data Extraction**:
- LM Studio (local LLM)
- OpenAI API support
- OpenRouter API support
- Custom prompt support

✅ **Smart Categorization** - 20+ expense categories with vendor overrides

✅ **Duplicate Detection** - MD5 hash-based caching

✅ **Failed File Tracking** - Automatic retry mechanism

### New Modular Features (Phases 1-4)

✅ **Catalog-Only Mode** - Extract and categorize without tax calculations

✅ **Pluggable Tax Strategies** - ATO strategy with externalized rules

✅ **WFH Log Integration** - Calculate dynamic work-use % from actual WFH days

✅ **Standalone Tax Calculator** - Process existing catalogs separately

✅ **Professional Reports** - Excel and CSV exports with formatting

---

## 📦 Installation

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

**For PDF to Image conversion:**
```bash
pip install pdf2image

# Also requires poppler:
# Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
# Mac: brew install poppler
# Linux: sudo apt-get install poppler-utils
```

### 3. Setup API Provider

**Option A: LM Studio (Local, Free)**
1. Download and install [LM Studio](https://lmstudio.ai)
2. Load a model (recommended: Mistral 7B or similar)
3. Start the Developer Server
4. Note the endpoint (default: http://localhost:1234)

**Option B: OpenAI**
1. Get API key from https://platform.openai.com
2. Set in `.env`: `OPENAI_API_KEY=your-key`
3. Set provider: `API_PROVIDER=openai`

**Option C: OpenRouter**
1. Get API key from https://openrouter.ai
2. Set in `.env`: `OPENROUTER_API_KEY=your-key`
3. Set provider: `API_PROVIDER=openrouter`

---

## 🚀 Usage

### Two-Phase Process

The system now supports a **two-phase workflow**:

#### Phase 1: Catalog Invoices (Extract & Categorize)
```bash
# Catalog only - no tax calculations
python invoice_cataloger.py --catalog-only --financial-year 2024-2025
```

**Output**: `Invoice_Catalog_{timestamp}.csv` with invoice data (no tax fields)

#### Phase 2: Calculate Tax Deductions
```bash
# Calculate tax from existing catalog
python tax_calculator_cli.py --catalog Invoice_Catalog_20241031.csv --output tax_report.csv
```

**Output**: `tax_report.csv` with deduction calculations

### Full Process (Catalog + Tax in One Step)

```bash
# Traditional workflow - catalog and calculate tax together
python invoice_cataloger.py --financial-year 2024-2025
```

### With WFH Log (Dynamic Work-Use %)

```bash
# Use actual WFH days to calculate work-use percentage
python invoice_cataloger.py --financial-year 2024-2025 --wfh-log examples/wfh_log.csv
```

### Standalone Tax Calculator

```bash
# Basic usage
python tax_calculator_cli.py --catalog catalog.csv --output tax_report.csv

# With WFH log
python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --output tax_report.csv

# With static work-use percentage
python tax_calculator_cli.py --catalog catalog.csv --work-use-percentage 65 --output tax_report.csv

# Export to Excel
python tax_calculator_cli.py --catalog catalog.csv --output tax_report.xlsx --format excel
```

---

## 📋 Command Line Arguments

### Main Invoice Cataloger

```bash
python invoice_cataloger.py [OPTIONS]
```

**Options:**
- `--financial-year YYYY-YYYY` - Specify financial year (default: 2024-2025)
- `--catalog-only` - Only catalog invoices, skip tax calculations
- `--tax-strategy {ato,custom}` - Tax calculation strategy (default: ato)
- `--wfh-log PATH` - Path to WFH log file for dynamic work-use %
- `--retry-failed` - Process only previously failed files
- `--reprocess` - Reprocess all files, ignoring cache
- `--cleanup-non-invoices` - Clean up non-invoice files
- `--dry-run` - Preview cleanup without deleting (use with --cleanup-non-invoices)
- `--check-only` - Check prerequisites without processing
- `--verbose` - Enable debug logging

### Standalone Tax Calculator

```bash
python tax_calculator_cli.py [OPTIONS]
```

**Options:**
- `--catalog PATH` - Path to catalog file (CSV, Excel, or JSON) **[Required]**
- `--wfh-log PATH` - Path to WFH log file (CSV or JSON)
- `--strategy {ato,custom}` - Tax calculation strategy (default: ato)
- `--work-use-percentage FLOAT` - Static work-use % (0-100)
- `--financial-year YYYY-YYYY` - Financial year for WFH log filtering
- `--output PATH` - Output path for tax report
- `--format {csv,excel,json}` - Output format (default: csv)
- `--show-wfh-report` - Display WFH statistics report
- `--verbose` - Enable debug logging

---

## 📁 Project Structure

```
invoice_cataloger/
├── catalog/                      # Phase 1: Pure cataloging
│   ├── cataloger.py             # Invoice cataloging (no tax)
│   ├── catalog_exporter.py      # Export catalog
│   └── catalog_loader.py        # Load catalog
│
├── tax/                          # Phase 2 & 3: Tax calculations
│   ├── tax_calculator.py        # Main tax calculator orchestrator
│   ├── strategies/              # Pluggable tax strategies
│   │   ├── base_strategy.py    # Abstract base class
│   │   └── ato_strategy.py     # ATO implementation
│   ├── rules/                   # Externalized tax rules
│   │   ├── ato_rules.json      # ATO rules configuration
│   │   └── rule_loader.py      # Load and validate rules
│   └── wfh/                     # WFH log integration
│       ├── wfh_parser.py       # Parse CSV/JSON logs
│       └── wfh_calculator.py   # Calculate work-use %
│
├── core/                         # Phase 4: Refactored modules
│   ├── prerequisite_checker.py # System validation
│   └── file_processor.py       # File processing logic
│
├── extractors/                   # Text extraction
│   ├── pdf_extractor.py
│   ├── image_extractor.py
│   ├── document_extractor.py
│   └── email_extractor.py
│
├── processors/                   # Data processing
│   ├── llm_processor.py
│   ├── categorizer.py
│   └── deduction_calculator.py
│
├── exporters/                    # Export functionality
│   ├── excel_exporter.py
│   └── csv_exporter.py
│
├── utils/                        # Utilities
│   ├── logger.py
│   └── cache_manager.py
│
├── examples/                     # Example files
│   ├── wfh_log.csv
│   └── wfh_log.json
│
├── invoice_cataloger.py          # Main CLI
├── tax_calculator_cli.py         # Standalone tax CLI
└── config.py                     # Configuration
```

---

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# API Provider (lmstudio, openai, openrouter)
API_PROVIDER=lmstudio

# LM Studio Configuration
LM_STUDIO_ENDPOINT=http://192.168.0.100:1234/v1/chat/completions
LM_STUDIO_MODEL=local-model

# OpenAI Configuration
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# OpenRouter Configuration
OPENROUTER_API_KEY=your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Financial Year
FINANCIAL_YEAR=2024-2025

# Work From Home Settings
WORK_FROM_HOME_DAYS=3
TOTAL_WORK_DAYS=5

# Tax Strategy
TAX_STRATEGY=ato
```

### config.py

```python
from pathlib import Path

# Paths
base_path = Path("G:/My Drive/Tax Invoices")
financial_year = "2024-2025"

# Work-use percentage (calculated from WFH days)
work_from_home_days = 3
total_work_days = 5
work_use_percentage = 60  # 3/5 = 60%

# Tax configuration
tax_strategy = "ato"
wfh_log_path = None  # Optional: Path to WFH log
catalog_only_mode = False
```

---

## 📊 WFH Log Format

### CSV Format

```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
2024-07-03,Home,Yes,Full day WFH
```

**Supported WFH values**: Yes/No, True/False, 1/0, Y/N (case-insensitive)

### JSON Format

```json
{
  "financial_year": "2024-2025",
  "entries": [
    {"date": "2024-07-01", "location": "Home", "wfh": true, "notes": "Full day WFH"},
    {"date": "2024-07-02", "location": "Office", "wfh": false, "notes": "In office"}
  ]
}
```

**Supported WFH values**: true/false (boolean) or "Yes"/"No" (string)

See `examples/wfh_log.csv` and `examples/wfh_log.json` for complete examples.

---

## 📈 Output Files

### Catalog-Only Mode
- `Invoice_Catalog_{timestamp}.csv` - Invoice data without tax fields
- `cache.json` - Processed files cache
- `Logs/processing_{date}.log` - Processing logs

### Full Process Mode
- `Invoice_Catalog_{timestamp}.xlsx` - Excel with multiple sheets
- `Invoice_Catalog_{timestamp}.csv` - Detailed catalog with tax data
- `Deduction_Summary_{timestamp}.csv` - Summary by category
- `Manual_Review_Required.csv` - Invoices needing review
- `cache.json` - Processed files cache
- `failed_files.json` - Failed files tracking
- `Logs/processing_{date}.log` - Processing logs

### Tax Calculator Output
- `tax_report.csv` (or .xlsx, .json) - Tax deductions report
- WFH statistics (if --show-wfh-report used)

---

## 🏗️ Architecture & Design Patterns

### SOLID Principles Applied

✅ **Single Responsibility Principle**
- `InvoiceCataloger`: Only catalogs invoices
- `TaxCalculator`: Only calculates tax deductions
- `WFHParser`: Only parses WFH logs
- `WFHCalculator`: Only calculates percentages

✅ **Open/Closed Principle**
- New tax strategies can be added without modifying existing code
- Extend `TaxStrategy` base class for custom strategies

✅ **Liskov Substitution Principle**
- All tax strategies inherit from `TaxStrategy`
- Any strategy can be substituted without breaking code

✅ **Interface Segregation Principle**
- Clean, focused interfaces
- No unnecessary dependencies

✅ **Dependency Inversion Principle**
- Depend on abstractions (`TaxStrategy`), not concrete implementations
- Tax calculator accepts any strategy implementing the interface

### Design Patterns Used

1. **Strategy Pattern** - Tax calculation strategies (ATO, custom)
2. **Factory Pattern** - Tax strategy factory
3. **Repository Pattern** - Catalog loader/exporter
4. **Dependency Injection** - Tax calculator receives strategy

---

## 🔍 Usage Examples

### Example 1: Catalog Only

```bash
# Extract and categorize invoices without tax calculations
python invoice_cataloger.py --catalog-only --financial-year 2024-2025
```

**Use Case**: When you want to review invoices before calculating tax, or when you need just the catalog data.

### Example 2: Full Process with WFH Log

```bash
# Process invoices with dynamic work-use percentage from WFH log
python invoice_cataloger.py --financial-year 2024-2025 --wfh-log examples/wfh_log.csv
```

**Use Case**: When you track your WFH days and want accurate work-use percentage.

### Example 3: Standalone Tax Calculation

```bash
# Calculate tax from an existing catalog
python tax_calculator_cli.py \
  --catalog Invoice_Catalog_20241031.csv \
  --wfh-log wfh_log.csv \
  --output tax_report.xlsx \
  --format excel \
  --show-wfh-report
```

**Use Case**: When you already have a catalog and want to recalculate tax with different parameters.

### Example 4: Retry Failed Files

```bash
# Retry only files that failed in previous run
python invoice_cataloger.py --financial-year 2024-2025 --retry-failed
```

**Use Case**: When some files failed due to temporary issues (network, API limits, etc.).

### Example 5: Custom Tax Strategy

```python
# Create custom strategy
from tax.strategies import TaxStrategy

class CustomStrategy(TaxStrategy):
    def calculate_deduction(self, invoice_data, category, work_use_pct):
        # Your custom logic here
        pass
    
    def get_strategy_name(self):
        return "Custom"

# Use custom strategy
from tax import TaxCalculator
calculator = TaxCalculator(CustomStrategy())
```

**Use Case**: When you need different tax rules (e.g., different country, different occupation).

---

## 🛠️ Troubleshooting

### No text extracted from PDFs

The system has robust multi-stage extraction. If all methods fail:

1. Check if PDF is password-protected
2. Verify PDF is not corrupted (try opening manually)
3. Check logs for specific error messages
4. Install additional OCR dependencies (EasyOCR or Tesseract)
5. Try with `--verbose` for detailed extraction logs

### API Connection Failed

**LM Studio:**
1. Ensure LM Studio is running
2. Check that a model is loaded
3. Verify Developer Server is started
4. Check endpoint URL in config
5. Try accessing http://localhost:1234/v1/models in browser

**OpenAI/OpenRouter:**
1. Verify API key is set in `.env`
2. Check API key is valid and has credits
3. Verify model name is correct
4. Check internet connection

### WFH Log Parsing Errors

1. Verify date format is YYYY-MM-DD
2. Check CSV has required columns: Date, WorkFromHome
3. Ensure WFH values are Yes/No, True/False, or 1/0
4. Check for duplicate dates
5. Validate JSON structure matches expected format

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📚 Documentation

- **`PHASE1_COMPLETE.md`** - Catalog module documentation
- **`REFACTORING_COMPLETE.md`** - Phases 1-2 summary
- **`PHASE3_COMPLETE.md`** - WFH integration documentation
- **`REFACTORING_PHASE4_PLAN.md`** - Refactoring plan
- **`VENDOR_OVERRIDES_GUIDE.md`** - Vendor override configuration
- **`API_SETUP_GUIDE.md`** - API provider setup

---

## ⚖️ ATO Compliance

This tool calculates deductions based on:
- Work-from-home percentage (static or dynamic from WFH log)
- ATO fixed rate method ($0.70/hour for 2024-25)
- Actual cost method with work-use percentage
- ATO guidelines for each expense category

**Important:** Always consult with a tax professional for your specific situation. This tool is for record-keeping and estimation purposes.

---

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

---

## 📄 License

This tool is for personal use. Consult the ATO website for official guidance on work expense deductions.

---

## 🆘 Support

For issues or questions:
1. Check the logs in `Processed/Logs/`
2. Run with `--verbose` for detailed output
3. Use `--check-only` to verify setup
4. Review documentation in the project folder
5. Check example files in `examples/` directory

---

**Version**: 2.0 (SOLID & DRY Refactored)
**Last Updated**: October 2024
