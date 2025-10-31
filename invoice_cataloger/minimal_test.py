"""Minimal test without config loading"""
from processors.categorizer import ExpenseCategorizer

# Manually create test overrides
test_overrides = [
    {"vendor_pattern": "superloop", "category": "Internet", "enabled": True},
    {"vendor_pattern": "amaysim", "category": "Phone & Mobile", "enabled": True},
    {"vendor_pattern": "agl", "category": "Electricity", "enabled": True},
    {"vendor_pattern": "ampol", "category": "Electricity", "enabled": True},
]

print("Testing vendor overrides...")
cat = ExpenseCategorizer(vendor_overrides=test_overrides)

tests = [
    ("Superloop Ltd", "Internet"),
    ("amaysim Mobile", "Phone & Mobile"),
    ("AGL Energy", "Electricity"),
    ("Ampol Energy", "Electricity"),
    ("Woolworths", "Food & Groceries"),
]

for vendor, expected in tests:
    result = cat.categorize(vendor, "", [])
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: {vendor:30} -> {result:30} (expected: {expected})")

print("\nTest complete!")
