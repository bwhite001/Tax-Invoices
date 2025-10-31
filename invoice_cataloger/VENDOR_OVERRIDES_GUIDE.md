# Vendor Override Configuration Guide

## Overview

The Vendor Override feature allows you to specify fixed categories for specific vendors, ensuring consistent categorization regardless of invoice content. This is particularly useful for vendors that provide multiple types of services or when the AI categorization is inconsistent.

## How It Works

1. **Priority System**: Vendor overrides are checked FIRST before keyword-based categorization
2. **Case-Insensitive Matching**: Vendor patterns match regardless of case
3. **Partial Matching**: Pattern "superloop" matches "Superloop Limited", "Superloop Broadband Pty Ltd", etc.
4. **First Match Wins**: The first matching override rule is applied

## Configuration File

The vendor overrides are stored in `invoice_cataloger/vendor_overrides.json`

### File Structure

```json
{
  "overrides": [
    {
      "vendor_pattern": "superloop",
      "category": "Internet",
      "notes": "Internet and NBN services",
      "enabled": true
    }
  ],
  "available_categories": [...]
}
```

### Fields

- **vendor_pattern** (required): Text to match in vendor name (case-insensitive, partial match)
- **category** (required): Must be one of the available ATO categories
- **notes** (optional): Description for documentation purposes
- **enabled** (optional): Set to `false` to temporarily disable a rule (default: `true`)

## Available Categories

The following categories are available for use:

- Food & Groceries
- Electronics
- Software & Subscriptions
- Computer Equipment
- Electricity
- Internet
- Phone & Mobile
- Professional Development
- Professional Membership
- Office Supplies
- Communication Tools
- Transportation
- Clothing & Apparel
- Health & Medical
- Home & Garden
- Entertainment & Media
- Books & Publications
- Insurance
- Banking & Finance
- Utilities & Services
- Other

## Pre-Configured Vendors

The following vendors are pre-configured:

### Internet & Telecommunications
- **Superloop** → Internet
- **Telstra** → Internet
- **Optus** → Internet
- **amaysim** → Phone & Mobile

### Power & Electricity
- **AGL** → Electricity
- **AMPOL** → Electricity
- **Origin Energy** → Electricity
- **Energex** → Electricity
- **Ergon** → Electricity

### Software & Development
- **JetBrains** → Software & Subscriptions
- **GitHub** → Software & Subscriptions
- **Microsoft** → Software & Subscriptions
- **Adobe** → Software & Subscriptions
- **AWS / Amazon Web Services** → Software & Subscriptions

## Adding New Vendor Overrides

### Example 1: Add a new vendor

```json
{
  "vendor_pattern": "netflix",
  "category": "Entertainment & Media",
  "notes": "Streaming service",
  "enabled": true
}
```

### Example 2: Multiple patterns for same vendor

```json
{
  "vendor_pattern": "amazon web services",
  "category": "Software & Subscriptions",
  "notes": "AWS cloud services",
  "enabled": true
},
{
  "vendor_pattern": "aws",
  "category": "Software & Subscriptions",
  "notes": "AWS cloud services (short form)",
  "enabled": true
}
```

### Example 3: Temporarily disable a rule

```json
{
  "vendor_pattern": "superloop",
  "category": "Internet",
  "notes": "Internet and NBN services",
  "enabled": false
}
```

## Best Practices

1. **Use Specific Patterns**: Use the most specific vendor name that will match all variations
   - Good: "superloop" (matches all Superloop entities)
   - Avoid: "super" (too generic, might match unrelated vendors)

2. **Order Matters**: Place more specific patterns before generic ones
   ```json
   [
     {"vendor_pattern": "amazon web services", "category": "Software & Subscriptions"},
     {"vendor_pattern": "amazon", "category": "Electronics"}
   ]
   ```

3. **Test Your Patterns**: After adding new rules, test with a few invoices to ensure correct matching

4. **Document Your Rules**: Use the `notes` field to explain why a particular categorization was chosen

5. **Review Regularly**: Periodically review your overrides to ensure they're still accurate

## Troubleshooting

### Override Not Working

1. **Check the pattern**: Ensure the pattern appears in the vendor name
2. **Check enabled status**: Verify `"enabled": true`
3. **Check category name**: Must exactly match an available category
4. **Check JSON syntax**: Ensure valid JSON (no trailing commas, proper quotes)

### Multiple Matches

If a vendor name matches multiple patterns, the FIRST matching rule is applied. Reorder your rules if needed.

### Case Sensitivity

Vendor matching is case-insensitive. "SUPERLOOP", "Superloop", and "superloop" all match the pattern "superloop".

## Examples from Log Analysis

Based on the processing log, here are examples of how overrides improve categorization:

### Before Overrides
- Superloop invoices: Sometimes "Internet", sometimes "Software & Subscriptions"
- amaysim invoices: Varies between "Internet", "Phone & Mobile", "Software & Subscriptions"
- AMPOL invoices: Inconsistent categorization

### After Overrides
- **All Superloop invoices** → "Internet" (consistent)
- **All amaysim invoices** → "Phone & Mobile" (consistent)
- **All AMPOL invoices** → "Electricity" (consistent)
- **All AGL invoices** → "Electricity" (consistent)

## Testing Your Configuration

After modifying `vendor_overrides.json`, run the invoice cataloger:

```bash
cd invoice_cataloger
python invoice_cataloger.py --financial-year 2024-2025
```

The system will automatically load and apply your vendor overrides.

## Support

If you encounter issues with vendor overrides:

1. Check the log file for any warnings about loading vendor overrides
2. Validate your JSON syntax using a JSON validator
3. Ensure category names match exactly (case-sensitive for categories)
4. Review the "available_categories" list in the configuration file

## Version History

- **v1.0** (2024-10-31): Initial vendor override feature
  - Case-insensitive partial matching
  - Priority over keyword-based categorization
  - Enable/disable individual rules
  - Pre-configured common Australian vendors
