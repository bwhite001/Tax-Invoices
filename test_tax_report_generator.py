"""
Test Script for Tax Report Generator

Quick test to verify the system is properly installed and configured.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from tax_report_generator.config import Config, FilePaths, TaxParameters, ReportConfig
        from tax_report_generator.wfh_processor import WFHProcessor
        from tax_report_generator.invoice_processor import InvoiceProcessor
        from tax_report_generator.bank_processor import BankProcessor
        from tax_report_generator.report_generator import ReportGenerator
        from tax_report_generator.main import TaxReportGenerator
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_dependencies():
    """Test that required dependencies are installed"""
    print("\nTesting dependencies...")
    missing = []
    
    try:
        import pandas
        print(f"✓ pandas {pandas.__version__}")
    except ImportError:
        missing.append("pandas")
        print("❌ pandas not installed")
    
    try:
        import openpyxl
        print(f"✓ openpyxl {openpyxl.__version__}")
    except ImportError:
        missing.append("openpyxl")
        print("❌ openpyxl not installed")
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r tax_report_generator/requirements.txt")
        return False
    
    return True


def test_configuration():
    """Test configuration creation"""
    print("\nTesting configuration...")
    try:
        from tax_report_generator.config import Config
        
        config = Config(financial_year="2024-2025")
        print(f"✓ Config created for FY{config.financial_year}")
        print(f"  WFH log path: {config.file_paths.wfh_log}")
        print(f"  Invoice catalog path: {config.file_paths.invoice_catalog}")
        print(f"  WFH categories: {len(config.tax_params.wfh_categories)} categories")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_file_validation():
    """Test file path validation"""
    print("\nTesting file validation...")
    try:
        from tax_report_generator.config import Config
        
        config = Config(financial_year="2024-2025")
        validation = config.validate_paths()
        
        print(f"  Required files:")
        for name, exists in validation['required'].items():
            status = "✓" if exists else "❌"
            print(f"    {status} {name}")
        
        print(f"  Optional files:")
        for name, exists in validation['optional'].items():
            status = "✓" if exists else "⚠"
            print(f"    {status} {name}")
        
        if validation['all_valid']:
            print("✓ All required files found")
        else:
            print("⚠ Some required files missing (this is OK for testing)")
        
        return True
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def test_processors():
    """Test processor initialization"""
    print("\nTesting processors...")
    try:
        from tax_report_generator.wfh_processor import WFHProcessor
        from tax_report_generator.invoice_processor import InvoiceProcessor
        from tax_report_generator.bank_processor import BankProcessor
        
        wfh = WFHProcessor(exclude_locations=['Leave'])
        print(f"✓ WFHProcessor initialized")
        
        invoice = InvoiceProcessor(wfh_categories=['Electricity', 'Internet'])
        print(f"✓ InvoiceProcessor initialized")
        
        bank = BankProcessor()
        print(f"✓ BankProcessor initialized")
        
        return True
    except Exception as e:
        print(f"❌ Processor error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("TAX REPORT GENERATOR - SYSTEM TEST")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Configuration", test_configuration),
        ("File Validation", test_file_validation),
        ("Processors", test_processors),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nTo generate a report, run:")
        print("  python generate_tax_report.py")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        if not test_dependencies():
            print("\nInstall missing dependencies:")
            print("  pip install -r tax_report_generator/requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
