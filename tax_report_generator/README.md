# Tax Report Generator

A modular, reusable tax report generation system following SOLID and DRY principles.

## 🎯 Features

- **WFH Calculation**: Automatically calculates work-from-home percentage from location logs
- **Dynamic Deductions**: Recalculates tax deductions based on actual WFH percentage
- **Bank Integration**: Processes and categorizes bank statement transactions
- **Comprehensive Reports**: Generates multi-sheet Excel reports with detailed breakdowns
- **Reusable**: Parameterized design allows use across multiple financial years

## 🏗️ Architecture

The system follows SOLID principles:

### Single Responsibility Principle (SRP)
Each module has one clear responsibility:
- `config.py` - Configuration management
- `wfh_processor.py` - WFH log processing
- `invoice_processor.py` - Invoice catalog processing
- `bank_processor.py` - Bank statement processing
- `report_generator.py` - Excel report generation
- `main.py` - Orchestration

### Open/Closed Principle (OCP)
- Open for extension (new processors, report types)
- Closed for modification (core logic remains stable)

### Dependency Inversion Principle (DIP)
- Modules depend on abstractions (DataFrames, dictionaries)
- Not on concrete implementations

### DRY (Don't Repeat Yourself)
- Reusable functions for common operations
- Parameterized configurations
- Extracted helper methods

## 📁 Module Structure

```
tax_report_generator/
├── __init__.py           # Package initialization
├── config.py             # Configuration management
├── wfh_processor.py      # WFH log processing
├── invoice_processor.py  # Invoice processing
├── bank_processor.py     # Bank statement processing
├── report_generator.py   # Excel report generation
├── main.py              # Main orchestrator
└── README.md            # This file
```

## 🚀 Usage

### Basic Usage

```python
from tax_report_generator.main import TaxReportGenerator

# Generate report for FY2024-2025
generator = TaxReportGenerator(financial_year="2024-2025")
report_path = generator.run()
```

### Command Line

```bash
# Generate report for current FY
python generate_tax_report.py

# Specify financial year
python generate_tax_report.py --financial-year 2025-2026

# Custom base directory
python generate_tax_report.py --base-dir "C:/Tax Documents"
```

### Advanced Usage

```python
from pathlib import Path
from tax_report_generator.config import Config
from tax_report_generator.main import TaxReportGenerator

# Custom configuration
config = Config(
    financial_year="2024-2025",
    base_dir=Path("C:/Tax Documents")
)

# Create generator with custom config
generator = TaxReportGenerator(
    financial_year=config.financial_year,
    base_dir=config.base_dir
)

# Run generation
report_path = generator.run()
```

## 📊 Output

The generated Excel report contains:

1. **Summary** - Overview of WFH statistics and deductions
2. **Invoice Catalog** - All invoices with recalculated deductions
3. **Category Breakdown** - Deductions grouped by expense category
4. **WFH Analysis** - Daily and monthly work-from-home patterns
5. **Bank Statements** - Categorized bank transactions
6. **Monthly Summary** - Month-by-month expense breakdown

## ⚙️ Configuration

### File Paths

Configure file paths for any financial year:

```python
from tax_report_generator.config import FilePaths

paths = FilePaths.for_financial_year("2024-2025")
```

### Tax Parameters

Configure tax calculation parameters:

```python
from tax_report_generator.config import TaxParameters

params = TaxParameters.for_australian_fy(2024)
```

### Report Formatting

Customize report appearance:

```python
from tax_report_generator.config import ReportConfig

report_config = ReportConfig.default()
# Modify as needed
report_config.excel_header_color = "366092"
```

## 🔧 Extending the System

### Adding New Processors

Create a new processor following the same pattern:

```python
class NewProcessor:
    """Process new data type"""
    
    def __init__(self):
        self.data = None
    
    def load_data(self, file_path: Path):
        """Load data from file"""
        pass
    
    def process_data(self):
        """Process the data"""
        pass
    
    def get_summary_statistics(self):
        """Return summary statistics"""
        pass
    
    def get_data_for_export(self):
        """Return data for export"""
        pass
```

### Adding New Report Sheets

