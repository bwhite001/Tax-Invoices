# Phases 3-6 Implementation Instructions

This document provides detailed instructions and context for completing the remaining phases of the SOLID & DRY refactoring.

---

## 📋 Current Status

### ✅ Completed:
- **Phase 1**: Catalog Module (invoice cataloging without tax calculations)
- **Phase 2**: Tax Calculation System (Strategy Pattern, externalized rules)

### ⏳ Remaining:
- **Phase 3**: WFH Log Integration
- **Phase 4**: CLI Updates
- **Phase 5**: Documentation
- **Phase 6**: Full Testing & Validation

---

## Phase 3: WFH Log Integration

### 🎯 Goal
Support dynamic work-use percentage based on actual work-from-home days from log files.

### 📁 Files to Create

#### 1. `tax/wfh/__init__.py`
```python
"""
WFH Module - Work From Home Log Integration

Calculates dynamic work-use percentage based on actual WFH days.
"""

from .wfh_parser import WFHParser
from .wfh_calculator import WFHCalculator

__all__ = ['WFHParser', 'WFHCalculator']
```

#### 2. `tax/wfh/wfh_parser.py`
**Purpose**: Parse WFH logs from CSV or JSON files

**Key Methods**:
- `parse_csv(file_path)` - Parse CSV format
- `parse_json(file_path)` - Parse JSON format
- `validate_log(log_data)` - Validate log structure
- `filter_by_date_range(log_data, start_date, end_date)` - Filter by dates
- `filter_by_financial_year(log_data, financial_year)` - Filter by FY

**CSV Format**:
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
2024-07-03,Home,Yes,Full day WFH
```

**JSON Format**:
```json
{
  "financial_year": "2024-2025",
  "entries": [
    {"date": "2024-07-01", "location": "Home", "wfh": true, "notes": "Full day WFH"},
    {"date": "2024-07-02", "location": "Office", "wfh": false, "notes": "In office"}
  ]
}
```

**Implementation Tips**:
- Use `csv.DictReader` for CSV parsing
- Use `json.load()` for JSON parsing
- Validate date formats (YYYY-MM-DD)
- Handle missing or invalid data gracefully
- Support both boolean and string values for WFH field

#### 3. `tax/wfh/wfh_calculator.py`
**Purpose**: Calculate work-use percentage from WFH logs

**Key Methods**:
- `calculate_wfh_percentage(log_data)` - Calculate WFH %
- `calculate_wfh_days(log_data)` - Count WFH days
- `calculate_total_work_days(log_data)` - Count total work days
- `generate_wfh_report(log_data)` - Generate statistics report
- `get_wfh_stats_by_month(log_data)` - Monthly breakdown

**Calculation Logic**:
```python
wfh_days = count of entries where wfh == True
total_work_days = total count of entries
work_use_percentage = (wfh_days / total_work_days) * 100
```

**Example Report**:
```
WFH Statistics Report
Financial Year: 2024-2025
Total Work Days: 260
WFH Days: 156
Office Days: 104
WFH Percentage: 60%

Monthly Breakdown:
July 2024: 12 WFH / 20 total (60%)
August 2024: 15 WFH / 22 total (68%)
...
```

#### 4. Integration with Tax Calculator

**Modify `tax/tax_calculator.py`** (to be created in Phase 4):
```python
def __init__(self, strategy, work_use_percentage=None, wfh_log_path=None):
    if wfh_log_path:
        # Parse WFH log
        parser = WFHParser()
        log_data = parser.parse(wfh_log_path)
        
        # Calculate dynamic percentage
        calculator = WFHCalculator()
        work_use_percentage = calculator.calculate_wfh_percentage(log_data)
        
        self.logger.info(f"Using dynamic work-use %: {work_use_percentage}%")
    
    self.work_use_percentage = work_use_percentage or 60  # Default
