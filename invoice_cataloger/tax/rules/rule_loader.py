"""
Rule Loader - Load and validate tax rules from JSON files

Follows Single Responsibility Principle - only loads and validates rules.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Import from parent modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils import get_logger


class RuleLoader:
    """
    Load and validate tax rules from JSON files
    
    Responsibilities:
    - Load rules from JSON files
    - Validate rule structure
    - Cache loaded rules
    - Provide rule access methods
    """
    
    def __init__(self):
        """Initialize rule loader"""
        self.logger = get_logger()
        self._cache = {}
    
    def load_rules(self, rules_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load rules from JSON file
        
        Args:
            rules_path: Path to rules JSON file
        
        Returns:
            Rules dictionary or None if loading fails
        """
        rules_path = Path(rules_path)
        
        # Check cache
        cache_key = str(rules_path.absolute())
        if cache_key in self._cache:
            self.logger.debug(f"Using cached rules: {rules_path.name}")
            return self._cache[cache_key]
        
        # Load from file
        if not rules_path.exists():
            self.logger.error(f"Rules file not found: {rules_path}")
            return None
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            # Validate rules
            is_valid, errors = self.validate_rules(rules)
            if not is_valid:
                self.logger.error(f"Invalid rules file: {rules_path}")
                for error in errors:
                    self.logger.error(f"  - {error}")
                return None
            
            # Cache rules
            self._cache[cache_key] = rules
            
            self.logger.success(f"Loaded rules: {rules_path.name}")
            return rules
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in rules file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
            return None
    
    def validate_rules(self, rules: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate rules structure
        
        Args:
            rules: Rules dictionary
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ['strategy_name', 'categories']
        for field in required_fields:
            if field not in rules:
                errors.append(f"Missing required field: {field}")
        
        # Check categories
        if 'categories' in rules:
            if not isinstance(rules['categories'], dict):
                errors.append("'categories' must be a dictionary")
            else:
                # Validate each category
                for category_name, category_rules in rules['categories'].items():
                    category_errors = self._validate_category(category_name, category_rules)
                    errors.extend(category_errors)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _validate_category(self, category_name: str, 
                          category_rules: Dict[str, Any]) -> list[str]:
        """
        Validate a single category's rules
        
        Args:
            category_name: Category name
            category_rules: Category rules dictionary
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        required_fields = [
            'claim_method',
            'work_use_applicable',
            'ato_reference',
            'required_documentation'
        ]
        
        for field in required_fields:
            if field not in category_rules:
                errors.append(f"Category '{category_name}': Missing field '{field}'")
        
        # Validate field types
        if 'work_use_applicable' in category_rules:
            if not isinstance(category_rules['work_use_applicable'], bool):
                errors.append(f"Category '{category_name}': 'work_use_applicable' must be boolean")
        
        if 'threshold' in category_rules:
            threshold = category_rules['threshold']
            if threshold is not None and not isinstance(threshold, (int, float)):
                errors.append(f"Category '{category_name}': 'threshold' must be number or null")
        
        if 'depreciation_years' in category_rules:
            years = category_rules['depreciation_years']
            if years is not None and not isinstance(years, (int, float)):
                errors.append(f"Category '{category_name}': 'depreciation_years' must be number or null")
        
        if 'required_documentation' in category_rules:
            if not isinstance(category_rules['required_documentation'], list):
                errors.append(f"Category '{category_name}': 'required_documentation' must be a list")
        
        return errors
    
    def get_category_rule(self, rules: Dict[str, Any], 
                         category: str) -> Optional[Dict[str, Any]]:
        """
        Get rule for a specific category
        
        Args:
            rules: Rules dictionary
            category: Category name
        
        Returns:
            Category rule dictionary or None if not found
        """
        if 'categories' not in rules:
            return None
        
        return rules['categories'].get(category)
    
    def get_all_categories(self, rules: Dict[str, Any]) -> list[str]:
        """
        Get list of all categories in rules
        
        Args:
            rules: Rules dictionary
        
        Returns:
            List of category names
        """
        if 'categories' not in rules:
            return []
        
        return list(rules['categories'].keys())
    
    def clear_cache(self):
        """Clear the rules cache"""
        self._cache.clear()
        self.logger.info("Rules cache cleared")
    
    @staticmethod
    def get_default_ato_rules_path() -> Path:
        """
        Get path to default ATO rules file
        
        Returns:
            Path to ato_rules.json
        """
        # Get path relative to this file
        current_file = Path(__file__)
        rules_dir = current_file.parent
        return rules_dir / "ato_rules.json"
