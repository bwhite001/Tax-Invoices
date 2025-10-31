"""
WFH Calculator - Calculate work-use percentage from WFH logs

Calculates:
- Total WFH days
- Total work days
- WFH percentage
- Monthly breakdown
- Statistics report
"""
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils import get_logger


class WFHCalculator:
    """
    Calculate work-use percentage from WFH logs
    
    Provides statistics and reports on WFH patterns.
    """
    
    def __init__(self):
        self.logger = get_logger()
    
    def calculate_wfh_percentage(self, log_data: List[Dict[str, Any]]) -> float:
        """
        Calculate WFH percentage
        
        Formula: (WFH Days / Total Work Days) × 100
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            WFH percentage (0-100)
        """
        if not log_data:
            self.logger.warning("No WFH log data provided, using default")
            return 60.0  # Default fallback
        
        wfh_days = self.calculate_wfh_days(log_data)
        total_days = self.calculate_total_work_days(log_data)
        
        if total_days == 0:
            self.logger.warning("No work days found in log, using default")
            return 60.0
        
        percentage = (wfh_days / total_days) * 100
        
        self.logger.info(f"Calculated WFH percentage: {percentage:.1f}% ({wfh_days}/{total_days} days)")
        
        return round(percentage, 1)
    
    def calculate_wfh_days(self, log_data: List[Dict[str, Any]]) -> int:
        """
        Count WFH days
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            Number of WFH days
        """
        wfh_days = sum(1 for entry in log_data if entry.get('wfh', False))
        return wfh_days
    
    def calculate_total_work_days(self, log_data: List[Dict[str, Any]]) -> int:
        """
        Count total work days
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            Total number of work days
        """
        return len(log_data)
    
    def calculate_office_days(self, log_data: List[Dict[str, Any]]) -> int:
        """
        Count office days
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            Number of office days
        """
        office_days = sum(1 for entry in log_data if not entry.get('wfh', False))
        return office_days
    
    def get_wfh_stats_by_month(self, log_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Get WFH statistics broken down by month
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            Dictionary with monthly statistics
            {
                "2024-07": {
                    "wfh_days": 12,
                    "total_days": 20,
                    "office_days": 8,
                    "percentage": 60.0
                }
            }
        """
        monthly_stats = defaultdict(lambda: {'wfh_days': 0, 'total_days': 0, 'office_days': 0})
        
        for entry in log_data:
            if 'date' not in entry:
                continue
            
            # Extract year-month (YYYY-MM)
            date_str = entry['date']
            if len(date_str) >= 7:
                year_month = date_str[:7]  # YYYY-MM
                
                monthly_stats[year_month]['total_days'] += 1
                
                if entry.get('wfh', False):
                    monthly_stats[year_month]['wfh_days'] += 1
                else:
                    monthly_stats[year_month]['office_days'] += 1
        
        # Calculate percentages
        for year_month, stats in monthly_stats.items():
            if stats['total_days'] > 0:
                stats['percentage'] = round((stats['wfh_days'] / stats['total_days']) * 100, 1)
            else:
                stats['percentage'] = 0.0
        
        return dict(monthly_stats)
    
    def generate_wfh_report(self, log_data: List[Dict[str, Any]], 
                           financial_year: str = None) -> str:
        """
        Generate comprehensive WFH statistics report
        
        Args:
            log_data: List of WFH entries
            financial_year: Optional financial year label
        
        Returns:
            Formatted report string
        """
        if not log_data:
            return "No WFH data available"
        
        # Calculate overall statistics
        total_days = self.calculate_total_work_days(log_data)
        wfh_days = self.calculate_wfh_days(log_data)
        office_days = self.calculate_office_days(log_data)
        percentage = self.calculate_wfh_percentage(log_data)
        
        # Get monthly breakdown
        monthly_stats = self.get_wfh_stats_by_month(log_data)
        
        # Get date range
        dates = [entry['date'] for entry in log_data if 'date' in entry]
        start_date = min(dates) if dates else 'N/A'
        end_date = max(dates) if dates else 'N/A'
        
        # Build report
        report_lines = [
            "=" * 60,
            "WFH STATISTICS REPORT",
            "=" * 60,
        ]
        
        if financial_year:
            report_lines.append(f"Financial Year: {financial_year}")
        
        report_lines.extend([
            f"Date Range: {start_date} to {end_date}",
            "",
            "OVERALL STATISTICS",
            "-" * 60,
            f"Total Work Days:    {total_days:>6}",
            f"WFH Days:           {wfh_days:>6}",
            f"Office Days:        {office_days:>6}",
            f"WFH Percentage:     {percentage:>5.1f}%",
            "",
            "MONTHLY BREAKDOWN",
            "-" * 60,
        ])
        
        # Sort months chronologically
        sorted_months = sorted(monthly_stats.keys())
        
        for year_month in sorted_months:
            stats = monthly_stats[year_month]
            
            # Format month name
            try:
                date_obj = datetime.strptime(year_month + "-01", '%Y-%m-%d')
                month_name = date_obj.strftime('%B %Y')
            except:
                month_name = year_month
            
            report_lines.append(
                f"{month_name:20} {stats['wfh_days']:>3} WFH / {stats['total_days']:>3} total "
                f"({stats['percentage']:>5.1f}%)"
            )
        
        report_lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(report_lines)
    
    def get_summary_stats(self, log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics as dictionary
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            Dictionary with summary statistics
        """
        if not log_data:
            return {
                'total_days': 0,
                'wfh_days': 0,
                'office_days': 0,
                'percentage': 0.0,
                'monthly_stats': {}
            }
        
        return {
            'total_days': self.calculate_total_work_days(log_data),
            'wfh_days': self.calculate_wfh_days(log_data),
            'office_days': self.calculate_office_days(log_data),
            'percentage': self.calculate_wfh_percentage(log_data),
            'monthly_stats': self.get_wfh_stats_by_month(log_data)
        }
    
    def validate_percentage(self, percentage: float) -> tuple[bool, str]:
        """
        Validate calculated percentage
        
        Args:
            percentage: Calculated WFH percentage
        
        Returns:
            Tuple of (is_valid, message)
        """
        if percentage < 0 or percentage > 100:
            return False, f"Invalid percentage: {percentage}% (must be 0-100)"
        
        if percentage == 0:
            return False, "Warning: 0% WFH - no work from home days found"
        
        if percentage == 100:
            return True, "Note: 100% WFH - all days are work from home"
        
        return True, f"Valid percentage: {percentage}%"