Extend the ReportGenerator:

```python
def add_custom_sheet(self, data: pd.DataFrame):
    """Add custom sheet to report"""
    ws = self.workbook.create_sheet("Custom Sheet")
    # Add your custom logic
```

## 📋 Requirements

- Python 3.7+
- pandas
- openpyxl

## 🔄 Reusability

The system is designed for reuse across financial years:

```python
# Generate reports for multiple years
for year in range(2024, 2027):
    fy = f"{year}-{year+1}"
    generator = TaxReportGenerator(financial_year=fy)
    generator.run()
```

## 🐛 Error Handling

The system includes comprehensive error handling:

- File validation before processing
- Graceful handling of missing optional files
- Detailed error messages
- Stack traces in verbose mode

## 📝 License

Internal use only.

## 👥 AuthorNow let me create a comprehensive README file to document the modular system:

<create_file>
<path>tax_report_generator/README.md</path>
<content>
# Tax Report Generator

A modular, reusable tax report generation system built with SOLID principles and DRY practices. Automatically calculates expenses based on Work From Home (WFH) logs and generates comprehensive Excel reports.

## 🎯 Features

- **Modular Design**: Each component has a single responsibility
- **Reusable**: Configurable for different financial years
- **Comprehensive**: Processes WFH logs, invoices, and bank statements
- **Excel Output**: Multi-sheet reports with filtering and formatting
- **Error Handling**: Graceful handling of missing files and data
- **Progress Feedback**: Clear console output during processing

## 📁 Project Structure

```
tax_report_generator/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── wfh_processor.py         # WFH log processing
├── invoice_processor.py     # Invoice catalog processing
├── bank_processor.py        # Bank statement processing
├── report_generator.py      # Excel report generation
├── main.py                  # Orchestration logic
└── README.md               # This documentation

generate_tax_report.py      # CLI entry point
```

## 🏗️ Architecture Principles

### SOLID Principles
- **Single Responsibility**: Each module handles one concern
- **Open/Closed**: Modules are open for extension, closed for modification
- **Liskov Substitution**: Compatible interfaces
- **Interface Segregation**: Focused interfaces
- **Dependency Inversion**: Depends on abstractions

### DRY (Don't Repeat Yourself)
- Centralized configuration
- Reusable calculation methods
- Consistent error handling
- Standardized formatting

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas openpyxl
```

### Basic Usage
```bash
# Generate report for FY2024-2025 (default)
python generate_tax_report.py

# Generate report for specific financial year
python generate_tax_report.py --financial-year 2025-2026

# Specify custom base directory
python generate_tax_report.py --base-dir "G:/My Drive/Tax Invoices"
```

### Programmatic Usage
```python
from tax_report_generator.main import TaxReportGenerator

# Create generator
generator = TaxReportGenerator(financial_year="2024-2025")

# Generate report
report_path = generator.run()

print(f"Report generated: {report_path}")
```

## 📋 Input Files

The system expects the following file structure:

```
Base Directory/
├── wfh/
│   └── wfh_2024_2025.csv          # WFH log
├── FY2024-2025/
│   └── Processed/
│       ├── Invoice_Catalog_20251031_193538.csv    # Invoice catalog
│       ├── Deduction_Summary_20251031_193538.csv  # Deduction summary (optional)
│       └── BankStatements/
│           └── ZipMoney_20251031_201436/
│               └── expense_catalog.csv            # Bank statements (optional)
```

### WFH Log Format
```csv
Date,Time,Day,Location
2024-07-01,09:00:05,Monday,Home
2024-07-02,09:00:04,Tuesday,Home
2024-07-03,09:00:06,Wednesday,Work
2024-07-04,09:00:08,Thursday,Leave
```

### Invoice Catalog Format
```csv
ProcessDate,FileName,VendorName,InvoiceNumber,InvoiceDate,Category,Currency,InvoiceTotal,DeductibleAmount,WorkUsePercentage
2025-10-31,invoice.pdf,Vendor Name,INV001,2024-07-01,Electricity,AUD,150.00,90.00,60
```

## ⚙️ Configuration

### File Paths
Paths are automatically configured based on financial year:

```python
from tax_report_generator.config import Config

