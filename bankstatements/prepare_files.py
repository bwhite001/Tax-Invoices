"""
Prepare bank statement files for processing by adding 'zip_' prefix
"""
import shutil
from pathlib import Path

# Source and destination folders
source_folder = Path("G:/My Drive/Tax Invoices/Statements/FY2024-FY2025")
dest_folder = Path("G:/My Drive/Tax Invoices/Statements/FY2024-FY2025/temp_processing")

# Ensure destination exists
dest_folder.mkdir(parents=True, exist_ok=True)

# Copy all PDF files with zip_ prefix
pdf_files = list(source_folder.glob("*.pdf"))

print(f"Found {len(pdf_files)} PDF files to copy")
print("="*60)

copied_count = 0
for pdf_file in pdf_files:
    # Create new filename with zip_ prefix
    new_name = f"zip_{pdf_file.name}"
    dest_path = dest_folder / new_name
    
    # Copy file
    try:
        shutil.copy2(pdf_file, dest_path)
        print(f"✓ Copied: {pdf_file.name} -> {new_name}")
        copied_count += 1
    except Exception as e:
        print(f"✗ Error copying {pdf_file.name}: {e}")

print("="*60)
print(f"Successfully copied {copied_count} out of {len(pdf_files)} files")
print(f"Files are ready in: {dest_folder}")
