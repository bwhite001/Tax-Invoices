"""
Expense Cataloger - Consolidate and Categorize Bank Transactions
Processes extracted bank statements and creates a unified expense catalog
Author: Automated Script Generator
Date: October 2024
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Required: pip install pandas openpyxl

try:
    import pandas as pd
except ImportError:
    print("Missing required library: pandas")
    print("Please install: pip install pandas openpyxl")
    sys.exit(1)


class ExpenseCataloger:
    """Consolidate and categorize expenses from multiple bank statements"""

    # Expense categories with keywords
    CATEGORIES = {
        'Groceries': ['woolworths', 'coles', 'aldi', 'iga', 'supermarket', 'grocery'],
        'Dining': ['restaurant', 'cafe', 'coffee', 'uber eats', 'menulog', 
                  'deliveroo', 'doordash', 'mcdonald', 'kfc', 'hungry jack'],
        'Transport': ['fuel', 'petrol', 'gas station', 'bp', 'caltex', 'shell', 
                     'uber', 'taxi', 'public transport', 'parking', 'toll'],
        'Utilities': ['electricity', 'gas', 'water', 'internet', 'phone', 'mobile',
                     'telstra', 'optus', 'vodafone', 'energy', 'agl', 'origin'],
        'Entertainment': ['netflix', 'spotify', 'youtube', 'disney', 'stan', 
                         'cinema', 'movie', 'games', 'steam', 'playstation'],
        'Shopping': ['amazon', 'ebay', 'kmart', 'target', 'big w', 'bunnings',
                    'jb hi-fi', 'harvey norman', 'officeworks'],
        'Health': ['pharmacy', 'chemist', 'doctor', 'medical', 'hospital', 
                  'dental', 'physio', 'medicare'],
        'Insurance': ['insurance', 'nrma', 'racv', 'bupa', 'medibank'],
        'Subscription': ['subscription', 'membership', 'annual fee', 'monthly fee'],
        'Banking': ['bank fee', 'atm', 'interest', 'service fee'],
        'Income': ['salary', 'wage', 'pay', 'deposit', 'transfer in', 'refund'],
        'Transfer': ['transfer', 'payment to', 'bpay'],
        'Other': []  # Catch-all category
    }

    def __init__(self, input_folder: str, output_file: str = "expense_catalog.csv"):
        self.input_folder = Path(input_folder)
        self.output_file = output_file
        self.all_transactions = []

    def load_all_statements(self):
        """Load all CSV files from the input folder"""
        print("\n=== Loading Bank Statements ===")

        csv_files = list(self.input_folder.glob("*.csv"))

        if not csv_files:
            print(f"No CSV files found in {self.input_folder}")
            return False

        for csv_file in csv_files:
            print(f"Loading: {csv_file.name}")
            try:
                df = pd.read_csv(csv_file)
                print(f"  - Found {len(df)} transactions")
                self.all_transactions.append(df)
            except Exception as e:
                print(f"  - Error loading {csv_file.name}: {e}")

        return len(self.all_transactions) > 0

    def consolidate_transactions(self) -> pd.DataFrame:
        """Consolidate all transactions into a single DataFrame"""
        print("\n=== Consolidating Transactions ===")

        if not self.all_transactions:
            print("No transactions to consolidate")
            return pd.DataFrame()

        # Combine all DataFrames
        combined_df = pd.concat(self.all_transactions, ignore_index=True)

        # Standardize column names
        combined_df = self._standardize_columns(combined_df)

        # Parse and standardize dates
        combined_df = self._standardize_dates(combined_df)

        # Add categories
        print("\n=== Categorizing Transactions ===")
        combined_df['category'] = combined_df['description'].apply(self._categorize_transaction)

        # Add expense type
        combined_df['type'] = combined_df['amount'].apply(
            lambda x: 'Income' if x > 0 else 'Expense'
        )

        # Sort by date (most recent first)
        combined_df = combined_df.sort_values('date', ascending=False)

        print(f"\nTotal transactions: {len(combined_df)}")
        print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")

        return combined_df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names across different banks"""
        # Ensure required columns exist
        required_columns = ['date', 'description', 'amount', 'bank']

        for col in required_columns:
            if col not in df.columns:
                df[col] = ''

        return df

    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date formats"""
        def parse_date(date_str):
            if pd.isna(date_str) or not date_str:
                return pd.NaT

            date_str = str(date_str).strip()

            # Try various date formats
            formats = [
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y-%m-%d',
                '%d/%m/%y',
                '%d-%m-%y',
                '%d %b %Y',
                '%d %B %Y',
                '%Y/%m/%d'
            ]

            for fmt in formats:
                try:
                    return pd.to_datetime(date_str, format=fmt)
                except:
                    continue

            # Try pandas auto-parse
            try:
                return pd.to_datetime(date_str)
            except:
                return pd.NaT

        df['date'] = df['date'].apply(parse_date)
        return df

    def _categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description"""
        if pd.isna(description):
            return 'Other'

        description_lower = str(description).lower()

        # Check each category's keywords
        for category, keywords in self.CATEGORIES.items():
            if category == 'Other':
                continue

            for keyword in keywords:
                if keyword in description_lower:
                    return category

        return 'Other'

    def generate_summary(self, df: pd.DataFrame):
        """Generate expense summary statistics"""
        print("\n" + "="*60)
        print("EXPENSE SUMMARY")
        print("="*60)

        # Overall summary
        total_expenses = df[df['amount'] < 0]['amount'].sum()
        total_income = df[df['amount'] > 0]['amount'].sum()

        print(f"\nTotal Income:   ${abs(total_income):,.2f}")
        print(f"Total Expenses: ${abs(total_expenses):,.2f}")
        print(f"Net:            ${(total_income + total_expenses):,.2f}")

        # Category breakdown
        print("\n--- Expenses by Category ---")
        category_summary = df[df['amount'] < 0].groupby('category')['amount'].agg([
            ('Total', lambda x: abs(x.sum())),
            ('Count', 'count'),
            ('Average', lambda x: abs(x.mean()))
        ]).sort_values('Total', ascending=False)

        print(category_summary.to_string())

        # Bank breakdown
        print("\n--- Transactions by Bank ---")
        bank_summary = df.groupby('bank')['amount'].agg([
            ('Transactions', 'count'),
            ('Total Expenses', lambda x: abs(x[x < 0].sum())),
            ('Total Income', lambda x: x[x > 0].sum())
        ])
        print(bank_summary.to_string())

        # Monthly breakdown (if date range > 1 month)
        if not df['date'].isna().all():
            df['month'] = df['date'].dt.to_period('M')
            print("\n--- Monthly Expenses ---")
            monthly_summary = df[df['amount'] < 0].groupby('month')['amount'].agg([
                ('Total', lambda x: abs(x.sum())),
                ('Count', 'count')
            ]).sort_index(ascending=False)
            print(monthly_summary.to_string())

        print("\n" + "="*60)

    def save_catalog(self, df: pd.DataFrame, output_path: str = None):
        """Save consolidated catalog to CSV"""
        if output_path is None:
            output_path = self.input_folder / self.output_file
        else:
            output_path = Path(output_path)

        # Select and reorder columns for output
        output_columns = ['date', 'bank', 'description', 'amount', 'category', 
                         'type', 'balance', 'source_file']

        # Only include columns that exist
        output_columns = [col for col in output_columns if col in df.columns]

        df_output = df[output_columns].copy()

        # Format date
        if 'date' in df_output.columns:
            df_output['date'] = df_output['date'].dt.strftime('%Y-%m-%d')

        # Format amount
        if 'amount' in df_output.columns:
            df_output['amount'] = df_output['amount'].round(2)

        df_output.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\nCatalog saved to: {output_path}")
        print(f"Total records: {len(df_output)}")

        # Also save Excel version with formatting
        excel_path = output_path.with_suffix('.xlsx')
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_output.to_excel(writer, sheet_name='Transactions', index=False)

                # Add summary sheet
                summary_df = self._create_summary_dataframe(df)
                summary_df.to_excel(writer, sheet_name='Summary')

            print(f"Excel version saved to: {excel_path}")
        except Exception as e:
            print(f"Could not save Excel version: {e}")

    def _create_summary_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a summary DataFrame for Excel export"""
        summary_data = []

        # Overall totals
        summary_data.append(['Metric', 'Value'])
        summary_data.append(['Total Transactions', len(df)])
        summary_data.append(['Total Income', f"${df[df['amount'] > 0]['amount'].sum():.2f}"])
        summary_data.append(['Total Expenses', f"${abs(df[df['amount'] < 0]['amount'].sum()):.2f}"])
        summary_data.append([''])

        # Category breakdown
        summary_data.append(['Category', 'Total Spent', 'Transaction Count'])
        category_summary = df[df['amount'] < 0].groupby('category')['amount'].agg([
            ('Total', lambda x: abs(x.sum())),
            ('Count', 'count')
        ]).sort_values('Total', ascending=False)

        for category, row in category_summary.iterrows():
            summary_data.append([category, f"${row['Total']:.2f}", int(row['Count'])])

        return pd.DataFrame(summary_data)

    def create_monthly_report(self, df: pd.DataFrame):
        """Create a monthly expense report"""
        if df['date'].isna().all():
            print("Cannot create monthly report: no valid dates")
            return

        df['year_month'] = df['date'].dt.to_period('M')

        # Pivot table: rows=categories, columns=months, values=total expenses
        monthly_by_category = df[df['amount'] < 0].pivot_table(
            values='amount',
            index='category',
            columns='year_month',
            aggfunc=lambda x: abs(x.sum()),
            fill_value=0
        )

        output_path = self.input_folder / "monthly_expenses_by_category.csv"
        monthly_by_category.to_csv(output_path)
        print(f"\nMonthly report saved to: {output_path}")

    def filter_and_export(self, df: pd.DataFrame):
        """Export filtered views of the data"""
        print("\n=== Creating Filtered Exports ===")

        # Export expenses only
        expenses_df = df[df['amount'] < 0].copy()
        if len(expenses_df) > 0:
            expense_path = self.input_folder / "expenses_only.csv"
            expenses_df.to_csv(expense_path, index=False, encoding='utf-8-sig')
            print(f"Expenses exported to: {expense_path}")

        # Export income only
        income_df = df[df['amount'] > 0].copy()
        if len(income_df) > 0:
            income_path = self.input_folder / "income_only.csv"
            income_df.to_csv(income_path, index=False, encoding='utf-8-sig')
            print(f"Income exported to: {income_path}")

        # Export by category
        for category in df['category'].unique():
            if pd.isna(category):
                continue
            category_df = df[df['category'] == category].copy()
            if len(category_df) > 0:
                safe_filename = re.sub(r'[^\w\s-]', '', category).strip().replace(' ', '_')
                category_path = self.input_folder / f"category_{safe_filename}.csv"
                category_df.to_csv(category_path, index=False, encoding='utf-8-sig')
                print(f"  - {category}: {len(category_df)} transactions")


def main():
    """Main cataloging function"""
    print("="*60)
    print("Expense Cataloger")
    print("Consolidate and categorize bank transactions")
    print("="*60)

    # Get input folder
    input_folder = input("\nEnter folder with extracted CSV files (or press Enter for 'extracted'): ").strip()
    if not input_folder:
        input_folder = "extracted"

    if not Path(input_folder).exists():
        print(f"Error: Folder '{input_folder}' does not exist!")
        print("Please run the bank statement extractor first.")
        return

    # Create cataloger
    cataloger = ExpenseCataloger(input_folder)

    # Load statements
    if not cataloger.load_all_statements():
        print("\nNo statements loaded. Exiting.")
        return

    # Consolidate and categorize
    consolidated_df = cataloger.consolidate_transactions()

    if consolidated_df.empty:
        print("\nNo transactions to process. Exiting.")
        return

    # Generate summary
    cataloger.generate_summary(consolidated_df)

    # Save main catalog
    cataloger.save_catalog(consolidated_df)

    # Create monthly report
    try:
        cataloger.create_monthly_report(consolidated_df)
    except Exception as e:
        print(f"Could not create monthly report: {e}")

    # Create filtered exports
    create_filters = input("\nCreate filtered exports by category? (y/n): ").strip().lower()
    if create_filters == 'y':
        cataloger.filter_and_export(consolidated_df)

    print("\n" + "="*60)
    print("Cataloging complete!")
    print("="*60)


if __name__ == "__main__":
    main()
