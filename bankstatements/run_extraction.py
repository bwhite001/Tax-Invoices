"""
Run bank statement extraction on prepared Zip Money statements
"""
import sys
from pathlib import Path

# Add current directory to path to import the extractor
sys.path.insert(0, str(Path(__file__).parent))

from bank_statement_extractor import ZipExtractor

def main():
    print("="*60)
    print("Zip Money Statement Extraction")
    print("="*60)
    
    # Set up folders
    input_folder = "G:/My Drive/Tax Invoices/Statements/FY2024-FY2025/temp_processing"
    output_folder = "G:/My Drive/Tax Invoices/bankstatements/extracted"
    
    print(f"\nInput folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    
    # Create extractor
    extractor = ZipExtractor(input_folder, output_folder)
    
    # Extract transactions
    print("\nStarting extraction...")
    extractor.extract()
    
    print("\n" + "="*60)
    print("Extraction complete!")
    print("="*60)

if __name__ == "__main__":
    main()
