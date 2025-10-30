"""
Excel Export with Formatting for Invoice Catalog
"""
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd


class ExcelExporter:
    """Export invoice catalog to formatted Excel file"""
    
    def __init__(self, output_folder: Path):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def export(self, processed_invoices: List[Dict[str, Any]], 
               config: Dict[str, Any]) -> Path:
        """
        Export processed invoices to Excel with multiple sheets
        
        Args:
            processed_invoices: List of processed invoice data
            config: Configuration dictionary
        
        Returns:
            Path to created Excel file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = self.output_folder / f"Invoice_Catalog_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00'
            })
            
            # Create Summary Sheet
            self._create_summary_sheet(writer, processed_invoices, config, 
                                      header_format, currency_format)
            
            # Create Invoices Sheet
            self._create_invoices_sheet(writer, processed_invoices, 
                                       header_format, currency_format)
            
            # Create Failed Files Sheet (if any)
            failed_invoices = [inv for inv in processed_invoices 
                             if inv.get('ProcessingStatus', '').startswith('Failed') 
                             or inv.get('ProcessingStatus', '').startswith('Skipped')]
            
            if failed_invoices:
                self._create_failed_sheet(writer, failed_invoices, header_format)
        
        return excel_path
    
    def _create_summary_sheet(self, writer, processed_invoices: List[Dict[str, Any]],
                             config: Dict[str, Any], header_format, currency_format):
        """Create summary sheet with totals by category"""
        # Prepare summary data
        df = pd.DataFrame(processed_invoices)
        
        # Group by category
        summary = df.groupby('Category').agg({
            'FileName': 'count',
            'TotalAmount': 'sum',
            'DeductibleAmount': 'sum'
        }).reset_index()
        
        summary.columns = ['Category', 'Invoice Count', 'Total Invoiced', 'Total Deductible']
        summary = summary.sort_values('Total Deductible', ascending=False)
        
        # Add totals row
        totals = pd.DataFrame([{
            'Category': 'TOTAL',
            'Invoice Count': summary['Invoice Count'].sum(),
            'Total Invoiced': summary['Total Invoiced'].sum(),
            'Total Deductible': summary['Total Deductible'].sum()
        }])
        
        summary = pd.concat([summary, totals], ignore_index=True)
        
        # Write to Excel
        summary.to_excel(writer, sheet_name='Summary', index=False, startrow=5)
        
        # Get worksheet
        worksheet = writer.sheets['Summary']
        
        # Add title and config info
        title_format = writer.book.add_format({
            'bold': True,
            'font_size': 14
        })
        
        worksheet.write('A1', 'ATO WORK EXPENSE DEDUCTION SUMMARY', title_format)
        worksheet.write('A3', f"Employee: {config.get('occupation', 'N/A')}")
        worksheet.write('B3', f"Work Days WFH: {config.get('work_from_home_days', 0)}/{config.get('total_work_days', 0)}")
        worksheet.write('A4', f"Financial Year: {config.get('financial_year', 'N/A')}")
        worksheet.write('B4', f"Work Use %: {config.get('work_use_percentage', 0)}%")
        
        # Format columns
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:D', 18, currency_format)
        
        # Apply header format
        for col_num, value in enumerate(summary.columns.values):
            worksheet.write(5, col_num, value, header_format)
    
    def _create_invoices_sheet(self, writer, processed_invoices: List[Dict[str, Any]],
                               header_format, currency_format):
        """Create detailed invoices sheet"""
        # Prepare data
        invoices_data = []
        for inv in processed_invoices:
            invoices_data.append({
                'Status': inv.get('ProcessingStatus', 'Unknown'),
                'File': inv.get('FileName', ''),
                'Date': inv.get('InvoiceDate', ''),
                'Vendor': inv.get('VendorName', ''),
                'Category': inv.get('Category', ''),
                'Amount': inv.get('TotalAmount', 0.00),
                'Deductible': inv.get('DeductibleAmount', 0.00),
                'Method': inv.get('ClaimMethod', ''),
                'Moved To': inv.get('MovedTo', '')
            })
        
        df = pd.DataFrame(invoices_data)
        df.to_excel(writer, sheet_name='Invoices', index=False)
        
        # Get worksheet
        worksheet = writer.sheets['Invoices']
        
        # Format columns
        worksheet.set_column('A:A', 15)  # Status
        worksheet.set_column('B:B', 40)  # File
        worksheet.set_column('C:C', 12)  # Date
        worksheet.set_column('D:D', 25)  # Vendor
        worksheet.set_column('E:E', 25)  # Category
        worksheet.set_column('F:F', 12, currency_format)  # Amount
        worksheet.set_column('G:G', 12, currency_format)  # Deductible
        worksheet.set_column('H:H', 35)  # Method
        worksheet.set_column('I:I', 50)  # Moved To
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Color code rows based on status
        failed_format = writer.book.add_format({'bg_color': '#FFE4B5'})  # Orange
        cached_format = writer.book.add_format({'bg_color': '#ADD8E6'})  # Light Blue
        
        for row_num, inv in enumerate(processed_invoices, start=1):
            status = inv.get('ProcessingStatus', '')
            if 'Failed' in status or 'Skipped' in status:
                worksheet.set_row(row_num, None, failed_format)
            elif 'Cached' in status:
                worksheet.set_row(row_num, None, cached_format)
    
    def _create_failed_sheet(self, writer, failed_invoices: List[Dict[str, Any]],
                            header_format):
        """Create failed files sheet"""
        # Prepare data
        failed_data = []
        for inv in failed_invoices:
            failed_data.append({
                'Status': inv.get('ProcessingStatus', 'Unknown'),
                'File': inv.get('FileName', ''),
                'Category': inv.get('Category', ''),
                'Error/Reason': inv.get('ClaimNotes', ''),
                'File Hash': inv.get('FileHash', ''),
                'Original Path': inv.get('OriginalPath', inv.get('FilePath', ''))
            })
        
        df = pd.DataFrame(failed_data)
        df.to_excel(writer, sheet_name='Failed Files', index=False)
        
        # Get worksheet
        worksheet = writer.sheets['Failed Files']
        
        # Format columns
        worksheet.set_column('A:A', 15)  # Status
        worksheet.set_column('B:B', 40)  # File
        worksheet.set_column('C:C', 25)  # Category
        worksheet.set_column('D:D', 50)  # Error/Reason
        worksheet.set_column('E:E', 35)  # File Hash
        worksheet.set_column('F:F', 60)  # Original Path
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
