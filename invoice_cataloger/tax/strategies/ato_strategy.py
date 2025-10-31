"""
ATO Strategy - Australian Taxation Office compliant tax calculations

Implements tax deduction calculations following ATO guidelines.
Uses externalized rules from ato_rules.json.
"""
from pathlib import Path
from typing import Dict, Any, Optional

# Import from parent modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from .base_strategy import TaxStrategy
from ..rules.rule_loader import RuleLoader
from utils import get_logger


class ATOStrategy(TaxStrategy):
    """
    ATO-compliant tax calculation strategy
    
    Implements Australian Taxation Office work-related expense deduction rules
    for Software Developers. Rules are loaded from ato_rules.json.
    """
    
    def __init__(self, rules: Optional[Dict[str, Any]] = None, 
                 rules_path: Optional[Path] = None):
        """
        Initialize ATO strategy
        
        Args:
            rules: Pre-loaded rules dictionary (optional)
            rules_path: Path to rules JSON file (optional, uses default if not provided)
        """
        self.logger = get_logger()
        self.rule_loader = RuleLoader()
        
        # Load rules
        if rules:
            self.rules = rules
        elif rules_path:
            self.rules = self.rule_loader.load_rules(rules_path) or {}
        else:
            # Use default ATO rules
            default_path = RuleLoader.get_default_ato_rules_path()
            self.rules = self.rule_loader.load_rules(default_path) or {}
        
        # Initialize base class
        super().__init__(self.rules)
        
        if not self.rules:
            self.logger.warning("ATO strategy initialized with no rules")
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "ATO"
    
    def calculate_deduction(self, invoice_data: Dict[str, Any], 
                          category: str, 
                          work_use_percentage: float) -> Dict[str, Any]:
        """
        Calculate ATO-compliant tax deduction
        
        Args:
            invoice_data: Invoice data from catalog
            category: Expense category
            work_use_percentage: Work use percentage (0-100)
        
        Returns:
            Dictionary with deduction details
        """
        total_amount = float(invoice_data.get('total', 0))
        
        # Get category rule
        category_rule = self.get_category_rule(category)
        
        if not category_rule:
            # No rule found, return manual review required
            return self._create_manual_review_deduction(category, total_amount, work_use_percentage)
        
        # Calculate based on category rule
        return self._calculate_by_rule(category, total_amount, work_use_percentage, category_rule)
    
    def _calculate_by_rule(self, category: str, total_amount: float,
                          work_use_percentage: float, 
                          rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate deduction based on category rule
        
        Args:
            category: Expense category
            total_amount: Total invoice amount
            work_use_percentage: Work use percentage
            rule: Category rule dictionary
        
        Returns:
            Deduction dictionary
        """
        # Check if work use percentage applies
        work_use_applicable = rule.get('work_use_applicable', True)
        
        if not work_use_applicable:
            # Full deduction (e.g., Professional Development, Memberships)
            return self._calculate_full_deduction(category, total_amount, rule)
        
        # Check for threshold (e.g., $300 for equipment)
        threshold = rule.get('threshold')
        
        if threshold is not None:
            # Apply threshold rules
            return self._calculate_with_threshold(category, total_amount, 
                                                 work_use_percentage, threshold, rule)
        else:
            # Simple work use percentage calculation
            return self._calculate_work_use(category, total_amount, 
                                           work_use_percentage, rule)
    
    def _calculate_full_deduction(self, category: str, total_amount: float,
                                  rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate full deduction (100%)
        
        Args:
            category: Expense category
            total_amount: Total invoice amount
            rule: Category rule
        
        Returns:
            Deduction dictionary
        """
        return self.format_deduction_result(
            category=category,
            total_amount=total_amount,
            work_use_percentage=100,
            deductible_amount=total_amount,
            claim_method=rule.get('claim_method', 'Full Deduction (100%)'),
            claim_notes=rule.get('claim_notes', ''),
            ato_reference=rule.get('ato_reference', ''),
            required_docs=rule.get('required_documentation', [])
        )
    
    def _calculate_work_use(self, category: str, total_amount: float,
                           work_use_percentage: float, 
                           rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate deduction with work use percentage
        
        Args:
            category: Expense category
            total_amount: Total invoice amount
            work_use_percentage: Work use percentage
            rule: Category rule
        
        Returns:
            Deduction dictionary
        """
        deductible_amount = self.calculate_work_use_amount(total_amount, work_use_percentage)
        
        claim_method = rule.get('claim_method', 'Actual Cost Method')
        if work_use_percentage < 100:
            claim_method = f"{claim_method} ({work_use_percentage:.0f}% work use)"
        
        return self.format_deduction_result(
            category=category,
            total_amount=total_amount,
            work_use_percentage=work_use_percentage,
            deductible_amount=deductible_amount,
            claim_method=claim_method,
            claim_notes=rule.get('claim_notes', ''),
            ato_reference=rule.get('ato_reference', ''),
            required_docs=rule.get('required_documentation', [])
        )
    
    def _calculate_with_threshold(self, category: str, total_amount: float,
                                  work_use_percentage: float, threshold: float,
                                  rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate deduction with threshold (e.g., $300 for equipment)
        
        Args:
            category: Expense category
            total_amount: Total invoice amount
            work_use_percentage: Work use percentage
            threshold: Threshold amount
            rule: Category rule
        
        Returns:
            Deduction dictionary
        """
        if total_amount <= threshold:
            # Immediate deduction
            deductible_amount = self.calculate_work_use_amount(total_amount, work_use_percentage)
            claim_method = f"Immediate Deduction (Under ${threshold:.0f})"
            claim_notes = rule.get('claim_notes', '')
            if work_use_percentage < 100:
                claim_notes = f"Work-related portion only ({work_use_percentage:.0f}%). " + claim_notes
        else:
            # Depreciation required
            depreciation_years = rule.get('depreciation_years', 3)
            work_use_amount = self.calculate_work_use_amount(total_amount, work_use_percentage)
            deductible_amount = round(work_use_amount / depreciation_years, 2)
            claim_method = f"Decline in Value (Over ${threshold:.0f} - Depreciation)"
            claim_notes = f"Typical effective life: {depreciation_years} years. Use ATO Depreciation Tool. " + rule.get('claim_notes', '')
        
        return self.format_deduction_result(
            category=category,
            total_amount=total_amount,
            work_use_percentage=work_use_percentage,
            deductible_amount=deductible_amount,
            claim_method=claim_method,
            claim_notes=claim_notes,
            ato_reference=rule.get('ato_reference', ''),
            required_docs=rule.get('required_documentation', [])
        )
    
    def _create_manual_review_deduction(self, category: str, total_amount: float,
                                       work_use_percentage: float) -> Dict[str, Any]:
        """
        Create deduction entry for manual review
        
        Args:
            category: Expense category
            total_amount: Total invoice amount
            work_use_percentage: Work use percentage
        
        Returns:
            Deduction dictionary
        """
        return self.format_deduction_result(
            category=category,
            total_amount=total_amount,
            work_use_percentage=work_use_percentage,
            deductible_amount=0.00,
            claim_method="Manual Review Required",
            claim_notes=f"No rule found for category '{category}'. Consult tax professional.",
            ato_reference="Other Operating Expenses",
            required_docs=["Full documentation", "Professional advice"]
        )
    
    def validate_rules(self) -> tuple[bool, list[str]]:
        """
        Validate ATO rules
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not self.rules:
            return False, ["No rules loaded"]
        
        # Use rule loader validation
        return self.rule_loader.validate_rules(self.rules)
    
    def get_fixed_rate_info(self) -> Optional[Dict[str, Any]]:
        """
        Get fixed rate method information
        
        Returns:
            Fixed rate method info or None
        """
        return self.rules.get('fixed_rate_method')
