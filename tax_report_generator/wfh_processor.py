"""
WFH Processor Module

Single Responsibility: Process Work From Home logs and calculate statistics.
Open/Closed: Open for extension (new location types), closed for modification.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime


class WFHProcessor:
    """
    Process Work From Home logs
    
    Responsibilities:
    - Load WFH log data
    - Calculate WFH statistics
    - Generate monthly breakdowns
    """

    def __init__(self, exclude_locations: List[str] = None):
        """
        Initialize WFH processor
        
        Args:
            exclude_locations: Locations to exclude from calculations (e.g., ['Leave'])
        """
        self.exclude_locations = exclude_locations or ['Leave']
        self.wfh_data = []
        self.statistics = {}

    def load_wfh_log(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load WFH log from CSV file
        
        Args:
            file_path: Path to WFH log CSV
            
        Returns:
            List of WFH entries
        """
        if not file_path.exists():
            raise FileNotFoundError(f"WFH log not found: {file_path}")

        self.wfh_data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                location = row.get('Location', '')
                
                # Skip excluded locations
                if location in self.exclude_locations:
                    continue
                
                # Determine if working from home
                wfh = (location == 'Home')
                
                entry = {
                    'Date': row.get('Date', ''),
                    'Day': row.get('Day', ''),
                    'Time': row.get('Time', ''),
                    'Location': location,
                    'WorkFromHome': wfh
                }
                
                self.wfh_data.append(entry)
        
        return self.wfh_data

    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate WFH statistics
        
        Returns:
            Dictionary with WFH statistics
        """
        if not self.wfh_data:
            return self._empty_statistics()

        total_days = len(self.wfh_data)
        wfh_days = sum(1 for entry in self.wfh_data if entry['WorkFromHome'])
        office_days = total_days - wfh_days
        wfh_percentage = (wfh_days / total_days * 100) if total_days > 0 else 0

        # Calculate monthly breakdown
        monthly_stats = self._calculate_monthly_breakdown()

        self.statistics = {
            'total_days': total_days,
            'wfh_days': wfh_days,
            'office_days': office_days,
            'wfh_percentage': round(wfh_percentage, 2),
            'monthly_breakdown': monthly_stats
        }

        return self.statistics

    def _calculate_monthly_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate monthly WFH breakdown (DRY - extracted method)
        
        Returns:
            Dictionary with monthly statistics
        """
        monthly_stats = defaultdict(lambda: {'wfh': 0, 'office': 0, 'total': 0})
        
        for entry in self.wfh_data:
            date_str = entry.get('Date', '')
            if len(date_str) >= 7:
                month = date_str[:7]  # YYYY-MM format
                
                monthly_stats[month]['total'] += 1
                if entry['WorkFromHome']:
                    monthly_stats[month]['wfh'] += 1
                else:
                    monthly_stats[month]['office'] += 1
        
        # Calculate percentages
        for month in monthly_stats:
            stats = monthly_stats[month]
            if stats['total'] > 0:
                stats['percentage'] = round((stats['wfh'] / stats['total']) * 100, 2)
            else:
                stats['percentage'] = 0.0
        
        return dict(monthly_stats)

    def _empty_statistics(self) -> Dict[str, Any]:
        """
        Return empty statistics structure (DRY - default values)
        
        Returns:
            Empty statistics dictionary
        """
        return {
            'total_days': 0,
            'wfh_days': 0,
            'office_days': 0,
            'wfh_percentage': 0.0,
            'monthly_breakdown': {}
        }

    def get_wfh_percentage(self) -> float:
        """
        Get calculated WFH percentage
        
        Returns:
            WFH percentage (0-100)
        """
        if not self.statistics:
            self.calculate_statistics()
        
        return self.statistics.get('wfh_percentage', 0.0)

    def generate_report_text(self) -> str:
        """
        Generate text report of WFH statistics
        
        Returns:
            Formatted text report
        """
        if not self.statistics:
            return "No WFH data available"

        lines = [
            "=" * 70,
            "WORK FROM HOME STATISTICS",
            "=" * 70,
            f"Total Work Days:    {self.statistics['total_days']:>6}",
            f"WFH Days:           {self.statistics['wfh_days']:>6}",
            f"Office Days:        {self.statistics['office_days']:>6}",
            f"WFH Percentage:     {self.statistics['wfh_percentage']:>6.2f}%",
            "",
            "MONTHLY BREAKDOWN",
            "-" * 70
        ]

        # Add monthly breakdown
        monthly = self.statistics.get('monthly_breakdown', {})
        for month in sorted(monthly.keys()):
            stats = monthly[month]
            try:
                month_name = datetime.strptime(month + "-01", '%Y-%m-%d').strftime('%B %Y')
            except:
                month_name = month
            
            lines.append(
                f"{month_name:20} {stats['wfh']:>3} WFH / {stats['total']:>3} total "
                f"({stats['percentage']:>5.1f}%)"
            )

        lines.append("=" * 70)
        
        return "\n".join(lines)

    def get_data_for_export(self) -> List[Dict[str, Any]]:
        """
        Get WFH data formatted for export
        
        Returns:
            List of WFH entries ready for export
        """
        return self.wfh_data.copy()

    def __repr__(self) -> str:
        """String representation"""
        return f"WFHProcessor(entries={len(self.wfh_data)}, wfh_pct={self.get_wfh_percentage():.1f}%)"
