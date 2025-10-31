"""
Improved Zip Money Statement Extractor
Specifically designed for Zip Money PDF statements
"""
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import pdfplumber

class ZipMoneyExtractor:
    """Extract transactions from Zip Money PDF statements"""
    
    def __init__(self, input_folder: str, output_folder: str):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.transactions = []
    
    def extract_all(self):
        """Extract all Zip Money statements"""
        print("\n=== Extracting Zip Money Statements ===")
        
        # Find all PDF files with 'zip' in the name
        pdf_files = list(self.input_folder.glob("zip*.pdf")) + \
                   list(self.input_folder.glob("Zip*.pdf"))
        
        if not pdf_files:
            print("No Zip Money PDF files found")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process\n")
        
        for pdf_file in sorted(pdf_files):
            print(f"Processing: {pdf_file.name}")
            self._extract_pdf(pdf_file)
        
        if self.transactions:
            self._save_to_csv()
        else:
            print("\nNo transactions extracted from any files")
    
    def _extract_pdf(self, pdf_file: Path):
        """Extract transactions from a single PDF"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        self._parse_transactions(text, pdf_file.name)
        except Exception as e:
            print(f"  Error: {e}")
    
    def _parse_transactions(self, text: str, source_file: str):
        """Parse transactions from PDF text"""
        lines = text.split('\n')
        
        # Find the transaction summary section
        in_transaction_section = False
        transaction_count = 0
        
        for i, line in enumerate(lines):
            # Start of transaction section
            if 'Transaction summary' in line or 'Transactio n su mmary' in line:
                in_transaction_section = True
                continue
            
            # End of transaction section
            if in_transaction_section and ('Pay your' in line or 'Note:' in line):
                break
            
            # Skip header and opening/closing balance lines
            if not in_transaction_section:
                continue
            
            if 'Date' in line and 'Description' in line and 'Amount' in line:
                continue
            
            if 'Opening Balance' in line or 'Closing Balance' in line:
                continue
            
            # Parse transaction line
            transaction = self._parse_transaction_line(line, source_file)
            if transaction:
                self.transactions.append(transaction)
                transaction_count += 1
        
        if transaction_count > 0:
            print(f"  Extracted {transaction_count} transactions")
    
    def _parse_transaction_line(self, line: str, source_file: str):
        """Parse a single transaction line"""
        # Pattern: Date Description Amount
        # Example: "3 Aug 2024BPAY Payment($250.00)"
        # Example: "8 Aug 2024Amazon AU Order # 213803a8-0663-42ba-920b-8d8ee0c48e7d$58.25"
        
        # Try to extract date (various formats)
        date_patterns = [
            r'(\d{1,2}\s+\w+\s+\d{4})',  # "3 Aug 2024"
            r'(\d{1,2}\s+\w{3}\s+\d{4})',  # "3 Aug 2024"
            r'(\d{1,2}/\d{1,2}/\d{4})',   # "03/08/2024"
        ]
        
        date_str = None
        date_match = None
        
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                date_str = match.group(1)
                date_match = match
                break
        
        if not date_str:
            return None
        
        # Extract amount (at the end of the line)
        amount_pattern = r'\(?\$?([\d,]+\.\d{2})\)?'
        amount_matches = re.findall(amount_pattern, line)
        
        if not amount_matches:
            return None
        
        # Last amount is the transaction amount
        amount_str = amount_matches[-1]
        
        # Determine if it's a payment (negative) or purchase (positive)
        is_payment = '(' in line or 'Payment' in line or 'payment' in line
        
        try:
            amount = float(amount_str.replace(',', ''))
            if is_payment:
                amount = -amount
        except:
            return None
        
        # Extract description (between date and amount)
        # Remove the date from the beginning
        desc_start = date_match.end()
        # Find where the amount starts
        amount_pos = line.rfind('$')
        if amount_pos > desc_start:
            description = line[desc_start:amount_pos].strip()
        else:
            description = line[desc_start:].strip()
        
        # Clean up description
        description = re.sub(r'\s+', ' ', description)
        description = description.replace('($', '').replace(')', '')
        
        if not description:
            description = "Transaction"
        
        # Parse date
        try:
            parsed_date = self._parse_date(date_str)
        except:
            parsed_date = date_str
        
        return {
            'date': parsed_date,
            'bank': 'Zip Money',
            'description': description,
            'amount': amount,
            'balance': '',
            'category': '',
            'source_file': source_file
        }
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to standard format"""
        # Try various formats
        formats = [
            '%d %b %Y',   # "3 Aug 2024"
            '%d %B %Y',   # "3 August 2024"
            '%d/%m/%Y',   # "03/08/2024"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        return date_str
    
    def _save_to_csv(self):
        """Save transactions to CSV"""
        output_path = self.output_folder / "zip_transactions.csv"
        
        df = pd.DataFrame(self.transactions)
        
        # Sort by date
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('date')
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"\n{'='*60}")
        print(f"SUCCESS! Saved {len(self.transactions)} transactions")
        print(f"Output file: {output_path}")
        print(f"{'='*60}")
        
        # Show summary
        print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
        print(f"Total amount: ${df['amount'].sum():.2f}")
        print(f"Payments: {len(df[df['amount'] < 0])}")
        print(f"Purchases: {len(df[df['amount'] > 0])}")


def main():
    print("="*60)
    print("Zip Money Statement Extractor")
    print("="*60)
    
    input_folder = "G:/My Drive/Tax Invoices/Statements/FY2024-FY2025/temp_processing"
    output_folder = "G:/My Drive/Tax Invoices/bankstatements/extracted"
    
    print(f"\nInput: {input_folder}")
    print(f"Output: {output_folder}")
    
    extractor = ZipMoneyExtractor(input_folder, output_folder)
    extractor.extract_all()
    
    print("\n" + "="*60)
    print("Extraction Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
