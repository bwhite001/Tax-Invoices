"""
CSV Export for Invoice Catalog
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import csv


class CSVExporter:
    """Export invoice catalog to CSV files"""
    
    def __init__(self, output_folder: Path):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def export(self, processed_invoices: List[Dict[str, Any]]) -> tuple[Path, Path, Optional[Path]]:
        """
        Export processed invoices to CSV files
        
        Args:
            processed_invoices: List of processed invoice data
        
        Returns:
            Tuple of (catalog_path, summary_path, manual_review_path)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export detailed catalog
        catalog_path = self._export_catalog(processed_invoices, timestamp)
        
        # Export summary
        summary_path = self._export_summary(processed_invoices, timestamp)
        
        # Export manual review list (if any)
        manual_review_path = self._export_manual_review(processed_invoices, timestamp)
        
        return catalog_path, summary_path, manual_review_path
    
    def _export_catalog(self, processed_invoices: List[Dict[str, Any]], 
                       timestamp: str) -> Path:
        """Export detailed catalog CSV"""
        catalog_path = self.output_folder / f"Invoice_Catalog_{timestamp}.csv"
        
        fieldnames = [
            'ProcessDate', 'ProcessingStatus', 'FileName', 'FileType', 'FileHash',
            'VendorName', 'VendorABN', 'InvoiceNumber', 'InvoiceDate', 'DueDate',
            'Category', 'Currency', 'SubTotal', 'Tax', 'InvoiceTotal',
            'WorkUsePercentage', 'DeductibleAmount', 'ClaimMethod', 'ClaimNotes',
            'ATOReference', 'RequiredDocumentation', 'OriginalPath', 'MovedTo',
            'NeedsManualReview', 'MissingFields'
        ]
        
        with open(catalog_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for inv in processed_invoices:
                row = {
                    'ProcessDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ProcessingStatus': inv.get('ProcessingStatus', 'Unknown'),
                    'FileName': inv.get('FileName', ''),
                    'FileType': inv.get('FileType', ''),
                    'FileHash': inv.get('FileHash', ''),
                    'VendorName': inv.get('VendorName', ''),
                    'VendorABN': inv.get('VendorABN', ''),
                    'InvoiceNumber': inv.get('InvoiceNumber', ''),
                    'InvoiceDate': inv.get('InvoiceDate', ''),
                    'DueDate': inv.get('DueDate', ''),
                    'Category': inv.get('Category', ''),
                    'Currency': inv.get('Currency', 'AUD'),
                    'SubTotal': inv.get('SubTotal', 0.00),
                    'Tax': inv.get('Tax', 0.00),
                    'InvoiceTotal': inv.get('TotalAmount', 0.00),
                    'WorkUsePercentage': inv.get('WorkUsePercentage', 0),
                    'DeductibleAmount': inv.get('DeductibleAmount', 0.00),
                    'ClaimMethod': inv.get('ClaimMethod', ''),
                    'ClaimNotes': inv.get('ClaimNotes', ''),
                    'ATOReference': inv.get('AtoReference', ''),
                    'RequiredDocumentation': '; '.join(inv.get('RequiresDocumentation', [])),
                    'OriginalPath': inv.get('OriginalPath', inv.get('FilePath', '')),
                    'MovedTo': inv.get('MovedTo', ''),
                    'NeedsManualReview': 'Yes' if inv.get('NeedsManualReview', False) else 'No',
                    'MissingFields': '; '.join(inv.get('MissingFields', []))
                }
                writer.writerow(row)
        
        return catalog_path
    
    def _export_summary(self, processed_invoices: List[Dict[str, Any]], 
                       timestamp: str) -> Path:
        """Export summary CSV"""
        summary_path = self.output_folder / f"Deduction_Summary_{timestamp}.csv"
        
        # Group by category
        category_totals = {}
        for inv in processed_invoices:
            category = inv.get('Category', 'Other')
            if category not in category_totals:
                category_totals[category] = {
                    'count': 0,
                    'total_invoiced': 0.00,
                    'total_deductible': 0.00
                }
            
            category_totals[category]['count'] += 1
            category_totals[category]['total_invoiced'] += float(inv.get('TotalAmount', 0))
            category_totals[category]['total_deductible'] += float(inv.get('DeductibleAmount', 0))
        
        # Write summary
        fieldnames = ['Category', 'InvoiceCount', 'TotalInvoiced', 'TotalDeductible', 'AverageDeduction']
        
        with open(summary_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Sort by total deductible
            sorted_categories = sorted(
                category_totals.items(),
                key=lambda x: x[1]['total_deductible'],
                reverse=True
            )
            
            for category, totals in sorted_categories:
                avg_deduction = totals['total_deductible'] / totals['count'] if totals['count'] > 0 else 0
                
                writer.writerow({
                    'Category': category,
                    'InvoiceCount': totals['count'],
                    'TotalInvoiced': round(totals['total_invoiced'], 2),
                    'TotalDeductible': round(totals['total_deductible'], 2),
                    'AverageDeduction': round(avg_deduction, 2)
                })
        
        return summary_path
    
    def _export_manual_review(self, processed_invoices: List[Dict[str, Any]], 
                              timestamp: str) -> Optional[Path]:
        """Export manual review required CSV"""
        # Filter invoices needing manual review
        manual_review_invoices = [
            inv for inv in processed_invoices 
            if inv.get('NeedsManualReview', False)
        ]
        
        if not manual_review_invoices:
            return None
        
        manual_review_path = self.output_folder / f"Manual_Review_Required_{timestamp}.csv"
        
        fieldnames = [
            'FileName', 'VendorName', 'InvoiceDate', 'TotalAmount',
            'Category', 'MissingFields', 'FilePath', 'ProcessingStatus'
        ]
        
        with open(manual_review_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for inv in manual_review_invoices:
                writer.writerow({
                    'FileName': inv.get('FileName', ''),
                    'VendorName': inv.get('VendorName', 'N/A'),
                    'InvoiceDate': inv.get('InvoiceDate', ''),
                    'TotalAmount': inv.get('TotalAmount', 0.00),
                    'Category': inv.get('Category', ''),
                    'MissingFields': '; '.join(inv.get('MissingFields', [])),
                    'FilePath': inv.get('FilePath', ''),
                    'ProcessingStatus': inv.get('ProcessingStatus', 'Unknown')
                })
        
        return manual_review_path
