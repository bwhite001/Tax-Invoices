# Phase 4: CLI Refactoring - Breaking Up invoice_cataloger.py

## 🎯 Goal
Refactor the monolithic `invoice_cataloger.py` (900+ lines) into smaller, more manageable modules following SOLID principles, with CLI as a clean entrypoint.

## 📊 Current Status

### ✅ Completed:
1. **Created `core/` module structure**
   - `core/__init__.py` - Module initialization
   - `core/prerequisite_checker.py` (200+ lines) - System validation
   - `core/file_processor.py` (500+ lines) - File processing logic

### ⏳ Remaining Tasks:

#### 1. Create `core/cataloger_service.py`
**Purpose**: Main service orchestrator (replaces InvoiceCataloger class)

**Responsibilities**:
- Coordinate file scanning
- Manage processing workflow
- Handle statistics and reporting
- Export results

**Key Methods**:
```python
class CatalogerService:
    def __init__(self, config: Config)
    def get_invoice_files(self, retry_failed: bool) -> List[Path]
    def process_all_files(self, files: List[Path], reprocess: bool) -> List[Dict]
    def export_results(self, processed_invoices: List[Dict])
    def generate_summary(self, processed_invoices: List[Dict]) -> Dict
    def cleanup_non_invoices(self, dry_run: bool) -> tuple[int, int]
```

#### 2. Create `cli/` module
**Purpose**: Clean CLI entrypoint separated from business logic

**Files to create**:
- `cli/__init__.py`
- `cli/invoice_cataloger_cli.py` - Main CLI (replaces current main())
- `cli/argument_parser.py` - CLI argument parsing
- `cli/command_handlers.py` - Command execution handlers

**Structure**:
```python
# cli/invoice_cataloger_cli.py
def main():
    args = parse_arguments()
    config = create_config(args)
    
    if args.check_only:
        handle_check_command(config)
    elif args.cleanup_non_invoices:
        handle_cleanup_command(config, args)
    elif args.catalog_only:
        handle_catalog_only_command(config, args)
    else:
        handle_full_process_command(config, args)
```

#### 3. Update `invoice_cataloger.py`
**New role**: Thin wrapper/compatibility layer

```python
#!/usr/bin/env python3
"""
Invoice Cataloger - Main Entry Point

This is a thin wrapper around the CLI for backward compatibility.
For new code, use: from cli import main
"""
from cli.invoice_cataloger_cli import main

if __name__ == '__main__':
    main()
```

## 📁 New Project Structure

```
invoice_cataloger/
├── cli/                          # NEW: CLI layer
│   ├── __init__.py
│   ├── invoice_cataloger_cli.py  # Main CLI entrypoint
│   ├── argument_parser.py        # Argument parsing
│   └── command_handlers.py       # Command execution
│
├── core/                         # NEW: Core business logic
│   ├── __init__.py
│   ├── cataloger_service.py      # Main service orchestrator
│   ├── file_processor.py         # ✅ File processing logic
│   └── prerequisite_checker.py   # ✅ System validation
│
├── catalog/                      # Existing: Catalog module
├── tax/                          # Existing: Tax module
├── extractors/                   # Existing: Text extraction
├── processors/                   # Existing: LLM & categorization
├── exporters/                    # Existing: Export functionality
├── utils/                        # Existing: Utilities
│
├── invoice_cataloger.py          # UPDATED: Thin wrapper
├── tax_calculator_cli.py         # Existing: Standalone tax CLI
└── config.py                     # Existing: Configuration
```

## 🎯 Benefits of Refactoring

### 1. **Single Responsibility Principle (SRP)**
- **PrerequisiteChecker**: Only validates system requirements
- **FileProcessor**: Only processes individual files
- **CatalogerService**: Only orchestrates the workflow
- **CLI**: Only handles command-line interface

### 2. **Improved Testability**
- Each module can be tested independently
- Mock dependencies easily
- Unit tests are simpler and focused

### 3. **Better Maintainability**
- Smaller files are easier to understand
- Changes are localized to specific modules
- Reduced cognitive load

### 4. **Reusability**
- Core modules can be imported and used programmatically
- CLI is just one interface to the core functionality
- Easy to add web API, GUI, or other interfaces

### 5. **Cleaner Dependencies**
- Clear separation between CLI and business logic
- Core modules don't depend on CLI
- Easier to track and manage dependencies

