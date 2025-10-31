"""
Tax Module - Pluggable Tax Calculation System

This module handles tax deduction calculations using the Strategy Pattern.
Follows Open/Closed Principle - open for extension, closed for modification.
"""

from .tax_calculator import TaxCalculator
from .strategies.base_strategy import TaxStrategy
from .strategies.ato_strategy import ATOStrategy

__all__ = [
    'TaxCalculator',
    'TaxStrategy',
    'ATOStrategy'
]
