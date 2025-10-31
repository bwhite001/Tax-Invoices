"""Test script for vendor override functionality"""
from config import Config
from processors import ExpenseCategorizer

# Load config and overrides
config = Config()
overrides_data = config.load_vendor_overrides()
overrides = overrides_data.get('overrides', [])

print(f"✓ Loaded {len(overrides)} vendor overrides\n")

# Initialize categorizer with overrides
categorizer = ExpenseCategorizer(vendor_overrides=overrides)

# Test cases: (vendor_name, expected_category)
test_cases = [
    # Case-insensitive matching
    ('Superloop Broadband Pty Ltd', 'Internet'),
    ('SUPERLOOP LIMITED', 'Internet'),
    ('superloop', 'Internet'),
    
    # Partial matching
    ('amaysim Mobile Pty Ltd', 'Phone & Mobile'),
    ('Amaysim', 'Phone & Mobile'),
    
    # Power companies
    ('AGL Energy', 'Electricity'),
    ('Ampol Energy (Retail) Pty Ltd', 'Electricity'),
    ('Origin Energy', 'Electricity'),
    
    # Software vendors
    ('JetBrains s.r.o.', 'Software & Subscriptions'),
    ('GitHub', 'Software & Subscriptions'),
    ('Microsoft', 'Software & Subscriptions'),
    ('Adobe', 'Software & Subscriptions'),
    
    # Telcos
    ('Telstra', 'Internet'),
    ('Optus', 'Internet'),
    
    # Non-override vendor (should use keyword matching)
    ('Woolworths', 'Food & Groceries'),
    ('JB Hi-Fi', 'Electronics'),
    
    # Unknown vendor
    ('Random Unknown Vendor', 'Other'),
]

print("Testing Vendor Categorization:")
print("=" * 80)

passed = 0
failed = 0

for vendor_name, expected_category in test_cases:
    result = categorizer.categorize(vendor_name, '', [])
    status = '✓' if result == expected_category else '✗'
    
    if result == expected_category:
        passed += 1
    else:
        failed += 1
    
    print(f"{status} {vendor_name:45} -> {result:30} (expected: {expected_category})")

print("=" * 80)
print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")

if failed == 0:
    print("✓ All tests passed!")
else:
    print(f"✗ {failed} test(s) failed")

# Test edge cases
print("\n" + "=" * 80)
print("Testing Edge Cases:")
print("=" * 80)

edge_cases = [
    ('', 'Other', 'Empty vendor name'),
    (None, 'Other', 'None vendor name'),
    ('   ', 'Other', 'Whitespace only'),
]

for vendor_name, expected, description in edge_cases:
    try:
        result = categorizer.categorize(vendor_name or '', '', [])
        status = '✓' if result == expected else '✗'
        print(f"{status} {description:45} -> {result}")
    except Exception as e:
        print(f"✗ {description:45} -> ERROR: {e}")

print("\n✓ Testing complete!")
