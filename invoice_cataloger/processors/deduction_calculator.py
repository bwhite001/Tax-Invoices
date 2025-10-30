"""
ATO Deduction Calculator for Work Expenses
"""
from typing import Dict, Any


class DeductionCalculator:
    """Calculate ATO-compliant deductions for work expenses"""
    
    def __init__(self, work_use_percentage: int, fixed_rate_hourly: float):
        self.work_use_percentage = work_use_percentage
        self.work_use_decimal = work_use_percentage / 100
        self.fixed_rate_hourly = fixed_rate_hourly
    
    def calculate_deduction(self, invoice_data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Calculate ATO deduction for an invoice
        
        Args:
            invoice_data: Extracted invoice data
            category: Expense category
        
        Returns:
            Dictionary with deduction details
        """
        total = float(invoice_data.get('total', 0))
        
        deduction = {
            'Category': category,
            'TotalAmount': total,
            'WorkUsePercentage': self.work_use_percentage,
            'DeductibleAmount': 0.00,
            'ClaimMethod': '',
            'ClaimNotes': '',
            'AtoReference': '',
            'RequiresDocumentation': []
        }
        
        # Calculate based on category
        if category == "Electricity":
            deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
            deduction['ClaimMethod'] = f"Actual Cost Method ({self.work_use_percentage}% work use)"
            deduction['ClaimNotes'] = f"Alternative: Fixed Rate Method at ${self.fixed_rate_hourly}/hour requires time records"
            deduction['AtoReference'] = "Working from Home Expenses"
            deduction['RequiresDocumentation'] = ["Original invoice", "Usage records"]
        
        elif category == "Internet":
            deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
            deduction['ClaimMethod'] = f"Actual Cost Method ({self.work_use_percentage}% work use)"
            deduction['ClaimNotes'] = "NOT claimable if using Fixed Rate Method"
            deduction['AtoReference'] = "Home Phone and Internet Expenses"
            deduction['RequiresDocumentation'] = ["Invoice with breakdown", "Evidence of work use"]
        
        elif category == "Phone & Mobile":
            deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
            deduction['ClaimMethod'] = f"Actual Cost Method ({self.work_use_percentage}% work use)"
            deduction['ClaimNotes'] = "Must have itemized bills showing work calls"
            deduction['AtoReference'] = "Home Phone and Internet Expenses"
            deduction['RequiresDocumentation'] = ["Itemized phone bill", "Call log analysis"]
        
        elif category == "Software & Subscriptions":
            if total <= 300:
                deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
                deduction['ClaimMethod'] = "Immediate Deduction (Under $300)"
                deduction['ClaimNotes'] = "Verify work-related purpose in vendor name/description"
                deduction['AtoReference'] = "Computers, Laptops and Software"
            else:
                # Conservative estimate for depreciation
                deduction['DeductibleAmount'] = round(total * self.work_use_decimal / 2, 2)
                deduction['ClaimMethod'] = "Decline in Value (Over $300 - Depreciation Required)"
                deduction['ClaimNotes'] = "Use ATO Depreciation Tool to calculate. Typical: 2-3 years"
                deduction['AtoReference'] = "Depreciation - Assets over $300"
            deduction['RequiresDocumentation'] = ["Invoice", "Evidence of work-related use"]
        
        elif category == "Computer Equipment":
            if total <= 300:
                deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
                deduction['ClaimMethod'] = "Immediate Deduction (Under $300)"
                deduction['ClaimNotes'] = f"Work-related portion only ({self.work_use_percentage}%)"
            else:
                # Conservative 3-year depreciation estimate
                deduction['DeductibleAmount'] = round(total * self.work_use_decimal / 3, 2)
                deduction['ClaimMethod'] = "Decline in Value (Over $300 - Depreciation)"
                deduction['ClaimNotes'] = "Typical effective life for computers: 2-4 years. Use ATO tool"
                deduction['AtoReference'] = "Depreciation - Assets over $300"
            deduction['RequiresDocumentation'] = ["Invoice", "Purchase receipt", "Depreciation calculation"]
        
        elif category == "Professional Development":
            deduction['DeductibleAmount'] = total
            deduction['WorkUsePercentage'] = 100
            deduction['ClaimMethod'] = "Full Deduction (100%)"
            deduction['ClaimNotes'] = "Must directly relate to current employment and improve current skills"
            deduction['AtoReference'] = "Training and Education"
            deduction['RequiresDocumentation'] = ["Course invoice", "Evidence of course content", "Relevance to role"]
        
        elif category == "Professional Membership":
            deduction['DeductibleAmount'] = total
            deduction['WorkUsePercentage'] = 100
            deduction['ClaimMethod'] = "Full Deduction (100%)"
            deduction['ClaimNotes'] = "Must be relevant to your IT profession"
            deduction['AtoReference'] = "Professional Memberships and Accreditations"
            deduction['RequiresDocumentation'] = ["Invoice", "Membership certificate"]
        
        elif category == "Office Supplies":
            deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
            deduction['ClaimMethod'] = f"Actual Cost Method ({self.work_use_percentage}%) OR included in Fixed Rate"
            deduction['ClaimNotes'] = "Covered by Fixed Rate Method if using that approach"
            deduction['AtoReference'] = "Home Office Expenses"
            deduction['RequiresDocumentation'] = ["Invoice", "Usage records"]
        
        elif category == "Communication Tools":
            deduction['DeductibleAmount'] = round(total * self.work_use_decimal, 2)
            deduction['ClaimMethod'] = f"Actual Cost Method ({self.work_use_percentage}% work use)"
            deduction['AtoReference'] = "Home Phone and Internet Expenses"
            deduction['RequiresDocumentation'] = ["Invoice", "Usage analysis"]
        
        else:
            deduction['DeductibleAmount'] = 0.00
            deduction['ClaimMethod'] = "Manual Review Required"
            deduction['ClaimNotes'] = "Consult tax professional to determine deductibility"
            deduction['AtoReference'] = "Other Operating Expenses"
            deduction['RequiresDocumentation'] = ["Full documentation", "Professional advice"]
        
        return deduction
