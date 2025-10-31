"""
WFH Module - Work From Home Log Integration

Calculates dynamic work-use percentage based on actual WFH days.
"""

from .wfh_parser import WFHParser
from .wfh_calculator import WFHCalculator

__all__ = ['WFHParser', 'WFHCalculator']
