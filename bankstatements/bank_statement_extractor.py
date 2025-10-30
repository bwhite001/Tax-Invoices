"""
Bank Statement Extractor for Australian Financial Institutions
Supports: Suncorp, Beyondbank, Zip, and Afterpay
Author: Automated Script Generator
Date: October 2024
"""

import os
import sys
import re
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Required installations:
# pip install pdfplumber pandas openpyxl tabula-py PyPDF2

try:
    import pdfplumber
    import pandas as pd
    import PyPDF2
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install required libraries:")
    print("pip install pdfplumber pandas openpyxl tabula-py PyPDF2")
    sys.exit(1)


class BankStatementExtractor:
    """Base class for extracting bank statements"""

    def __init__(self, input_folder: str, output_folder: str):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.transactions = []

    def extract(self):
        """Override this method in subclasses"""
        raise NotImplementedError

    def save_to_csv(self, filename: str):
        """Save extracted transactions to CSV"""
        if not self.transactions:
            print(f"No transactions to save for {filename}")
            return

        output_path = self.output_folder / filename
        df = pd.DataFrame(self.transactions)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Saved {len(self.transactions)} transactions to {output_path}")
        return output_path


class SuncorpExtractor(BankStatementExtractor):
    """Extract Suncorp bank statements (CSV/PDF)"""

    def extract(self):
        """Extract Suncorp statements"""
        print("\n=== Extracting Suncorp Statements ===")

        # Look for CSV files first (preferred format from Suncorp Internet Banking)
        csv_files = list(self.input_folder.glob("*suncorp*.csv")) + \
                   list(self.input_folder.glob("*Suncorp*.csv"))

        for csv_file in csv_files:
            print(f"Processing CSV: {csv_file.name}")
            self._extract_csv(csv_file)

        # Look for PDF files
        pdf_files = list(self.input_folder.glob("*suncorp*.pdf")) + \
                   list(self.input_folder.glob("*Suncorp*.pdf"))

        for pdf_file in pdf_files:
            print(f"Processing PDF: {pdf_file.name}")
            self._extract_pdf(pdf_file)

        if self.transactions:
            self.save_to_csv("suncorp_transactions.csv")
        else:
            print("No Suncorp files found or no transactions extracted")

    def _extract_csv(self, csv_file: Path):
        """Extract from Suncorp CSV format"""
        try:
            # Suncorp CSV typically has: Date, Description, Debit, Credit, Balance
            df = pd.read_csv(csv_file)

            for _, row in df.iterrows():
                transaction = {
                    'bank': 'Suncorp',
                    'date': row.get('Date', row.get('Transaction Date', '')),
                    'description': row.get('Description', row.get('Details', '')),
                    'amount': self._calculate_amount(
                        row.get('Debit', 0), 
                        row.get('Credit', 0)
                    ),
                    'balance': row.get('Balance', ''),
                    'category': '',
                    'source_file': csv_file.name
                }
                self.transactions.append(transaction)
        except Exception as e:
            print(f"Error extracting CSV {csv_file.name}: {e}")

    def _extract_pdf(self, pdf_file: Path):
        """Extract from Suncorp PDF statements"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table or len(table) < 2:
                            continue

                        # Try to identify transaction rows
                        for row in table[1:]:  # Skip header
                            if len(row) >= 3:
                                transaction = self._parse_pdf_row(row, pdf_file.name)
                                if transaction:
                                    self.transactions.append(transaction)
        except Exception as e:
            print(f"Error extracting PDF {pdf_file.name}: {e}")

    def _parse_pdf_row(self, row: List, source_file: str) -> Optional[Dict]:
        """Parse a row from Suncorp PDF"""
        try:
            # Suncorp PDF format: Date, Description, Debit/Withdrawal, Credit/Deposit, Balance
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'

            date_str = ''
            description = ''
            amount = 0.0
            balance = ''

            for cell in row:
                if cell and re.search(date_pattern, str(cell)):
                    date_str = cell
                elif cell and any(keyword in str(cell).lower() for keyword in 
                                 ['transfer', 'payment', 'purchase', 'withdrawal', 'deposit']):
                    description = cell

            if date_str:
                return {
                    'bank': 'Suncorp',
                    'date': date_str,
                    'description': description,
                    'amount': amount,
                    'balance': balance,
                    'category': '',
                    'source_file': source_file
                }
        except:
            pass
        return None

    @staticmethod
    def _calculate_amount(debit, credit):
        """Calculate transaction amount (negative for debit, positive for credit)"""
        try:
            debit_val = float(str(debit).replace('$', '').replace(',', '')) if debit else 0
            credit_val = float(str(credit).replace('$', '').replace(',', '')) if credit else 0
            return credit_val - debit_val
        except:
            return 0.0


class BeyondbankExtractor(BankStatementExtractor):
    """Extract Beyond Bank statements"""

    def extract(self):
        """Extract Beyond Bank statements"""
        print("\n=== Extracting Beyond Bank Statements ===")

        # Beyond Bank provides transaction listings as PDF
        pdf_files = list(self.input_folder.glob("*beyond*.pdf")) + \
                   list(self.input_folder.glob("*Beyond*.pdf"))

        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            self._extract_pdf(pdf_file)

        if self.transactions:
            self.save_to_csv("beyondbank_transactions.csv")
        else:
            print("No Beyond Bank files found or no transactions extracted")

    def _extract_pdf(self, pdf_file: Path):
        """Extract from Beyond Bank PDF"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    # Extract text for pattern matching
                    text = page.extract_text()
                    if text:
                        self._parse_text_transactions(text, pdf_file.name)

                    # Also try table extraction
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            self._parse_table_transactions(table, pdf_file.name)
        except Exception as e:
            print(f"Error extracting {pdf_file.name}: {e}")

    def _parse_text_transactions(self, text: str, source_file: str):
        """Parse transactions from text"""
        # Pattern: Date, Description, Amount, Balance
        lines = text.split('\n')
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        amount_pattern = r'([+-]?\$?[\d,]+\.\d{2})'

        for line in lines:
            if re.search(date_pattern, line):
                # Extract transaction details
                parts = line.split()
                if len(parts) >= 3:
                    transaction = {
                        'bank': 'Beyond Bank',
                        'date': parts[0],
                        'description': ' '.join(parts[1:-2]) if len(parts) > 3 else '',
                        'amount': self._extract_amount(line),
                        'balance': '',
                        'category': '',
                        'source_file': source_file
                    }
                    self.transactions.append(transaction)

    def _parse_table_transactions(self, table: List, source_file: str):
        """Parse transactions from table"""
        for row in table[1:]:  # Skip header
            if len(row) >= 3:
                transaction = {
                    'bank': 'Beyond Bank',
                    'date': row[0] if row[0] else '',
                    'description': row[1] if len(row) > 1 and row[1] else '',
                    'amount': self._extract_amount(row[2]) if len(row) > 2 else 0,
                    'balance': row[-1] if row[-1] else '',
                    'category': '',
                    'source_file': source_file
                }
                if transaction['date']:
                    self.transactions.append(transaction)

    @staticmethod
    def _extract_amount(text: str) -> float:
        """Extract amount from text"""
        try:
            # Remove currency symbols and extract number
            amount_str = re.sub(r'[^\d.,-]', '', str(text))
            amount_str = amount_str.replace(',', '')
            return float(amount_str) if amount_str else 0.0
        except:
            return 0.0


