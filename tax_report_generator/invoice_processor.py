"""
Invoice Processor Module

Single Responsibility: Process invoice catalog and recalculate deductions.
Dependency Inversion: Depends on abstractions (pandas DataFrame), not concrete implementations.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any


class InvoiceProcessor:
    """
    Process invoice catalog and recalculate tax deductions
    
    Responsibilities:
    - Load invoice catalog
    - Recalculate deductions based on WFH percentage
    - Generate category summaries
    """

    def __init__(self, wfh_categories: List[str] = None):
        """
        Initialize invoice processor
        
        Args:
            wfh_categories: Categories that should use WFH percentage for deductions
        """
        self.wfh_categories = wfh_categories or [
            'Electricity', 'Internet', 'Phone & Mobile',
            'Office Supplies', 'Software & Subscriptions',
            'Computer Equipment', 'Communication Tools'
        ]
        self.invoices_df = None
        self.original_total = 0.0
        self.recalculated_total = 0.0

    def load_invoice_catalog(self, file_path: Path) -> pd.DataFrame:
        """
        Load invoice catalog from CSV
        
        Args:
            file_path: Path to invoice catalog CSV
            
        Returns:
            DataFrame with invoice data
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Invoice catalog not found: {file_path}")

        self.invoices_df = pd.read_csv(file_path)
        self.original_total = self.invoices_df['DeductibleAmount'].sum()
        
        return self.invoices_df

    def recalculate_deductions(self, wfh_percentage: float) -> pd.DataFrame:
        """
        Recalculate deductions using actual WFH percentage
        
        Args:
            wfh_percentage: Calculated WFH percentage (0-100)
            
        Returns:
            DataFrame with recalculated deductions
        """
        if self.invoices_df is None:
            raise ValueError("Invoice catalog not loaded. Call load_invoice_catalog() first.")

        # Create new columns for recalculated values
        self.invoices_df['RecalculatedDeduction'] = self.invoices_df['DeductibleAmount']
        self.invoices_df['DeductionMethod'] = 'Original'
        self.invoices_df['AppliedWFHPercentage'] = self.invoices_df['WorkUsePercentage']

        # Recalculate for WFH-dependent categories
        for idx, row in self.invoices_df.iterrows():
            if self._should_recalculate(row):
                new_deduction = self._calculate_new_deduction(row, wfh_percentage)
                
                self.invoices_df.at[idx, 'RecalculatedDeduction'] = new_deduction
                self.invoices_df.at[idx, 'DeductionMethod'] = f'WFH-Based ({wfh_percentage:.1f}%)'
                self.invoices_df.at[idx, 'AppliedWFHPercentage'] = wfh_percentage

        self.recalculated_total = self.invoices_df['RecalculatedDeduction'].sum()
        
        return self.invoices_df

    def _should_recalculate(self, row: pd.Series) -> bool:
        """
        Determine if invoice should be recalculated (DRY - extracted logic)
        
        Args:
            row: Invoice row
            
        Returns:
            True if should recalculate
        """
        category = row.get('Category', '')
        invoice_total = row.get('InvoiceTotal', 0)
        work_use_pct = row.get('WorkUsePercentage', 0)
        
        return (
            category in self.wfh_categories and
            pd.notna(invoice_total) and
            invoice_total > 0 and
            work_use_pct > 0
        )

    def _calculate_new_deduction(self, row: pd.Series, wfh_percentage: float) -> float:
        """
        Calculate new deduction amount (DRY - extracted calculation)
        
        Args:
            row: Invoice row
            wfh_percentage: WFH percentage to apply
            
        Returns:
            New deduction amount
        """
        invoice_total = row.get('InvoiceTotal', 0)
        new_deduction = invoice_total * (wfh_percentage / 100)
        return round(new_deduction, 2)

    def get_category_summary(self) -> pd.DataFrame:
        """
        Generate summary by category
        
        Returns:
            DataFrame with category-level summary
        """
        if self.invoices_df is None:
            raise ValueError("Invoice catalog not loaded")

        summary = self.invoices_df.groupby('Category').agg({
            'FileName': 'count',
            'InvoiceTotal': 'sum',
            'DeductibleAmount': 'sum',
            'RecalculatedDeduction': 'sum'
        }).reset_index()

        summary.columns = [
            'Category',
            'Invoice_Count',
            'Total_Invoiced',
            'Original_Deduction',
            'Recalculated_Deduction'
        ]

        # Calculate adjustment
        summary['Adjustment'] = (
            summary['Recalculated_Deduction'] - summary['Original_Deduction']
        )

        # Round to 2 decimal places
        for col in ['Total_Invoiced', 'Original_Deduction', 'Recalculated_Deduction', 'Adjustment']:
            summary[col] = summary[col].round(2)

        return summary

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get overall summary statistics
        
        Returns:
            Dictionary with summary statistics
        """
        if self.invoices_df is None:
            return self._empty_summary()

        return {
            'invoice_count': len(self.invoices_df),
            'total_invoiced': round(self.invoices_df['InvoiceTotal'].sum(), 2),
            'original_deduction': round(self.original_total, 2),
            'recalculated_deduction': round(self.recalculated_total, 2),
            'adjustment': round(self.recalculated_total - self.original_total, 2),
            'deduction_rate': round(
                (self.recalculated_total / self.invoices_df['InvoiceTotal'].sum() * 100)
                if self.invoices_df['InvoiceTotal'].sum() > 0 else 0,
                2
            )
        }

    def _empty_summary(self) -> Dict[str, Any]:
        """
        Return empty summary structure (DRY - default values)
        
        Returns:
            Empty summary dictionary
        """
        return {
            'invoice_count': 0,
            'total_invoiced': 0.0,
            'original_deduction': 0.0,
            'recalculated_deduction': 0.0,
            'adjustment': 0.0,
            'deduction_rate': 0.0
        }

    def get_monthly_summary(self) -> pd.DataFrame:
        """
        Generate monthly summary of invoices
        
        Returns:
            DataFrame with monthly breakdown
        """
        if self.invoices_df is None:
            raise ValueError("Invoice catalog not loaded")

        # Extract month from invoice date
        df = self.invoices_df.copy()
        df['Month'] = pd.to_datetime(df['InvoiceDate'], errors='coerce').dt.strftime('%Y-%m')

        monthly = df.groupby('Month').agg({
            'InvoiceTotal': 'sum',
            'DeductibleAmount': 'sum',
            'RecalculatedDeduction': 'sum',
            'InvoiceNumber': 'count'
        }).reset_index()

        monthly.columns = [
            'Month',
            'Total_Invoiced',
            'Original_Deduction',
            'Recalculated_Deduction',
            'Invoice_Count'
        ]

        # Round values
        for col in ['Total_Invoiced', 'Original_Deduction', 'Recalculated_Deduction']:
            monthly[col] = monthly[col].round(2)

        return monthly

    def get_data_for_export(self) -> pd.DataFrame:
        """
        Get invoice data formatted for export
        
        Returns:
            DataFrame ready for export
        """
        if self.invoices_df is None:
            return pd.DataFrame()
        
        return self.invoices_df.copy()

    def __repr__(self) -> str:
        """String representation"""
        count = len(self.invoices_df) if self.invoices_df is not None else 0
        return f"InvoiceProcessor(invoices={count}, total_deduction=${self.recalculated_total:,.2f})"