```

### 📝 Example WFH Log Files

Create `examples/wfh_log.csv`:
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
2024-07-03,Home,Yes,Full day WFH
2024-07-04,Home,Yes,Full day WFH
2024-07-05,Office,No,In office
```

Create `examples/wfh_log.json`:
```json
{
  "financial_year": "2024-2025",
  "entries": [
    {"date": "2024-07-01", "location": "Home", "wfh": true, "notes": "Full day WFH"},
    {"date": "2024-07-02", "location": "Office", "wfh": false, "notes": "In office"},
    {"date": "2024-07-03", "location": "Home", "wfh": true, "notes": "Full day WFH"}
  ]
}
```

### ✅ Testing Phase 3
- Test CSV parsing with valid and invalid files
- Test JSON parsing with valid and invalid files
- Test date range filtering
- Test financial year filtering
- Test percentage calculation
- Test with missing WFH log (fallback to config default)

---

## Phase 4: CLI Updates

### 🎯 Goal
Update CLI to support new architecture with catalog-only mode and standalone tax calculator.

### 📁 Files to Create/Modify

#### 1. Create `tax/tax_calculator.py`
**Purpose**: Main tax calculator that orchestrates everything

**Key Methods**:
```python
class TaxCalculator:
    def __init__(self, strategy, work_use_percentage=None, wfh_log_path=None):
        """Initialize with strategy and optional WFH log"""
        
    def calculate_deductions(self, catalog_entries):
        """Calculate deductions for all catalog entries"""
        
    def export_tax_report(self, tax_entries, output_path):
        """Export tax report with deductions"""
```

**Implementation**:
```python
from pathlib import Path
from typing import List, Dict, Any, Optional
from catalog import CatalogLoader
from .strategies.base_strategy import TaxStrategy
from .wfh.wfh_parser import WFHParser
from .wfh.wfh_calculator import WFHCalculator

class TaxCalculator:
    def __init__(self, strategy: TaxStrategy, 
                 work_use_percentage: Optional[float] = None,
                 wfh_log_path: Optional[Path] = None):
        self.strategy = strategy
        self.logger = get_logger()
        
        # Calculate work-use percentage
        if wfh_log_path:
            parser = WFHParser()
            log_data = parser.parse(wfh_log_path)
            calculator = WFHCalculator()
            self.work_use_percentage = calculator.calculate_wfh_percentage(log_data)
            self.logger.info(f"Dynamic work-use %: {self.work_use_percentage}%")
        else:
            self.work_use_percentage = work_use_percentage or 60
            self.logger.info(f"Static work-use %: {self.work_use_percentage}%")
    
    def calculate_deductions(self, catalog_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate tax deductions for catalog entries"""
        tax_entries = []
        
        for entry in catalog_entries:
            # Calculate deduction
            deduction = self.strategy.calculate_deduction(
                entry,
                entry.get('Category', 'Other'),
                self.work_use_percentage
            )
            
            # Merge catalog entry with deduction
            tax_entry = {**entry, **deduction}
            tax_entries.append(tax_entry)
        
        return tax_entries
```

#### 2. Create `tax_calculator_cli.py` (Standalone Script)
**Purpose**: Standalone CLI for tax calculation

