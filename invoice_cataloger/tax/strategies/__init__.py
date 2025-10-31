"""
Tax Strategies Module

Contains different tax calculation strategies following the Strategy Pattern.
"""

from .base_strategy import TaxStrategy
from .ato_strategy import ATOStrategy

__all__ = [
    'TaxStrategy',
    'ATOStrategy'
]