config = Config(financial_year="2024-2025")
print(config.file_paths.wfh_log)
# Output: wfh/wfh_2024_2025.csv
```

### Tax Parameters
Configure tax calculation parameters:

```python
from tax_report_generator.config import TaxParameters

params = TaxParameters.for_australian_fy(2024)
print(params.wfh_categories)
# Output: ['Electricity', 'Internet', 'Phone & Mobile', ...]
```

### Report Formatting
Customize Excel report appearance:

```python
from tax_report_generator.config import ReportConfig

config = ReportConfig.default()
config.currency_format = "$#,##0.00"
config.excel_header_color = "4F81BD"
```

## 📊 Output Report

The system generates a comprehensive Excel workbook with multiple sheets:

### Summary Sheet
- Overall WFH statistics
- Total deductions (original vs recalculated)
- Bank statement summary
- Key metrics overview

### Invoice Catalog Sheet
- All processed invoices
- Recalculated deductions
- Category and vendor information
- Filtering and sorting capabilities

### Category Breakdown Sheet
- Deductions grouped by category
- Original vs recalculated amounts
- Adjustment calculations

### WFH Analysis Sheet
- Daily WFH log
- Monthly statistics
- Percentage breakdowns
- Trend analysis

### Bank Statements Sheet
- Categorized transactions
- Tax relevance flags
- Amount summaries

### Monthly Summary Sheet
- Month-by-month breakdown
- Invoice counts and totals
- WFH percentage by month

## 🔧 Customization

### Adding New Categories
```python
# Modify tax parameters
params = TaxParameters.for_australian_fy(2024)
params.wfh_categories.append("New Category")
```

### Custom Financial Years
```python
# Create custom configuration
config = Config(financial_year="2023-2024")
config.tax_params.fy_start_date = "2023-07-01"
config.tax_params.fy_end_date = "2024-06-30"
```

### Extending Processors
```python
from tax_report_generator.wfh_processor import WFHProcessor

class CustomWFHProcessor(WFHProcessor):
    def calculate_custom_metric(self):
        # Add custom calculations
        return self.wfh_data.count() * 1.1
```

## 🧪 Testing

### Unit Tests
```python
import unittest
from tax_report_generator.wfh_processor import WFHProcessor

class TestWFHProcessor(unittest.TestCase):
    def test_calculate_percentage(self):
        processor = WFHProcessor()
        # Add test logic
        pass
```

### Integration Tests
```python
from tax_report_generator.main import TaxReportGenerator

def test_full_workflow():
    generator = TaxReportGenerator("2024-2025")
    report_path = generator.run()
    assert report_path.exists()
```

## 📈 Performance

- **Memory Efficient**: Processes data in chunks
- **Fast Processing**: Optimized pandas operations
- **Scalable**: Handles large datasets
- **Error Recovery**: Continues processing on individual failures

## 🔒 Error Handling

The system provides comprehensive error handling:

- **Missing Files**: Clear error messages with file paths
- **Data Validation**: Validates date formats and required fields
- **Graceful Degradation**: Continues with optional components
- **Detailed Logging**: Progress feedback and error details

## 🤝 Contributing

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all public methods
- Write unit tests for new functionality
- Update documentation

### Adding New Features
1. Create new module following SRP
2. Add configuration parameters
3. Update main orchestrator
4. Add tests and documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**"WFH log not found"**
- Check file path: `wfh/wfh_2024_2025.csv`
- Verify financial year parameter

**"Invoice catalog not found"**
- Check path: `FY2024-2025/Processed/Invoice_Catalog_*.csv`
- Ensure file exists and is readable

**"Permission denied"**
- Check write permissions for output directory
- Close Excel files before running

### Debug Mode
```bash
python generate_tax_report.py --verbose
```

## 🔄 Version History

- **v1.0.0**: Initial release with modular architecture
  - WFH log processing
  - Invoice recalculation
  - Bank statement integration
  - Multi-sheet Excel reports

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Ensure all input files are present
4. Verify file formats match specifications

---

Built with ❤️ using Python, pandas, and openpyxl