```python
#!/usr/bin/env python3
"""
Standalone Tax Calculator CLI

Calculate tax deductions from an existing invoice catalog.
"""
import argparse
from pathlib import Path
from tax import TaxCalculator, ATOStrategy
from catalog import CatalogLoader

def main():
    parser = argparse.ArgumentParser(
        description="Calculate tax deductions from invoice catalog"
    )
    parser.add_argument(
        '--catalog',
        type=str,
        required=True,
        help='Path to catalog file (CSV, Excel, or JSON)'
    )
    parser.add_argument(
        '--wfh-log',
        type=str,
        help='Path to WFH log file (CSV or JSON)'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        default='ato',
        choices=['ato', 'custom'],
        help='Tax calculation strategy (default: ato)'
    )
    parser.add_argument(
        '--work-use-percentage',
        type=float,
        help='Static work-use percentage (0-100). Overridden by --wfh-log'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output path for tax report'
    )
    
    args = parser.parse_args()
    
    # Load catalog
    loader = CatalogLoader()
    catalog = loader.load_catalog(Path(args.catalog))
    
    # Create strategy
    if args.strategy == 'ato':
        strategy = ATOStrategy()
    else:
        # Load custom strategy
        pass
    
    # Create calculator
    calculator = TaxCalculator(
        strategy,
        work_use_percentage=args.work_use_percentage,
        wfh_log_path=Path(args.wfh_log) if args.wfh_log else None
    )
    
    # Calculate deductions
    tax_entries = calculator.calculate_deductions(catalog)
    
    # Export report
    if args.output:
        calculator.export_tax_report(tax_entries, Path(args.output))
    
    print(f"Processed {len(tax_entries)} invoices")

if __name__ == '__main__':
    main()
```

#### 3. Modify `invoice_cataloger.py`

**Add new CLI arguments**:
```python
parser.add_argument(
    '--catalog-only',
    action='store_true',
    help='Only catalog invoices, skip tax calculations'
)
parser.add_argument(
    '--tax-strategy',
    type=str,
    default='ato',
    choices=['ato', 'custom'],
    help='Tax calculation strategy (default: ato)'
)
parser.add_argument(
    '--wfh-log',
    type=str,
    help='Path to WFH log file for dynamic work-use percentage'
)
```

**Modify `run()` method**:
```python
def run(self, catalog_only=False, tax_strategy='ato', wfh_log_path=None):
    # ... existing catalog code ...
    
    catalog_entries = self.catalog_invoices()
    
    if catalog_only:
        self.logger.info("CATALOG-ONLY MODE: Skipping tax calculations")
        # Export catalog only
        self.catalog_exporter.export_csv(catalog_entries)
        return
    
    # Calculate tax deductions
    from tax import TaxCalculator, ATOStrategy
    
    if tax_strategy == 'ato':
        strategy = ATOStrategy()
    
    calculator = TaxCalculator(
        strategy,
        work_use_percentage=self.config.work_use_percentage,
        wfh_log_path=Path(wfh_log_path) if wfh_log_path else None
    )
    
    tax_entries = calculator.calculate_deductions(catalog_entries)
    
    # Export with tax data
    self.export_with_tax(tax_entries)
```

#### 4. Update `config.py`

**Add new configuration fields**:
```python
@dataclass
class Config:
    # ... existing fields ...
    
    # Tax Configuration
    tax_strategy: str = field(default_factory=lambda: os.getenv("TAX_STRATEGY", "ato"))
    tax_rules_path: Optional[Path] = None
    wfh_log_path: Optional[Path] = None
    catalog_only_mode: bool = False
```

### 📝 Usage Examples

**Catalog Only**:
```bash
python invoice_cataloger.py --catalog-only --financial-year 2024-2025
```

**Full Process (Catalog + Tax)**:
```bash
python invoice_cataloger.py --financial-year 2024-2025
```

**With WFH Log**:
```bash
python invoice_cataloger.py --financial-year 2024-2025 --wfh-log wfh_log.csv
```

**Standalone Tax Calculator**:
```bash
python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --output tax_report.csv
```

### ✅ Testing Phase 4
- Test `--catalog-only` flag
- Test standalone tax calculator
- Test `--wfh-log` integration
- Test `--tax-strategy` option
- Test backward compatibility (no flags)

---

## Phase 5: Documentation

### 🎯 Goal
Comprehensive documentation for new architecture and usage.

### 📁 Files to Create

#### 1. Update `README.md`

**Add sections**:
- New Architecture Overview
- Two-Phase Process (Catalog → Tax)
- SOLID Principles Applied
- Usage Examples
- CLI Reference
- WFH Log Format
- Custom Tax Strategies

