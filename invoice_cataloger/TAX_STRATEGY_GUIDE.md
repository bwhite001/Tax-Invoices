# Tax Strategy Guide

## 📋 Overview

The Invoice Cataloger uses the **Strategy Pattern** for tax calculations, allowing you to plug in different tax calculation strategies without modifying the core code. This follows the **Open/Closed Principle** - open for extension, closed for modification.

## 🎯 What is a Tax Strategy?

A tax strategy defines **how** to calculate tax deductions for different expense categories. Different strategies can implement different rules, thresholds, and calculation methods.

### Built-in Strategies

1. **ATO Strategy** - Australian Taxation Office compliant calculations
2. **Custom Strategy** - User-defined rules (coming soon)

---

## 🇦🇺 ATO Strategy

### Overview

The ATO Strategy implements Australian Taxation Office guidelines for work-related expense deductions, specifically tailored for Software Developers and IT professionals.

### Features

✅ **Externalized Rules** - Rules stored in `tax/rules/ato_rules.json`
✅ **Category-Specific Calculations** - Different rules for each expense type
✅ **Work-Use Percentage** - Applies work-use % where appropriate
✅ **Threshold Support** - Handles $300 threshold for equipment
✅ **Depreciation Calculations** - Automatic depreciation for expensive items
✅ **ATO References** - Includes ATO reference links for each category

### Supported Categories

| Category | Claim Method | Work-Use % | Threshold | Depreciation |
|----------|-------------|------------|-----------|--------------|
| Electricity | Actual Cost | ✅ Yes | None | No |
| Internet | Actual Cost | ✅ Yes | None | No |
| Phone & Mobile | Actual Cost | ✅ Yes | None | No |
| Software & Subscriptions | Actual Cost | ✅ Yes | None | No |
| Computer Equipment | Actual Cost / Depreciation | ✅ Yes | $300 | 3 years |
| Professional Development | Full Deduction | ❌ No | None | No |
| Professional Membership | Full Deduction | ❌ No | None | No |
| Office Supplies | Actual Cost | ✅ Yes | None | No |
| Communication Tools | Actual Cost | ✅ Yes | None | No |
| Other | Manual Review | ✅ Yes | None | No |

### Rule Structure

Each category in `ato_rules.json` has the following structure:

```json
{
  "Electricity": {
    "claim_method": "Actual Cost Method",
    "work_use_applicable": true,
    "threshold": null,
    "depreciation_years": null,
    "claim_notes": "Calculate based on work-use percentage of total electricity costs",
    "ato_reference": "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/home-office-expenses",
    "required_documentation": [
      "Electricity bills",
      "Work from home diary or timesheet"
    ]
  }
}
```

### Calculation Examples

#### Example 1: Electricity (Simple Work-Use)

**Invoice**: $200 electricity bill
**Work-Use %**: 60%

**Calculation**:
```
Deductible Amount = $200 × 60% = $120
Claim Method: Actual Cost Method (60% work use)
```

#### Example 2: Computer Equipment (Under $300)

**Invoice**: $250 keyboard
**Work-Use %**: 60%

**Calculation**:
```
Deductible Amount = $250 × 60% = $150
Claim Method: Immediate Deduction (Under $300)
```

#### Example 3: Computer Equipment (Over $300)

**Invoice**: $2,000 laptop
**Work-Use %**: 60%
**Depreciation**: 3 years

**Calculation**:
```
Work-Use Amount = $2,000 × 60% = $1,200
Annual Deduction = $1,200 / 3 years = $400
Claim Method: Decline in Value (Over $300 - Depreciation)
```

#### Example 4: Professional Development (Full Deduction)

**Invoice**: $500 online course
**Work-Use %**: N/A (not applicable)

**Calculation**:
```
Deductible Amount = $500 × 100% = $500
Claim Method: Full Deduction (100%)
```

---

## 🔧 Using ATO Strategy

### With Invoice Cataloger

```bash
# ATO strategy is the default
python invoice_cataloger.py --financial-year 2024-2025

# Explicitly specify ATO strategy
python invoice_cataloger.py --financial-year 2024-2025 --tax-strategy ato
```

### With Standalone Tax Calculator

```bash
# ATO strategy is the default
python tax_calculator_cli.py --catalog catalog.csv --output tax_report.csv

# Explicitly specify ATO strategy
python tax_calculator_cli.py --catalog catalog.csv --strategy ato --output tax_report.csv
```

