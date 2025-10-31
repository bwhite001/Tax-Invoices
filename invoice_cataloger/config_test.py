"""Test with actual config loading"""
from config import Config
from processors.categorizer import ExpenseCategorizer

print("Loading config and overrides...")
config = Config()
overrides_data = config.load_vendor_overrides()
categorizer = ExpenseCategorizer(overrides_data['overrides'])

print(f"Loaded {len(overrides_data['overrides'])} overrides\n")

vendors = ['Superloop', 'JetBrains', 'Microsoft', 'GitHub', 'AWS', 'Telstra', 'Origin Energy']

print("Testing with config-loaded overrides:")
for vendor in vendors:
    category = categorizer.categorize(vendor, '', [])
    print(f"  {vendor:20} -> {category}")

print("\nConfig-based test complete!")
