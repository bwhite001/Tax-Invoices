"""
Tax Module - Pluggable Tax Calculation System

This module handles tax deduction calculations using the Strategy Pattern.
Follows Open/Closed Principle - open for extension, closed for modification.

Features:
- Tax strategies (ATO, custom)
- Rule-based calculations
- Externalized configuration
- WFH log integration
- Tax calculator orchestrator
"""

from .tax_calculator import TaxCalculator
from .strategies.base_strategy import TaxStrategy
from .strategies.ato_strategy import ATOStrategy
from .rules.rule_loader import RuleLoader
from .wfh.wfh_parser import WFHParser
from .wfh.wfh_calculator import WFHCalculator

__all__ = [
    'TaxCalculator',
    'TaxStrategy',
    'ATOStrategy',
    'RuleLoader',
    'WFHParser',
    'WFHCalculator'
]