class ZipExtractor(BankStatementExtractor):
    """Extract Zip Money/Pay statements"""

    def extract(self):
        """Extract Zip statements"""
        print("\n=== Extracting Zip Statements ===")

        # Zip provides CSV exports from dashboard
        csv_files = list(self.input_folder.glob("*zip*.csv")) + \
                   list(self.input_folder.glob("*Zip*.csv"))

        for csv_file in csv_files:
            print(f"Processing: {csv_file.name}")
            self._extract_csv(csv_file)

        # Also check for PDF statements
        pdf_files = list(self.input_folder.glob("*zip*.pdf")) + \
                   list(self.input_folder.glob("*Zip*.pdf"))

        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            self._extract_pdf(pdf_file)

        if self.transactions:
            self.save_to_csv("zip_transactions.csv")
        else:
            print("No Zip files found or no transactions extracted")

    def _extract_csv(self, csv_file: Path):
        """Extract from Zip CSV export"""
        try:
            df = pd.read_csv(csv_file)

            for _, row in df.iterrows():
                # Zip CSV format varies, try common column names
                transaction = {
                    'bank': 'Zip',
                    'date': row.get('Order Date', row.get('Date', row.get('Transaction Date', ''))),
                    'description': row.get('Description', row.get('Merchant', row.get('Store Name', ''))),
                    'amount': self._parse_amount(row),
                    'balance': row.get('Balance', ''),
                    'category': '',
                    'source_file': csv_file.name
                }
                self.transactions.append(transaction)
        except Exception as e:
            print(f"Error extracting {csv_file.name}: {e}")

    def _extract_pdf(self, pdf_file: Path):
        """Extract from Zip PDF statement"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Zip statements typically show purchases and payments
                        lines = text.split('\n')
                        for line in lines:
                            if self._is_transaction_line(line):
                                transaction = self._parse_zip_line(line, pdf_file.name)
                                if transaction:
                                    self.transactions.append(transaction)
        except Exception as e:
            print(f"Error extracting {pdf_file.name}: {e}")

    def _parse_amount(self, row) -> float:
        """Parse amount from various Zip column formats"""
        try:
            # Try different column names
            for col in ['Order Amount', 'Amount', 'Transaction Amount', 'Settlement Amount']:
                if col in row and row[col]:
                    amount_str = str(row[col]).replace('$', '').replace(',', '')
                    return float(amount_str)
            return 0.0
        except:
            return 0.0

    @staticmethod
    def _is_transaction_line(line: str) -> bool:
        """Check if line contains a transaction"""
        keywords = ['purchase', 'payment', 'refund', 'fee']
        return any(keyword in line.lower() for keyword in keywords)

    def _parse_zip_line(self, line: str, source_file: str) -> Optional[Dict]:
        """Parse Zip transaction line"""
        try:
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            date_match = re.search(date_pattern, line)

            if date_match:
                return {
                    'bank': 'Zip',
                    'date': date_match.group(),
                    'description': line,
                    'amount': self._extract_amount_from_text(line),
                    'balance': '',
                    'category': '',
                    'source_file': source_file
                }
        except:
            pass
        return None

    @staticmethod
    def _extract_amount_from_text(text: str) -> float:
        """Extract amount from text"""
        try:
            amounts = re.findall(r'\$?([\d,]+\.\d{2})', text)
            if amounts:
                return float(amounts[0].replace(',', ''))
        except:
            pass
        return 0.0


class AfterpayExtractor(BankStatementExtractor):
    """Extract Afterpay statements"""

    def extract(self):
        """Extract Afterpay statements"""
        print("\n=== Extracting Afterpay Statements ===")

        # Afterpay provides CSV settlement reports
        csv_files = list(self.input_folder.glob("*afterpay*.csv")) + \
                   list(self.input_folder.glob("*Afterpay*.csv"))

        for csv_file in csv_files:
            print(f"Processing: {csv_file.name}")
            self._extract_csv(csv_file)

        # Also check for PDF statements  
        pdf_files = list(self.input_folder.glob("*afterpay*.pdf")) + \
                   list(self.input_folder.glob("*Afterpay*.pdf"))

        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            self._extract_pdf(pdf_file)

        if self.transactions:
            self.save_to_csv("afterpay_transactions.csv")
        else:
            print("No Afterpay files found or no transactions extracted")

    def _extract_csv(self, csv_file: Path):
        """Extract from Afterpay CSV reconciliation report"""
        try:
            df = pd.read_csv(csv_file)

            for _, row in df.iterrows():
                # Afterpay CSV columns: Settlement Date, Order Date and Time, 
                # Order Amount, Merchant Fee incl Tax, Net Settlement Amount, Type
                transaction = {
                    'bank': 'Afterpay',
                    'date': row.get('Order Date and Time', row.get('Settlement Date', '')),
                    'description': f"{row.get('Type', 'Order')} - Order #{row.get('Afterpay Order ID', '')}",
                    'amount': self._parse_afterpay_amount(row),
                    'balance': '',
                    'category': row.get('Type', ''),
                    'merchant_fee': row.get('Merchant Fee incl Tax', ''),
                    'net_settlement': row.get('Net Settlement Amount', ''),
                    'source_file': csv_file.name
                }
                self.transactions.append(transaction)
        except Exception as e:
            print(f"Error extracting {csv_file.name}: {e}")

    def _extract_pdf(self, pdf_file: Path):
        """Extract from Afterpay PDF statement"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            self._parse_afterpay_table(table, pdf_file.name)
        except Exception as e:
            print(f"Error extracting {pdf_file.name}: {e}")

    def _parse_afterpay_table(self, table: List, source_file: str):
        """Parse Afterpay table from PDF"""
        for row in table[1:]:  # Skip header
            if len(row) >= 2:
                transaction = {
                    'bank': 'Afterpay',
                    'date': row[0] if row[0] else '',
                    'description': row[1] if len(row) > 1 and row[1] else '',
                    'amount': self._extract_amount_from_text(row[2]) if len(row) > 2 else 0,
                    'balance': '',
                    'category': '',
                    'source_file': source_file
                }
                if transaction['date']:
                    self.transactions.append(transaction)

    @staticmethod
    def _parse_afterpay_amount(row) -> float:
        """Parse amount from Afterpay row"""
        try:
            # Use Order Amount or Net Settlement Amount
            for col in ['Order Amount', 'Net Settlement Amount', 'Settlement Amount']:
                if col in row and row[col]:
                    amount_str = str(row[col]).replace('$', '').replace(',', '')
                    return float(amount_str)
            return 0.0
        except:
            return 0.0

    @staticmethod
    def _extract_amount_from_text(text: str) -> float:
        """Extract amount from text"""
        try:
            amount_str = re.sub(r'[^\d.,-]', '', str(text))
            amount_str = amount_str.replace(',', '')
            return float(amount_str) if amount_str else 0.0
        except:
            return 0.0