### Programmatic Usage

```python
from tax import TaxCalculator, ATOStrategy
from catalog import CatalogLoader

# Load catalog
loader = CatalogLoader()
catalog = loader.load_from_csv("catalog.csv")

# Create tax calculator with ATO strategy
strategy = ATOStrategy()
calculator = TaxCalculator(strategy, work_use_percentage=60)

# Calculate deductions
tax_entries = calculator.calculate_deductions(catalog)
```

---

## 🎨 Creating Custom Strategies

### Step 1: Create Strategy Class

Create a new file `tax/strategies/custom_strategy.py`:

```python
"""
Custom Tax Strategy

Implement your own tax calculation rules.
"""
from typing import Dict, Any
from .base_strategy import TaxStrategy


class CustomStrategy(TaxStrategy):
    """
    Custom tax calculation strategy
    
    Implement your own rules here.
    """
    
    def __init__(self, rules: Dict[str, Any] = None):
        """Initialize with custom rules"""
        if rules is None:
            # Load your custom rules
            rules = self._load_custom_rules()
        
        super().__init__(rules)
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "Custom"
    
    def calculate_deduction(self, invoice_data: Dict[str, Any], 
                          category: str, 
                          work_use_percentage: float) -> Dict[str, Any]:
        """
        Calculate deduction using custom rules
        
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
            # No rule found, return manual review
            return self._create_manual_review_deduction(
                category, total_amount, work_use_percentage
            )
        
        # Implement your custom calculation logic here
        # Example: Simple percentage-based calculation
        deductible_amount = total_amount * (work_use_percentage / 100)
        
        return self.format_deduction_result(
            category=category,
            total_amount=total_amount,
            work_use_percentage=work_use_percentage,
            deductible_amount=deductible_amount,
            claim_method=category_rule.get('claim_method', 'Custom Method'),
            claim_notes=category_rule.get('claim_notes', ''),
            ato_reference=category_rule.get('reference', ''),
            required_docs=category_rule.get('required_documentation', [])
        )
    
    def _load_custom_rules(self) -> Dict[str, Any]:
        """Load custom rules from file or define here"""
        return {
            "Software": {
                "claim_method": "Custom Method",
                "work_use_applicable": True,
                "claim_notes": "Custom calculation for software",
                "reference": "Your reference",
                "required_documentation": ["Invoice", "Usage log"]
            }
            # Add more categories...
        }
    
    def _create_manual_review_deduction(self, category: str, 
                                       total_amount: float,
                                       work_use_percentage: float) -> Dict[str, Any]:
        """Create deduction entry for manual review"""
        return self.format_deduction_result(
            category=category,
            total_amount=total_amount,
            work_use_percentage=work_use_percentage,
            deductible_amount=0.00,
            claim_method="Manual Review Required",
            claim_notes=f"No custom rule found for category '{category}'",
            ato_reference="N/A",
            required_docs=["Full documentation"]
        )
```

### Step 2: Create Custom Rules File

Create `tax/rules/custom_rules.json`:

```json
{
  "Software": {
    "claim_method": "Custom Method",
    "work_use_applicable": true,
    "threshold": null,
    "depreciation_years": null,
    "claim_notes": "Custom calculation for software expenses",
    "reference": "Your tax authority reference",
    "required_documentation": [
      "Invoice",
      "Usage log"
    ]
  },
  "Hardware": {
    "claim_method": "Custom Depreciation",
    "work_use_applicable": true,
    "threshold": 500,
    "depreciation_years": 5,
    "claim_notes": "Custom depreciation schedule",
    "reference": "Your tax authority reference",
    "required_documentation": [
      "Invoice",
      "Asset register"
    ]
  }
}
```

### Step 3: Use Custom Strategy

```python
from tax import TaxCalculator
from tax.strategies.custom_strategy import CustomStrategy
from catalog import CatalogLoader

# Load catalog
loader = CatalogLoader()
catalog = loader.load_from_csv("catalog.csv")

# Create tax calculator with custom strategy
strategy = CustomStrategy()
calculator = TaxCalculator(strategy, work_use_percentage=60)

# Calculate deductions
tax_entries = calculator.calculate_deductions(catalog)
```

---

## 📝 Rule JSON Format

### Complete Rule Structure