**Example Structure**:
```markdown
# Invoice Cataloger - SOLID & DRY Refactored

## Architecture

### Two-Phase Process
1. **Phase 1: Catalog** - Extract and categorize invoices
2. **Phase 2: Tax** - Calculate deductions using pluggable strategies

### SOLID Principles
- Single Responsibility: Each module has one clear purpose
- Open/Closed: Extend with new strategies without modifying code
- ...

## Usage

### Catalog Only
\`\`\`bash
python invoice_cataloger.py --catalog-only
\`\`\`

### Full Process
\`\`\`bash
python invoice_cataloger.py --financial-year 2024-2025
\`\`\`

### With WFH Log
\`\`\`bash
python invoice_cataloger.py --wfh-log wfh_log.csv
\`\`\`
```

#### 2. Create `WFH_LOG_GUIDE.md`

**Content**:
- WFH log purpose and benefits
- CSV format specification
- JSON format specification
- Example files
- Date range filtering
- Financial year filtering
- Calculation examples
- Troubleshooting

**Example**:
```markdown
# Work From Home (WFH) Log Guide

## Purpose
Calculate dynamic work-use percentage based on actual WFH days.

## CSV Format
\`\`\`csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
\`\`\`

## Calculation
\`\`\`
WFH Percentage = (WFH Days / Total Work Days) × 100
\`\`\`

## Usage
\`\`\`bash
python invoice_cataloger.py --wfh-log wfh_log.csv
\`\`\`
```

#### 3. Create `TAX_STRATEGY_GUIDE.md`

**Content**:
- Strategy Pattern explanation
- ATO strategy details
- Creating custom strategies
- Rule JSON format
- Examples

**Example**:
```markdown
# Tax Strategy Guide

## Strategy Pattern
The system uses the Strategy Pattern for pluggable tax calculations.

## ATO Strategy
Australian Taxation Office compliant calculations.

### Rules Location
\`tax/rules/ato_rules.json\`

### Supported Categories
- Electricity
- Internet
- Software & Subscriptions
- ...

## Creating Custom Strategies

\`\`\`python
from tax.strategies import TaxStrategy

class CustomStrategy(TaxStrategy):
    def calculate_deduction(self, invoice_data, category, work_use_pct):
        # Your logic here
        pass
    
    def get_strategy_name(self):
        return "Custom"
\`\`\`
```

#### 4. Create `MIGRATION_GUIDE.md`

**Content**:
- Changes from old to new system
- Before/after examples
- Backward compatibility notes
- Migration checklist
- Troubleshooting

**Example**:
```markdown
# Migration Guide

## What Changed

### Old System (Monolithic)
- Everything in one process
- Tax calculations hardcoded
- No separation of concerns

### New System (Modular)
- Catalog and tax are separate
- Pluggable tax strategies
- SOLID principles applied

## Backward Compatibility
The system maintains backward compatibility. Running without flags works as before:
\`\`\`bash
python invoice_cataloger.py --financial-year 2024-2025
\`\`\`

## New Features
- \`--catalog-only\` - Catalog without tax
- \`--wfh-log\` - Dynamic work-use %
- \`--tax-strategy\` - Choose strategy
```

#### 5. Create `API_DOCUMENTATION.md`

**Content**:
- Catalog module API
- Tax module API
- WFH module API
- Code examples
- Type hints

### ✅ Testing Phase 5
- Review all documentation for accuracy
- Test all code examples
- Verify links work
- Check formatting

---

## Phase 6: Full Testing & Validation

### 🎯 Goal
Comprehensive testing of entire refactored system.

### 📝 Testing Checklist

#### Unit Tests

**Catalog Module**:
- [ ] Test InvoiceCataloger initialization
- [ ] Test file extraction (PDF, images, documents)
- [ ] Test LLM processing
- [ ] Test categorization
- [ ] Test export (CSV, Excel, JSON)
- [ ] Test loading (CSV, Excel, JSON)
- [ ] Test validation

