"""
Base Tax Strategy - Abstract Base Class

Defines the interface for all tax calculation strategies.
Follows Open/Closed Principle and Strategy Pattern.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TaxStrategy(ABC):
    """
    Abstract base class for tax calculation strategies
    
    This class defines the interface that all tax strategies must implement.
    Follows the Strategy Pattern for pluggable tax calculation logic.
    """
    
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        """
        Initialize strategy with optional rules
        
        Args:
            rules: Dictionary of tax rules (optional)
        """
        self.rules = rules or {}
    
    @abstractmethod
    def calculate_deduction(self, invoice_data: Dict[str, Any], 
                          category: str, 
                          work_use_percentage: float) -> Dict[str, Any]:
        """
        Calculate tax deduction for an invoice
        
        Args:
            invoice_data: Invoice data from catalog
            category: Expense category
            work_use_percentage: Work use percentage (0-100)
        
        Returns:
            Dictionary with deduction details:
            {
                'Category': str,
                'TotalAmount': float,
                'WorkUsePercentage': float,
                'DeductibleAmount': float,
                'ClaimMethod': str,
                'ClaimNotes': str,
                'AtoReference': str,
                'RequiresDocumentation': list
            }
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy
        
        Returns:
            Strategy name (e.g., 'ATO', 'Custom')
        """
        pass
    
    def validate_rules(self) -> tuple[bool, list[str]]:
        """
        Validate that rules are properly configured
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not self.rules:
            return False, ["No rules configured"]
        
        return True, []
    
    def get_category_rule(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Get rule for a specific category
        
        Args:
            category: Expense category
        
        Returns:
            Rule dictionary or None if not found
        """
        if 'categories' in self.rules:
            return self.rules['categories'].get(category)
        return None
    
    def calculate_work_use_amount(self, total_amount: float, 
                                  work_use_percentage: float) -> float:
        """
        Calculate work use amount
        
        Args:
            total_amount: Total invoice amount
            work_use_percentage: Work use percentage (0-100)
        
        Returns:
            Work use amount
        """
        return round(total_amount * (work_use_percentage / 100), 2)
    
    def apply_threshold(self, total_amount: float, threshold: Optional[float],
                       work_use_percentage: float) -> tuple[float, str]:
        """
        Apply threshold rules (e.g., immediate deduction vs depreciation)
        
        Args:
            total_amount: Total invoice amount
            threshold: Threshold amount (e.g., $300 for ATO)
            work_use_percentage: Work use percentage
        
        Returns:
            Tuple of (deductible_amount, claim_method)
        """
        if threshold is None or total_amount <= threshold:
            # Immediate deduction
            deductible = self.calculate_work_use_amount(total_amount, work_use_percentage)
            return deductible, "Immediate Deduction"
        else:
            # Depreciation required
            # Conservative estimate: divide by 3 years
            deductible = self.calculate_work_use_amount(total_amount, work_use_percentage) / 3
            return round(deductible, 2), "Decline in Value (Depreciation)"
    
    def format_deduction_result(self, category: str, total_amount: float,
                               work_use_percentage: float, deductible_amount: float,
                               claim_method: str, claim_notes: str,
                               ato_reference: str, 
                               required_docs: list[str]) -> Dict[str, Any]:
        """
        Format deduction result in standard format
        
        Args:
            category: Expense category
            total_amount: Total invoice amount
            work_use_percentage: Work use percentage
            deductible_amount: Calculated deductible amount
            claim_method: Claim method description
            claim_notes: Additional notes
            ato_reference: ATO reference/guide
            required_docs: List of required documentation
        
        Returns:
            Formatted deduction dictionary
        """
        return {
            'Category': category,
            'TotalAmount': total_amount,
            'WorkUsePercentage': work_use_percentage,
            'DeductibleAmount': deductible_amount,
            'ClaimMethod': claim_method,
            'ClaimNotes': claim_notes,
            'AtoReference': ato_reference,
            'RequiresDocumentation': required_docs
        }