## 📝 Implementation Steps

### Step 1: Create `core/cataloger_service.py`
```python
class CatalogerService:
    """Main service for invoice cataloging"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.file_processor = FileProcessor(config)
        self.prerequisite_checker = PrerequisiteChecker(config)
        # ... initialize exporters, managers, etc.
    
    def run(self, retry_failed: bool = False, reprocess: bool = False):
        """Main processing workflow"""
        # Check prerequisites
        if not self.prerequisite_checker.check_all():
            return False
        
        # Get files
        files = self.get_invoice_files(retry_failed)
        
        # Process files
        results = self.process_all_files(files, reprocess)
        
        # Export results
        self.export_results(results)
        
        # Generate summary
        summary = self.generate_summary(results)
        
        return True
```

### Step 2: Create CLI Module
```python
# cli/invoice_cataloger_cli.py
def main():
    """Main CLI entrypoint"""
    args = ArgumentParser().parse()
    config = Config()
    config.financial_year = args.financial_year
    
    setup_logger(config.log_folder, 'DEBUG' if args.verbose else 'INFO')
    
    # Route to appropriate handler
    if args.check_only:
        CheckCommandHandler(config).execute()
    elif args.cleanup_non_invoices:
        CleanupCommandHandler(config, args).execute()
    elif args.catalog_only:
        CatalogOnlyCommandHandler(config, args).execute()
    else:
        FullProcessCommandHandler(config, args).execute()
```

### Step 3: Create Command Handlers
```python
# cli/command_handlers.py
class CommandHandler:
    """Base command handler"""
    def __init__(self, config: Config):
        self.config = config
        self.service = CatalogerService(config)
    
    def execute(self):
        raise NotImplementedError

class FullProcessCommandHandler(CommandHandler):
    """Handle full processing workflow"""
    def __init__(self, config: Config, args):
        super().__init__(config)
        self.args = args
    
    def execute(self):
        self.service.run(
            retry_failed=self.args.retry_failed,
            reprocess=self.args.reprocess
        )
```

### Step 4: Update `invoice_cataloger.py`
```python
#!/usr/bin/env python3
"""
Invoice Cataloger - Main Entry Point

Thin wrapper for backward compatibility.
"""
from cli.invoice_cataloger_cli import main

if __name__ == '__main__':
    main()
```

## ✅ Testing Strategy

### Unit Tests
- Test each core module independently
- Mock dependencies
- Test edge cases

### Integration Tests
- Test CLI argument parsing
- Test command handlers
- Test service orchestration

### End-to-End Tests
- Test full workflow
- Test with real files
- Test all CLI commands

## 📈 Migration Path

### Phase 1: Create Core Modules ✅ (Partially Complete)
- [x] Create `core/` directory
- [x] Create `prerequisite_checker.py`
- [x] Create `file_processor.py`
- [ ] Create `cataloger_service.py`

### Phase 2: Create CLI Module
- [ ] Create `cli/` directory
- [ ] Create `invoice_cataloger_cli.py`
- [ ] Create `argument_parser.py`
- [ ] Create `command_handlers.py`

### Phase 3: Update Main File
- [ ] Update `invoice_cataloger.py` to thin wrapper
- [ ] Test backward compatibility
- [ ] Update documentation

### Phase 4: Testing
- [ ] Create unit tests for core modules
- [ ] Create integration tests for CLI
- [ ] Run end-to-end tests
- [ ] Performance testing

## 🎯 Success Criteria

- [ ] All core logic moved to `core/` modules
- [ ] CLI is clean and focused on interface
- [ ] Each module has single responsibility
- [ ] All existing functionality works
- [ ] Backward compatibility maintained
- [ ] Tests pass
- [ ] Documentation updated

## 📝 Next Steps

1. **Complete `core/cataloger_service.py`**
   - Move workflow orchestration logic
   - Move file scanning logic
   - Move export logic
   - Move statistics generation

2. **Create CLI module**
   - Implement argument parser
   - Implement command handlers
   - Implement main CLI entrypoint

3. **Update main file**
   - Convert to thin wrapper
   - Test backward compatibility

4. **Testing & Documentation**
   - Create comprehensive tests
   - Update all documentation
   - Create migration guide

---

**Status**: 🔄 Phase 4 In Progress | Core modules partially complete
**Next**: Complete `cataloger_service.py` and create CLI module