```json
{
  "category_name": {
    "claim_method": "string",           // How to claim (e.g., "Actual Cost Method")
    "work_use_applicable": boolean,     // Whether work-use % applies
    "threshold": number or null,        // Threshold amount (e.g., 300 for equipment)
    "depreciation_years": number or null, // Years to depreciate over
    "claim_notes": "string",            // Notes about claiming
    "ato_reference": "string",          // Reference URL or code
    "required_documentation": [         // Required documents
      "string",
      "string"
    ]
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim_method` | string | Yes | How to claim the deduction |
| `work_use_applicable` | boolean | Yes | Whether work-use % applies |
| `threshold` | number/null | No | Threshold for immediate deduction |
| `depreciation_years` | number/null | No | Years to depreciate over |
| `claim_notes` | string | No | Additional notes |
| `ato_reference` | string | No | Reference link or code |
| `required_documentation` | array | No | Required documents |

### Example Rules

#### Simple Category (No Threshold)

```json
{
  "Internet": {
    "claim_method": "Actual Cost Method",
    "work_use_applicable": true,
    "threshold": null,
    "depreciation_years": null,
    "claim_notes": "Claim work-use portion of internet costs",
    "ato_reference": "https://www.ato.gov.au/...",
    "required_documentation": [
      "Internet bills",
      "Work diary"
    ]
  }
}
```

#### Category with Threshold

```json
{
  "Computer Equipment": {
    "claim_method": "Actual Cost Method / Depreciation",
    "work_use_applicable": true,
    "threshold": 300,
    "depreciation_years": 3,
    "claim_notes": "Under $300: immediate deduction. Over $300: depreciate over 3 years",
    "ato_reference": "https://www.ato.gov.au/...",
    "required_documentation": [
      "Invoice",
      "Asset register (if over $300)"
    ]
  }
}
```

#### Full Deduction Category

```json
{
  "Professional Development": {
    "claim_method": "Full Deduction (100%)",
    "work_use_applicable": false,
    "threshold": null,
    "depreciation_years": null,
    "claim_notes": "Directly related to current employment",
    "ato_reference": "https://www.ato.gov.au/...",
    "required_documentation": [
      "Course invoice",
      "Certificate of completion"
    ]
  }
}
```

---

## 🔍 Strategy Comparison

### ATO Strategy vs Custom Strategy

| Feature | ATO Strategy | Custom Strategy |
|---------|-------------|-----------------|
| **Rules Source** | `ato_rules.json` | Your custom rules file |
| **Compliance** | ATO compliant | Your jurisdiction |
| **Categories** | 10+ predefined | Define your own |
| **Thresholds** | ATO thresholds | Your thresholds |
| **Depreciation** | ATO schedules | Your schedules |
| **Maintenance** | Updated with ATO changes | You maintain |

---

## 💡 Best Practices

### 1. Rule Organization
- Keep rules in separate JSON files
- Use clear, descriptive category names
- Document calculation methods

### 2. Validation
- Validate rules on load
- Check for required fields
- Test with sample data

### 3. Documentation
- Document your custom rules
- Include references to tax authority
- Explain calculation methods

### 4. Testing
- Test with various invoice amounts
- Test threshold boundaries
- Test work-use percentage calculations

### 5. Maintenance
- Review rules annually
- Update for tax law changes
- Keep audit trail of changes

---

## 🛠️ Troubleshooting

### Error: "No rule found for category"

**Problem**: Category not defined in rules file

**Solution**:
```json
// Add rule for the category
{
  "YourCategory": {
    "claim_method": "Actual Cost Method",
    "work_use_applicable": true,
    // ... other fields
  }
}
```

### Error: "Invalid rule structure"

**Problem**: Rule missing required fields

**Solution**:
```json
// Ensure all required fields are present
{
  "Category": {
    "claim_method": "Required",
    "work_use_applicable": true  // Required
  }
}
```

### Warning: "Rule validation failed"

**Problem**: Rule has invalid values

**Solution**:
- Check `work_use_applicable` is boolean
- Check `threshold` is number or null
- Check `depreciation_years` is number or null

---

## 📚 Additional Resources

- **ATO Website**: https://www.ato.gov.au
- **Work Expenses Guide**: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim
- **Home Office Expenses**: https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/home-office-expenses

---

## ⚖️ Disclaimer

This guide is for informational purposes only. Tax laws vary by jurisdiction and change over time. Always consult with a qualified tax professional for advice specific to your situation.

---

**Last Updated**: October 2024
**Version**: 2.0
