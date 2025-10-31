"""Quick test for vendor override functionality"""
import sys
sys.path.insert(0, '.')

from config import Config
from processors.categorizer import ExpenseCategorizer

print("Loading config...")
config = Config()
overrides_data = config.load_vendor_overrides()
overrides = overrides_data.get('overrides', [])
print(f"Loaded {len(overrides)} overrides")

print("\nInitializing categorizer...")
categorizer = ExpenseCategorizer(vendor_overrides=overrides)

print("\nTesting categorization:")
tests = [
    'Superloop Broadband Pty Ltd',
    'amaysim Mobile Pty Ltd',
    'AGL Energy',
    'Ampol Energy',
    'JetBrains',
    'Woolworths'
]

for vendor in tests:
    category = categorizer.categorize(vendor, '', [])
    print(f"  {vendor:35} -> {category}")

print("\nTest complete!")
