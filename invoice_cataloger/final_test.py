"""Final comprehensive test for vendor overrides"""
import json
from config import Config
from processors.categorizer import ExpenseCategorizer

print("=" * 80)
print("VENDOR OVERRIDE COMPREHENSIVE TEST")
print("=" * 80)

# Test 1: Load vendor overrides
print("\n[TEST 1] Loading vendor overrides...")
config = Config()
overrides_data = config.load_vendor_overrides()
overrides = overrides_data.get('overrides', [])
print(f"✓ Loaded {len(overrides)} vendor overrides")

# Test 2: Initialize categorizer
print("\n[TEST 2] Initializing categorizer with overrides...")
categorizer = ExpenseCategorizer(vendor_overrides=overrides)
print("✓ Categorizer initialized successfully")

# Test 3: Test vendor override matching
print("\n[TEST 3] Testing vendor override matching...")
test_cases = [
    ('Superloop Broadband Pty Ltd', 'Internet'),
    ('SUPERLOOP LIMITED', 'Internet'),
    ('amaysim Mobile Pty Ltd', 'Phone & Mobile'),
    ('AGL Energy', 'Electricity'),
    ('Ampol Energy (Retail) Pty Ltd', 'Electricity'),
    ('JetBrains s.r.o.', 'Software & Subscriptions'),
    ('GitHub', 'Software & Subscriptions'),
]

passed = 0
failed = 0

for vendor, expected in test_cases:
    result = categorizer.categorize(vendor, '', [])
    if result == expected:
        print(f"  ✓ {vendor:40} -> {result}")
        passed += 1
    else:
        print(f"  ✗ {vendor:40} -> {result} (expected: {expected})")
        failed += 1

print(f"\nOverride Tests: {passed}/{len(test_cases)} passed")

# Test 4: Test keyword-based categorization (non-override vendors)
print("\n[TEST 4] Testing keyword-based categorization...")
keyword_tests = [
    ('Woolworths', 'Food & Groceries'),
    ('JB Hi-Fi', 'Electronics'),
    ('Bunnings', 'Home & Garden'),
]

for vendor, expected in keyword_tests:
    result = categorizer.categorize(vendor, '', [])
    if result == expected:
        print(f"  ✓ {vendor:40} -> {result}")
        passed += 1
    else:
        print(f"  ✗ {vendor:40} -> {result} (expected: {expected})")
        failed += 1

print(f"\nKeyword Tests: {passed - len(test_cases)}/{len(keyword_tests)} passed")

# Test 5: Edge cases
print("\n[TEST 5] Testing edge cases...")
edge_tests = [
    ('', 'Other', 'Empty string'),
    ('Unknown Vendor XYZ', 'Other', 'Unknown vendor'),
]

for vendor, expected, desc in edge_tests:
    result = categorizer.categorize(vendor, '', [])
    if result == expected:
        print(f"  ✓ {desc:40} -> {result}")
        passed += 1
    else:
        print(f"  ✗ {desc:40} -> {result} (expected: {expected})")
        failed += 1

# Final summary
print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)
total_tests = len(test_cases) + len(keyword_tests) + len(edge_tests)
print(f"Total: {passed}/{total_tests} tests passed")

if failed == 0:
    print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
else:
    print(f"\n✗ {failed} test(s) failed")

print("\n" + "=" * 80)