**Tax Module**:
- [ ] Test base strategy interface
- [ ] Test ATO strategy calculations
- [ ] Test rule loader
- [ ] Test rule validation
- [ ] Test threshold logic
- [ ] Test depreciation calculations
- [ ] Test work-use percentage calculations

**WFH Module**:
- [ ] Test CSV parsing
- [ ] Test JSON parsing
- [ ] Test date filtering
- [ ] Test percentage calculation
- [ ] Test report generation

#### Integration Tests

- [ ] Test catalog → tax workflow
- [ ] Test catalog-only mode
- [ ] Test with WFH log
- [ ] Test with different strategies
- [ ] Test error handling
- [ ] Test edge cases

#### End-to-End Tests

- [ ] Test full workflow with real invoices
- [ ] Test with various file types
- [ ] Test with WFH log
- [ ] Test export formats
- [ ] Test CLI commands

#### Performance Tests

- [ ] Benchmark catalog-only mode
- [ ] Benchmark tax calculation
- [ ] Compare with legacy system
- [ ] Test with large datasets (100+ invoices)

#### Validation Tests

- [ ] Verify SOLID principles applied
- [ ] Verify DRY principle applied
- [ ] Verify no code duplication
- [ ] Verify backward compatibility
- [ ] Code review

### 📝 Test Execution

**Run existing test suite**:
```bash
python invoice_cataloger/test_catalog_module.py
```

**Create additional test files**:
- `test_tax_module.py` - Test tax strategies
- `test_wfh_module.py` - Test WFH integration
- `test_integration.py` - Integration tests
- `test_end_to_end.py` - E2E tests

**Example Test Structure**:
```python
class TestTaxModule:
    def test_ato_strategy_initialization(self):
        strategy = ATOStrategy()
        assert strategy.get_strategy_name() == "ATO"
    
    def test_calculate_deduction_electricity(self):
        strategy = ATOStrategy()
        invoice_data = {'total': 100.00}
        deduction = strategy.calculate_deduction(
            invoice_data, 'Electricity', 60
        )
        assert deduction['DeductibleAmount'] == 60.00
    
    # ... more tests
```

### ✅ Success Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Performance is acceptable
- [ ] SOLID principles verified
- [ ] DRY principle verified
- [ ] Backward compatibility confirmed
- [ ] Documentation is complete and accurate

---

## 📊 Progress Tracking

Use `REFACTORING_TODO.md` to track progress:

```markdown
### Phase 3: WFH Integration ⏳ IN PROGRESS
- [x] 1/6 tasks completed
  - [x] Create WFH module structure
  - [ ] Implement WFH parser
  - [ ] Implement WFH calculator
  - [ ] Integrate with tax calculator
  - [ ] Create example files
  - [ ] Testing

### Phase 4: CLI Updates ⏸️ PENDING
- [ ] 0/5 tasks completed
```

---

## 🎯 Key Principles to Maintain

Throughout Phases 3-6, maintain:

1. **SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

2. **DRY Principle**
   - No code duplication
   - Reusable components
   - Shared helper methods

3. **Clean Code**
   - Clear naming
   - Comprehensive docstrings
   - Type hints
   - Error handling

4. **Testing**
   - Test as you go
   - Comprehensive coverage
   - Edge cases

5. **Documentation**
   - Document as you code
   - Clear examples
   - Usage guides

---

## 📞 Support

If you encounter issues:
1. Check existing documentation
2. Review test files for examples
3. Check `REFACTORING_TODO.md` for context
4. Review `REFACTORING_COMPLETE.md` for architecture

---

## ✅ Final Checklist

Before considering the refactoring complete:

- [ ] All 6 phases implemented
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Examples working
- [ ] Backward compatibility verifieThe user wants me to create instructions and context for the remaining phases (3-6). Let me create a comprehensive guide for completing the remaining phases of the refactoring.

<create_file>