def main():
    """Main extraction function"""
    print("="*60)
    print("Bank Statement Extractor")
    print("Supports: Suncorp, Beyond Bank, Zip, Afterpay")
    print("="*60)

    # Set up folders
    input_folder = input("Enter input folder path (or press Enter for 'statements'): ").strip()
    if not input_folder:
        input_folder = "statements"

    output_folder = input("Enter output folder path (or press Enter for 'extracted'): ").strip()
    if not output_folder:
        output_folder = "extracted"

    # Create input folder if it doesn't exist
    Path(input_folder).mkdir(parents=True, exist_ok=True)

    print(f"\nInput folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print("\nPlace your bank statement files (PDF or CSV) in the input folder.")
    print("Files should contain keywords: suncorp, beyond, zip, or afterpay in filename.\n")

    # Extract from each bank
    extractors = [
        SuncorpExtractor(input_folder, output_folder),
        BeyondbankExtractor(input_folder, output_folder),
        ZipExtractor(input_folder, output_folder),
        AfterpayExtractor(input_folder, output_folder)
    ]

    for extractor in extractors:
        try:
            extractor.extract()
        except Exception as e:
            print(f"Error with {extractor.__class__.__name__}: {e}")

    print("\n" + "="*60)
    print("Extraction complete! Check the output folder for CSV files.")
    print("="*60)


if __name__ == "__main__":
    main()
