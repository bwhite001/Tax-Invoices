# Implementation Plan: Phases 3-6

## 📊 Current Project Status

### ✅ Completed (Phases 1-2):
- **Phase 1**: Catalog Module
  - `catalog/cataloger.py` - Pure invoice cataloging
  - `catalog/catalog_exporter.py` - Export without tax fields
  - `catalog/catalog_loader.py` - Load catalogs
  
- **Phase 2**: Tax Calculation System
  - `tax/strategies/base_strategy.py` - Abstract base class
  - `tax/strategies/ato_strategy.py` - ATO implementation
  - `tax/rules/rule_loader.py` - Load and validate rules
  - `tax/rules/ato_rules.json` - Externalized ATO rules

### 🎯 To Be Implemented (Phases 3-6):
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
"""
from .wfh_parser import WFHParser
from .wfh_calculator import WFHCalculator

__all__ = ['WFHParser', 'WFHCalculator']
```

#### 2. `tax/wfh/wfh_parser.py`
**Purpose**: Parse WFH logs from CSV or JSON files

**Key Features**:
- Parse CSV format (Date, Location, WorkFromHome, Notes)
- Parse JSON format (financial_year, entries array)
- Validate date formats (YYYY-MM-DD)
- Handle missing or invalid data gracefully
- Support both boolean and string values for WFH field
- Filter by date range
- Filter by financial year

**CSV Format**:
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
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

#### 3. `tax/wfh/wfh_calculator.py`
**Purpose**: Calculate work-use percentage from WFH logs

**Key Features**:
- Calculate WFH percentage: (WFH Days / Total Work Days) × 100
- Count WFH days
- Count total work days
- Generate statistics report
- Monthly breakdown

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
```

#### 4. `tax/tax_calculator.py` (Main Orchestrator)
**Purpose**: Main tax calculator that orchestrates everything

**Key Features**:
- Initialize with strategy and optional WFH log
- Calculate deductions for all catalog entries
- Export tax report with deductions
- Support dynamic work-use percentage from WFH log
- Fallback to config default if no WFH log

**Integration**:
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

#### 5. Example WFH Log Files

**`examples/wfh_log.csv`**:
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
2024-07-03,Home,Yes,Full day WFH
2024-07-04,Home,Yes,Full day WFH
2024-07-05,Office,No,In office
```

**`examples/wfh_log.json`**:
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
- [ ] Test CSV parsing with valid files
- [ ] Test CSV parsing with invalid files
- [ ] Test JSON parsing with valid files
- [ ] Test JSON parsing with invalid files
- [ ] Test date range filtering
- [ ] Test financial year filtering
- [ ] Test percentage calculation
- [ ] Test with missing WFH log (fallback to config default)
- [ ] Test integration with tax calculator

---

## Phase 4: CLI Updates

### 🎯 Goal
Update CLI to support new architecture with catalog-only mode and standalone tax calculator.

### 📁 Files to Create/Modify

#### 1. Create `tax_calculator_cli.py` (Standalone Script)
**Purpose**: Standalone CLI for tax calculation

**Features**:
- Load catalog from CSV, Excel, or JSON
- Select tax strategy (ATO, custom)
- Optional WFH log for dynamic work-use %
- Optional static work-use percentage
- Export tax report

**Usage Examples**:
```bash
# Basic usage
python tax_calculator_cli.py --catalog catalog.csv --output tax_report.csv

# With WFH log
python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --output tax_report.csv

# With static work-use percentage
python tax_calculator_cli.py --catalog catalog.csv --work-use-percentage 65 --output tax_report.csv

# With custom strategy
python tax_calculator_cli.py --catalog catalog.csv --strategy custom --output tax_report.csv
```

#### 2. Modify `invoice_cataloger.py`

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
- Support catalog-only mode
- Conditionally run tax calculation
- Integrate WFH log if provided
- Maintain backward compatibility

**Usage Examples**:
```bash
# Catalog only (no tax calculations)
python invoice_cataloger.py --catalog-only --financial-year 2024-2025

# Full process (catalog + tax) - backward compatible
python invoice_cataloger.py --financial-year 2024-2025

# With WFH log
python invoice_cataloger.py --financial-year 2024-2025 --wfh-log wfh_log.csv

# With custom strategy
python invoice_cataloger.py --financial-year 2024-2025 --tax-strategy custom
```

#### 3. Update `config.py`

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

### ✅ Testing Phase 4
- [ ] Test `--catalog-only` flag
- [ ] Test standalone tax calculator with CSV catalog
- [ ] Test standalone tax calculator with Excel catalog
- [ ] Test standalone tax calculator with JSON catalog
- [ ] Test `--wfh-log` integration
- [ ] Test `--tax-strategy` option
- [ ] Test backward compatibility (no flags)
- [ ] Test all CLI combinations

---

## Phase 5: Documentation

### 🎯 Goal
Comprehensive documentation for new architecture and usage.

### 📁 Files to Create/Update

#### 1. Update `README.md`

**Add sections**:
- New Architecture Overview
- Two-Phase Process (Catalog → Tax)
- SOLID Principles Applied
- Usage Examples
- CLI Reference
- WFH Log Format
- Custom Tax Strategies

**Structure**:
```markdown
# Invoice Cataloger - SOLID & DRY Refactored

## 🏗️ Architecture

### Two-Phase Process
1. **Phase 1: Catalog** - Extract and categorize invoices
2. **Phase 2: Tax** - Calculate deductions using pluggable strategies

### SOLID Principles
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extend with new strategies without modifying code
- **Liskov Substitution**: All strategies are interchangeable
- **Interface Segregation**: Clean, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not implementations

## 📖 Usage

### Catalog Only
\`\`\`bash
python invoice_cataloger.py --catalog-only --financial-year 2024-2025
\`\`\`

### Full Process (Catalog + Tax)
\`\`\`bash
python invoice_cataloger.py --financial-year 2024-2025
\`\`\`

### With WFH Log
\`\`\`bash
python invoice_cataloger.py --financial-year 2024-2025 --wfh-log wfh_log.csv
\`\`\`

### Standalone Tax Calculator
\`\`\`bash
python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --output tax_report.csv
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

#### 3. Create `TAX_STRATEGY_GUIDE.md`

**Content**:
- Strategy Pattern explanation
- ATO strategy details
- Creating custom strategies
- Rule JSON format
- Examples

#### 4. Create `MIGRATION_GUIDE.md`

**Content**:
- Changes from old to new system
- Before/after examples
- Backward compatibility notes
- Migration checklist
- Troubleshooting

#### 5. Create `API_DOCUMENTATION.md`

**Content**:
- Catalog module API
- Tax module API
- WFH module API
- Code examples
- Type hints

### ✅ Testing Phase 5
- [ ] Review all documentation for accuracy
- [ ] Test all code examples
- [ ] Verify links work
- [ ] Check formatting
- [ ] Ensure examples are up-to-date

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
- [ ] Test error handling

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

### 📝 Test Files to Create

- `test_wfh_module.py` - Test WFH integration
- `test_tax_calculator.py` - Test tax calculator orchestrator
- `test_integration.py` - Integration tests
- `test_end_to_end.py` - E2E tests
- `test_cli.py` - CLI tests

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

## 📊 Implementation Order

### Step 1: Phase 3 - WFH Integration (Priority: HIGH)
1. Create `tax/wfh/` directory structure
2. Implement `wfh_parser.py`
3. Implement `wfh_calculator.py`
4. Create `tax/tax_calculator.py` (orchestrator)
5. Create example WFH log files
6. Test WFH module

### Step 2: Phase 4 - CLI Updates (Priority: HIGH)
1. Create `tax_calculator_cli.py` (standalone)
2. Update `config.py` with new fields
3. Modify `invoice_cataloger.py` for catalog-only mode
4. Test all CLI combinations
5. Verify backward compatibility

### Step 3: Phase 5 - Documentation (Priority: MEDIUM)
1. Update `README.md`
2. Create `WFH_LOG_GUIDE.md`
3. Create `TAX_STRATEGY_GUIDE.md`
4. Create `MIGRATION_GUIDE.md`
5. Create `API_DOCUMENTATION.md`
6. Review and test all examples

### Step 4: Phase 6 - Testing (Priority: HIGH)
1. Create test files
2. Run unit tests
3. Run integration tests
4. Run E2E tests
5. Performance testing
6. Final validation

---

## 🎯 Key Principles to Maintain

Throughout implementation:

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

## 📞 Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Start with Phase 3** - WFH integration is foundational
3. **Proceed sequentially** - Each phase builds on the previous
4. **Test continuously** - Don't wait until Phase 6
5. **Document as you go** - Keep documentation up-to-date

---

## ✅ Final Checklist

Before considering the refactoring complete:

- [ ] All 6 phases implemented
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Examples working
- [ ] Backward compatibility verified
- [ ] Performance acceptable
- [ ] Code review complete
- [ ] SOLID/DRY principles verified

---

**Status**: 📋 Plan Created | ⏳ Ready to Start Implementation
