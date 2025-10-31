# Invoice Cataloger - SOLID & DRY Refactoring TODO

## 🎯 Refactoring Goals
- Separate invoice cataloging from tax calculation
- Apply SOLID principles (Single Responsibility, Open/Closed, Dependency Inversion)
- Apply DRY principle (Don't Repeat Yourself)
- Make tax rules configurable and pluggable
- Support WFH log integration for dynamic work-use percentage
- Maintain backward compatibility

---

## Phase 1: Separate Invoice Cataloging from Tax Calculation

### Goal
Create independent catalog module that extracts and categorizes invoices WITHOUT tax calculations.

### Tasks

#### 1.1 Create Catalog Module Structure
- [ ] Create `catalog/` directory
- [ ] Create `catalog/__init__.py`
- [ ] Create `catalog/cataloger.py` - Pure invoice cataloging
- [ ] Create `catalog/catalog_exporter.py` - Export catalog without tax data
- [ ] Create `catalog/catalog_loader.py` - Load existing catalogs

#### 1.2 Implement Pure Cataloger
- [ ] Extract cataloging logic from `invoice_cataloger.py`
- [ ] Remove tax calculation dependencies
- [ ] Keep: extraction, LLM processing, categorization
- [ ] Remove: deduction calculation, tax-related fields
- [ ] Export catalog with: FileName, Vendor, Date, Amount, Category, etc.

#### 1.3 Implement Catalog Exporter
- [ ] Create CSV export without tax fields
- [ ] Create Excel export without tax fields
- [ ] Include: invoice metadata, amounts, categories
- [ ] Exclude: deduction amounts, claim methods, ATO references

#### 1.4 Implement Catalog Loader
- [ ] Load catalog from CSV
- [ ] Load catalog from Excel
- [ ] Validate catalog structure
- [ ] Return list of invoice records

#### 1.5 Testing
- [ ] Test catalog-only mode
- [ ] Verify no tax calculations in catalog
- [ ] Test catalog export formats
- [ ] Test catalog loading

---

## Phase 2: Pluggable Tax Calculation System

### Goal
Create modular tax calculation system with Strategy Pattern and configurable rules.

### Tasks

#### 2.1 Create Tax Module Structure
- [ ] Create `tax/` directory
- [ ] Create `tax/__init__.py`
- [ ] Create `tax/strategies/` directory
- [ ] Create `tax/strategies/__init__.py`
- [ ] Create `tax/rules/` directory
- [ ] Create `tax/rules/__init__.py`

#### 2.2 Implement Base Strategy (Abstract)
- [ ] Create `tax/strategies/base_strategy.py`
- [ ] Define abstract `TaxStrategy` class
- [ ] Define `calculate_deduction()` abstract method
- [ ] Define `get_strategy_name()` method
- [ ] Define `validate_rules()` method

#### 2.3 Implement ATO Strategy
- [ ] Create `tax/strategies/ato_strategy.py`
- [ ] Move logic from `processors/deduction_calculator.py`
- [ ] Load rules from JSON instead of hardcoded
- [ ] Support dynamic work-use percentage
- [ ] Implement all ATO category rules

#### 2.4 Create ATO Rules Configuration
- [ ] Create `tax/rules/ato_rules.json`
- [ ] Define rules for each category:
  - Electricity
  - Internet
  - Phone & Mobile
  - Software & Subscriptions
  - Computer Equipment
  - Professional Development
  - Professional Membership
  - Office Supplies
  - Communication Tools
  - Other
- [ ] Include: claim_method, work_use_applicable, threshold, depreciation_years, ato_reference

#### 2.5 Implement Rule Loader
- [ ] Create `tax/rules/rule_loader.py`
- [ ] Load rules from JSON
- [ ] Validate rule structure
- [ ] Support custom rule files
- [ ] Cache loaded rules

#### 2.6 Implement Rule Schema
- [ ] Create `tax/rules/rule_schema.json`
- [ ] Define JSON schema for validation
- [ ] Validate required fields
- [ ] Validate data types

#### 2.7 Implement Custom Strategy
- [ ] Create `tax/strategies/custom_strategy.py`
- [ ] Support user-defined rules
- [ ] Load from custom JSON file
- [ ] Allow rule overrides

#### 2.8 Implement Tax Calculator
- [ ] Create `tax/tax_calculator.py`
- [ ] Load catalog from CSV/Excel
- [ ] Select tax strategy (ATO, custom)
- [ ] Calculate deductions for all invoices
- [ ] Export tax report with deductions
- [ ] Support batch processing

#### 2.9 Deprecate Old Deduction Calculator
- [ ] Add deprecation warning to `processors/deduction_calculator.py`
- [ ] Redirect to new `tax/strategies/ato_strategy.py`
- [ ] Keep for backward compatibility
- [ ] Update documentation

#### 2.10 Testing
- [ ] Test ATO strategy with static work-use %
- [ ] Test custom strategy
- [ ] Test rule loading and validation
- [ ] Test tax calculator with catalog
- [ ] Test backward compatibility

---

## Phase 3: WFH Log Integration

### Goal
Support dynamic work-use percentage based on actual WFH days from log files.

### Tasks

#### 3.1 Create WFH Module Structure
- [ ] Create `tax/wfh/` directory
- [ ] Create `tax/wfh/__init__.py`
- [ ] Create `tax/wfh/wfh_parser.py`
- [ ] Create `tax/wfh/wfh_calculator.py`

#### 3.2 Design WFH Log Formats
- [ ] Define CSV format specification
- [ ] Define JSON format specification
- [ ] Create example WFH log files
- [ ] Document format requirements

#### 3.3 Implement WFH Parser
- [ ] Parse CSV format
- [ ] Parse JSON format
- [ ] Validate date formats
- [ ] Validate required fields
- [ ] Handle missing data
- [ ] Support date range filtering

#### 3.4 Implement WFH Calculator
- [ ] Calculate total WFH days
- [ ] Calculate total work days
- [ ] Calculate work-use percentage
- [ ] Support date range calculations
- [ ] Support financial year filtering
- [ ] Generate WFH statistics report

#### 3.5 Integrate with Tax Calculator
- [ ] Accept optional WFH log path
- [ ] Calculate dynamic work-use percentage
- [ ] Override config default if WFH log provided
- [ ] Pass to tax strategy
- [ ] Include WFH stats in tax report

#### 3.6 Testing
- [ ] Test CSV parsing
- [ ] Test JSON parsing
- [ ] Test WFH percentage calculation
- [ ] Test date range filtering
- [ ] Test integration with tax calculator
- [ ] Test with missing WFH log (fallback to config)

---

## Phase 4: CLI & Configuration Updates

### Goal
Update CLI and configuration to support new architecture while maintaining backward compatibility.

### Tasks

#### 4.1 Update Configuration
- [ ] Add `tax_strategy` field to `config.py`
- [ ] Add `tax_rules_path` field
- [ ] Add `wfh_log_path` field
- [ ] Add `catalog_only_mode` field
- [ ] Create `tax/rules/tax_config.json` for user settings
- [ ] Update `validate_api_config()` method
- [ ] Update `to_dict()` method

#### 4.2 Update Main CLI
- [ ] Add `--catalog-only` flag to `invoice_cataloger.py`
- [ ] Add `--tax-strategy` option (ato, custom)
- [ ] Add `--wfh-log` option
- [ ] Add `--tax-rules` option for custom rules
- [ ] Update help text
- [ ] Maintain backward compatibility (default: full process)

#### 4.3 Create Tax Calculator CLI
- [ ] Create `tax_calculator.py` (standalone script)
- [ ] Add `--catalog` argument (required)
- [ ] Add `--wfh-log` argument (optional)
- [ ] Add `--strategy` argument (default: ato)
- [ ] Add `--rules` argument for custom rules
- [ ] Add `--output` argument for tax report
- [ ] Add `--financial-year` argument

#### 4.4 Update Invoice Cataloger Main
- [ ] Refactor `run()` method to support catalog-only mode
- [ ] Use new `catalog.cataloger` module
- [ ] Conditionally run tax calculation
- [ ] Support legacy mode (full process)
- [ ] Update statistics and reporting

#### 4.5 Testing
- [ ] Test `--catalog-only` mode
- [ ] Test standalone tax calculator
- [ ] Test `--wfh-log` integration
- [ ] Test custom tax strategy
- [ ] Test backward compatibility (no flags)
- [ ] Test all CLI combinations

---

## Phase 5: Documentation & Examples

### Goal
Comprehensive documentation for new architecture and usage.

### Tasks

#### 5.1 Update README
- [ ] Document new architecture
- [ ] Explain two-phase process
- [ ] Document catalog-only mode
- [ ] Document tax calculator usage
- [ ] Document WFH log format
- [ ] Document custom tax strategies
- [ ] Add usage examples

#### 5.2 Create WFH Log Guide
- [ ] Create `WFH_LOG_GUIDE.md`
- [ ] Document CSV format
- [ ] Document JSON format
- [ ] Provide example files
- [ ] Explain date range filtering
- [ ] Show calculation examples

#### 5.3 Create Tax Strategy Guide
- [ ] Create `TAX_STRATEGY_GUIDE.md`
- [ ] Explain Strategy Pattern
- [ ] Document ATO strategy
- [ ] Document custom strategy creation
- [ ] Provide rule JSON examples
- [ ] Show how to extend

#### 5.4 Create Migration Guide
- [ ] Create `MIGRATION_GUIDE.md`
- [ ] Explain changes from old to new
- [ ] Show before/after examples
- [ ] Document backward compatibility
- [ ] Provide migration checklist

#### 5.5 Update API Documentation
- [ ] Document catalog module API
- [ ] Document tax module API
- [ ] Document WFH module API
- [ ] Add code examples
- [ ] Add type hints

#### 5.6 Create Example Files
- [ ] Create `examples/wfh_log.csv`
- [ ] Create `examples/wfh_log.json`
- [ ] Create `examples/custom_tax_rules.json`
- [ ] Create `examples/usage_examples.sh`

---

## Phase 6: Testing & Validation

### Goal
Comprehensive testing of refactored system.

### Tasks

#### 6.1 Unit Tests
- [ ] Test catalog module
- [ ] Test tax strategies
- [ ] Test WFH parser
- [ ] Test WFH calculator
- [ ] Test rule loader
- [ ] Test catalog loader

#### 6.2 Integration Tests
- [ ] Test catalog-only workflow
- [ ] Test tax calculation workflow
- [ ] Test WFH log integration
- [ ] Test custom strategy
- [ ] Test backward compatibility

#### 6.3 End-to-End Tests
- [ ] Test full workflow (catalog → tax)
- [ ] Test with real invoice files
- [ ] Test with WFH log
- [ ] Test with custom rules
- [ ] Test error handling

#### 6.4 Performance Tests
- [ ] Benchmark catalog-only mode
- [ ] Benchmark tax calculation
- [ ] Compare with legacy system
- [ ] Optimize bottlenecks

#### 6.5 Validation
- [ ] Verify SOLID principles applied
- [ ] Verify DRY principle applied
- [ ] Verify backward compatibility
- [ ] Verify all features working
- [ ] Code review

---

## Progress Tracking

### Phase 1: Catalog Module ✅ COMPLETE
- [x] 5/5 tasks completed
  - [x] Create catalog module structure
  - [x] Implement pure cataloger (cataloger.py)
  - [x] Implement catalog exporter (catalog_exporter.py)
  - [x] Implement catalog loader (catalog_loader.py)
  - [x] All catalog files created and functional

### Phase 2: Tax System ⏳ IN PROGRESS
- [ ] 0/10 tasks completed

### Phase 3: WFH Integration ⏸️ PENDING
- [ ] 0/6 tasks completed

### Phase 4: CLI Updates ⏸️ PENDING
- [ ] 0/5 tasks completed

### Phase 5: Documentation ⏸️ PENDING
- [ ] 0/6 tasks completed

### Phase 6: Testing ⏸️ PENDING
- [ ] 0/5 tasks completed

---

## Notes

- Maintain backward compatibility throughout
- Each phase should be independently testable
- Focus on clean, maintainable code
- Follow SOLID and DRY principles
- Document as we go
- Test thoroughly before moving to next phase

---

## Design Patterns Used

1. **Strategy Pattern**: Tax calculation strategies (ATO, custom)
2. **Factory Pattern**: Tax strategy factory
3. **Repository Pattern**: Catalog loader/exporter
4. **Dependency Injection**: Tax calculator receives strategy
5. **Single Responsibility**: Each module has one clear purpose
6. **Open/Closed**: Extend with new strategies without modifying existing code

---

## Architecture Diagram

```
OLD ARCHITECTURE:
File → Extract → LLM → Categorize → Calculate Tax → Export
(All in one monolithic process)

NEW ARCHITECTURE:
PHASE 1: CATALOG
File → Extract → LLM → Categorize → Export Catalog

PHASE 2: TAX CALCULATION
Catalog → Load → Apply Strategy → Calculate → Export Tax Report
                    ↓
                WFH Log (optional)
