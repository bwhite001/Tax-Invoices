"""
Bank Processor Module

Single Responsibility: Process bank statement data.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any


class BankProcessor:
    """
    Process bank statement data
    
    Responsibilities:
    - Load bank statement transactions
    - Categorize for tax purposes
    - Generate summaries
    """

    def __init__(self):
        """Initialize bank processor"""
        self.transactions_df = None

    def load_bank_statements(self, file_path: Path) -> pd.DataFrame:
        """
        Load bank statement transactions
        
        Args:
            file_path: Path to bank statement CSV
            
        Returns:
            DataFrame with transaction data
        """
        if not file_path.exists():
            print(f"Warning: Bank statement file not found: {file_path}")
            self.transactions_df = pd.DataFrame()
            return self.transactions_df

        self.transactions_df = pd.read_csv(file_path)
        return self.transactions_df

    def categorize_for_tax(self) -> pd.DataFrame:
        """
        Add tax relevance categorization to transactions
        
        Returns:
            DataFrame with tax categorization
        """
        if self.transactions_df is None or len(self.transactions_df) == 0:
            return pd.DataFrame()

        # Add tax relevance columns
        self.transactions_df['TaxRelevant'] = False
        self.transactions_df['TaxCategory'] = 'Personal'

        # Keywords that might indicate tax-relevant expenses
        tax_keywords = [
            'office', 'computer', 'software', 'internet', 'phone',
            'professional', 'business', 'work', 'equipment', 'subscription'
        ]

        # Check each transaction
        for idx, row in self.transactions_df.iterrows():
            description = str(row.get('Description', '')).lower()
            category = str(row.get('Category', '')).lower()
            
            # Check if any keyword matches
            for keyword in tax_keywords:
                if keyword in description or keyword in category:
                    self.transactions_df.at[idx, 'TaxRelevant'] = True
                    self.transactions_df.at[idx, 'TaxCategory'] = 'Potentially Deductible'
                    break

        return self.transactions_df

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get bank statement summary statistics
        
        Returns:
            Dictionary with summary statistics
        """
        if self.transactions_df is None or len(self.transactions_df) == 0:
            return self._empty_summary()

        total_transactions = len(self.transactions_df)
        tax_relevant = self.transactions_df['TaxRelevant'].sum() if 'TaxRelevant' in self.transactions_df.columns else 0
        
        # Calculate totals
        amount_col = 'Amount' if 'Amount' in self.transactions_df.columns else None
        total_amount = self.transactions_df[amount_col].sum() if amount_col else 0
        
        return {
            'total_transactions': int(total_transactions),
            'tax_relevant_count': int(tax_relevant),
            'total_amount': round(float(total_amount), 2),
            'has_data': True
        }

    def _empty_summary(self) -> Dict[str, Any]:
        """
        Return empty summary structure
        
        Returns:
            Empty summary dictionary
        """
        return {
            'total_transactions': 0,
            'tax_relevant_count': 0,
            'total_amount': 0.0,
            'has_data': False
        }

    def get_data_for_export(self) -> pd.DataFrame:
        """
        Get bank data formatted for export
        
        Returns:
            DataFrame ready for export
        """
        if self.transactions_df is None:
            return pd.DataFrame()
        
        return self.transactions_df.copy()

    def __repr__(self) -> str:
        """String representation"""
        count = len(self.transactions_df) if self.transactions_df is not None else 0
        return f"BankProcessor(transactions={count})"
