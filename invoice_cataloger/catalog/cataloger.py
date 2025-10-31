"""
Pure Invoice Cataloger - Extraction and Categorization Only

This module handles invoice cataloging WITHOUT tax calculations.
Follows Single Responsibility Principle (SRP).
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm

# Import from parent modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import Config
from utils import get_logger, CacheManager, FailedFilesManager
from extractors import PDFExtractor, ImageExtractor, DocumentExtractor, EmailExtractor
from processors import LLMProcessor, ExpenseCategorizer


class InvoiceCataloger:
    """
    Pure invoice cataloger - extracts and categorizes invoices.
    
    Responsibilities:
    - Extract text from various file formats
    - Process with LLM to extract invoice data
    - Categorize expenses
    - Track processing status
    
    Does NOT:
    - Calculate tax deductions
    - Apply ATO rules
    - Calculate work-use percentages
    """
    
    def __init__(self, config: Config):
        """
        Initialize cataloger with configuration
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger()
        
        # Initialize extractors
        self.pdf_extractor = PDFExtractor(
            tesseract_path=config.tesseract_path,
            ocr_languages=config.ocr_languages
        )
        self.image_extractor = ImageExtractor(
            tesseract_path=config.tesseract_path,
            ocr_languages=config.ocr_languages
        )
        self.document_extractor = DocumentExtractor()
        self.email_extractor = EmailExtractor()
        
        # Initialize LLM processor
        self.llm_processor = LLMProcessor(
            api_provider=config.api_provider,
            endpoint=config.lm_studio_endpoint,
            model=config.lm_studio_model,
            openai_api_key=config.openai_api_key,
            openai_model=config.openai_model,
            openai_api_base=config.openai_api_base,
            openrouter_api_key=config.openrouter_api_key,
            openrouter_model=config.openrouter_model,
            openrouter_api_base=config.openrouter_api_base,
            openrouter_app_name=config.openrouter_app_name,
            use_custom_prompt=config.use_custom_prompt,
            custom_extraction_prompt=config.custom_extraction_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout_seconds,
            retry_attempts=config.retry_attempts,
            retry_delay=config.retry_delay_seconds
        )
        
        # Initialize categorizer
        vendor_overrides_data = config.load_vendor_overrides()
        self.categorizer = ExpenseCategorizer(
            vendor_overrides=vendor_overrides_data.get('overrides', [])
        )
        
        # Initialize cache and failed files manager
        self.cache_manager = CacheManager(config.cache_path)
        self.failed_files_manager = FailedFilesManager(config.failed_files_path)
    
    def get_invoice_files(self, retry_failed: bool = False) -> List[Path]:
        """
        Get list of invoice files to process
        
        Args:
            retry_failed: If True, only process previously failed files
        
        Returns:
            List of file paths to process
        """
        self.logger.info(f"Scanning for invoice files in: {self.config.invoice_folder}")
        
        files = []
        for ext in self.config.file_extensions:
            files.extend(self.config.invoice_folder.rglob(f"*{ext}"))
        
        # Filter by retry mode
        if retry_failed:
            self.logger.info("RETRY MODE: Processing only failed files")
            retry_candidates = self.failed_files_manager.get_retry_candidates(
                self.config.max_retry_attempts
            )
            retry_paths = [Path(entry['FilePath']) for entry in retry_candidates]
            files = [f for f in files if f in retry_paths]
            self.logger.info(f"Found {len(files)} failed files to retry")
        
        self.logger.success(f"Total files found: {len(files)}")
        return files
    
    def extract_text(self, file_path: Path) -> tuple[Optional[str], str]:
        """
        Extract text from file based on type
        
        Args:
            file_path: Path to file
        
        Returns:
            Tuple of (extracted_text, extraction_method)
        """
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            return self.pdf_extractor.extract_text(file_path)
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            return self.image_extractor.extract_text(file_path)
        elif ext in ['.doc', '.docx']:
            return self.document_extractor.extract_from_word(file_path)
        elif ext in ['.xls', '.xlsx']:
            return self.document_extractor.extract_from_excel(file_path)
        elif ext == '.eml':
            return self.email_extractor.extract_from_eml(file_path)
        elif ext == '.msg':
            return self.email_extractor.extract_from_msg(file_path)
        else:
            return None, "Unsupported file type"
    
    def is_non_invoice(self, text: str) -> tuple[bool, str]:
        """
        Determine if file is a non-invoice (logo, signature, etc.)
        
        Args:
            text: Extracted text content
        
        Returns:
            Tuple of (is_non_invoice, reason)
        """
        if len(text.strip()) < 50:
            return True, "Too little text content (likely logo/signature)"
        
        return False, ""
    
    def check_missing_fields(self, extracted_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Check for missing critical fields
        
        Args:
            extracted_data: Extracted invoice data
        
        Returns:
            Tuple of (needs_review, list_of_missing_fields)
        """
        missing_fields = []
        
        # Critical fields
        if not extracted_data.get('vendor_name', '').strip():
            missing_fields.append('Vendor Name')
        
        if not extracted_data.get('invoice_date', '').strip():
            missing_fields.append('Invoice Date')
        
        if extracted_data.get('total', 0.0) == 0.0:
            missing_fields.append('Total Amount')
        
        # Bonus field (not critical but noted)
        if not extracted_data.get('invoice_number', '').strip():
            missing_fields.append('Invoice Number (bonus)')
        
        needs_review = len([f for f in missing_fields if '(bonus)' not in f]) > 0
        
        return needs_review, missing_fields
    
    def move_processed_file(self, file_path: Path, category: str, 
                           invoice_date: str) -> Path:
        """
        Move processed file to organized folder structure
        
        Args:
            file_path: Original file path
            category: Expense category
            invoice_date: Invoice date (YYYY-MM-DD format)
        
        Returns:
            New file path after moving
        """
        if not self.config.move_processed_files:
            return file_path
        
        try:
            # Parse date for folder structure
            year_month = "Unknown"
            if invoice_date and len(invoice_date) >= 7:
                year_month = invoice_date[:7]  # YYYY-MM
            
            # Create destination folder
            dest_folder = self.config.output_folder / category / year_month
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Move file
            dest_path = dest_folder / file_path.name
            
            # Handle duplicate filenames
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                dest_path = dest_folder / f"{stem}_{counter}{file_path.suffix}"
                counter += 1
            
            file_path.rename(dest_path)
            return dest_path
        except Exception as e:
            self.logger.error(f"Error moving file: {e}")
            return file_path
    
    def move_non_invoice(self, file_path: Path) -> Path:
        """
        Move non-invoice file to Non-Invoice folder
        
        Args:
            file_path: Original file path
        
        Returns:
            New file path after moving
        """
        try:
            non_invoice_folder = self.config.output_folder / "Non-Invoice"
            non_invoice_folder.mkdir(parents=True, exist_ok=True)
            
            dest_path = non_invoice_folder / file_path.name
            
            # Handle duplicate filenames
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                dest_path = non_invoice_folder / f"{stem}_{counter}{file_path.suffix}"
                counter += 1
            
            file_path.rename(dest_path)
            self.logger.info(f"Moved non-invoice to: {dest_path}")
            return dest_path
        except Exception as e:
            self.logger.error(f"Error moving non-invoice file: {e}")
            return file_path
    
    def process_file(self, file_path: Path, file_index: int, 
                    total_files: int, reprocess: bool = False) -> Optional[Dict[str, Any]]:
        """
        Process a single invoice file (extraction and categorization only)
        
        Args:
            file_path: Path to invoice file
            file_index: Current file index (for progress)
            total_files: Total number of files
            reprocess: If True, ignore cache and reprocess
        
        Returns:
            Dictionary with catalog entry (NO tax calculations)
        """
        self.logger.progress(file_index, total_files, f"Processing: {file_path.name}")
        
        # Calculate file hash
        file_hash = CacheManager.calculate_file_hash(file_path)
        if not file_hash:
            self.logger.error("Could not calculate file hash")
            return None
        
        # Check cache (skip if reprocess mode)
        cached_entry = None if reprocess else self.cache_manager.find_by_hash(file_hash)
        if cached_entry:
            self.logger.warning("DUPLICATE FOUND: File already processed (cached)")
            self.logger.info(f"Original: {cached_entry['FileName']} | Processed: {cached_entry['ProcessedDate']}")
            
            return {
                'FileName': file_path.name,
                'FileType': file_path.suffix.lower(),
                'FilePath': str(file_path),
                'OriginalPath': str(file_path),
                'ProcessedDateTime': datetime.now(),
                'VendorName': cached_entry['ExtractedData'].get('vendor_name', ''),
                'VendorABN': cached_entry['ExtractedData'].get('vendor_abn', ''),
                'InvoiceNumber': cached_entry['ExtractedData'].get('invoice_number', ''),
                'InvoiceDate': cached_entry['ExtractedData'].get('invoice_date', ''),
                'DueDate': cached_entry['ExtractedData'].get('due_date', ''),
                'SubTotal': cached_entry['ExtractedData'].get('subtotal', 0.00),
                'Tax': cached_entry['ExtractedData'].get('tax', 0.00),
                'TotalAmount': cached_entry['ExtractedData'].get('total', 0.00),
                'Currency': cached_entry['ExtractedData'].get('currency', 'AUD'),
                'Category': cached_entry['Category'],
                'ProcessingStatus': 'Cached (Duplicate)',
                'FileHash': file_hash,
                'MovedTo': 'N/A - Duplicate',
                'NeedsManualReview': False,
                'MissingFields': []
            }
        
        # Check if file has failed too many times
        failed_entry = self.failed_files_manager.find_by_path(str(file_path))
        if failed_entry and failed_entry['AttemptCount'] >= self.config.max_retry_attempts:
            self.logger.warning(f"SKIPPED: File has failed {failed_entry['AttemptCount']} times")
            
            return self._create_failed_entry(file_path, file_hash, 
                                            "Skipped - Too many failures",
                                            "Skipped (Max retries exceeded)")
        
        try:
            # Extract text
            text, method = self.extract_text(file_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.warning(f"No text extracted using {method}")
                
                attempt_count = failed_entry['AttemptCount'] + 1 if failed_entry else 1
                self.failed_files_manager.add_failure(
                    str(file_path), file_path.name,
                    f"No text content extracted ({method})",
                    attempt_count
                )
                
                return self._create_failed_entry(file_path, file_hash,
                                                "No text content extracted",
                                                "Failed (No text)")
            
            self.logger.debug(f"Text extracted using {method} ({len(text)} chars)")
            
            # Check if file is a non-invoice
            is_non_invoice, non_invoice_reason = self.is_non_invoice(text)
            if is_non_invoice:
                self.logger.warning(f"NON-INVOICE DETECTED: {non_invoice_reason}")
                
                # Move to Non-Invoice folder
                moved_path = self.move_non_invoice(file_path)
                
                return {
                    'FileName': file_path.name,
                    'FileType': file_path.suffix.lower(),
                    'FilePath': str(moved_path),
                    'OriginalPath': str(file_path),
                    'ProcessedDateTime': datetime.now(),
                    'VendorName': 'N/A',
                    'VendorABN': '',
                    'InvoiceNumber': '',
                    'InvoiceDate': '',
                    'DueDate': '',
                    'SubTotal': 0.00,
                    'Tax': 0.00,
                    'TotalAmount': 0.00,
                    'Currency': 'AUD',
                    'Category': 'Non-Invoice',
                    'ProcessingStatus': 'Non-Invoice',
                    'FileHash': file_hash,
                    'MovedTo': str(moved_path),
                    'NeedsManualReview': False,
                    'MissingFields': []
                }
            
            # Extract data using LLM
            extracted_data = self.llm_processor.extract_invoice_data(text, file_path.name)
            
            if not extracted_data:
                self.logger.warning("Failed to extract data with LLM")
                
                attempt_count = failed_entry['AttemptCount'] + 1 if failed_entry else 1
                self.failed_files_manager.add_failure(
                    str(file_path), file_path.name,
                    "AI extraction failed",
                    attempt_count
                )
                
                return self._create_failed_entry(file_path, file_hash,
                                                "AI extraction failed",
                                                "Failed (AI extraction)")
            
            # Check for missing critical fields
            needs_manual_review, missing_fields = self.check_missing_fields(extracted_data)
            
            # Categorize expense
            category = self.categorizer.categorize(
                extracted_data.get('vendor_name', ''),
                extracted_data.get('description', ''),
                extracted_data.get('line_items', [])
            )
            
            # Log if manual review needed
            if needs_manual_review:
                self.logger.warning(f"NEEDS MANUAL REVIEW: Missing fields: {', '.join(missing_fields)}")
            
            # Move file
            moved_path = self.move_processed_file(
                file_path, category, extracted_data.get('invoice_date', '')
            )
            
            # Add to cache (without tax data)
            self.cache_manager.add_entry(
                file_path.name, file_hash, extracted_data, category, {}
            )
            
            # Remove from failed files if it was there
            if failed_entry:
                self.failed_files_manager.remove_failure(str(file_path))
                self.logger.info("Removed from failed files list (successful retry)")
            
            self.logger.success(f"Cataloged: {extracted_data.get('vendor_name', 'Unknown')} - {category} - ${extracted_data.get('total', 0)}")
            
            # Return catalog entry WITHOUT tax calculations
            return {
                'FileName': file_path.name,
                'FileType': file_path.suffix.lower(),
                'FilePath': str(moved_path),
                'OriginalPath': str(file_path),
                'ProcessedDateTime': datetime.now(),
                'VendorName': extracted_data.get('vendor_name', ''),
                'VendorABN': extracted_data.get('vendor_abn', ''),
                'InvoiceNumber': extracted_data.get('invoice_number', ''),
                'InvoiceDate': extracted_data.get('invoice_date', ''),
                'DueDate': extracted_data.get('due_date', ''),
                'SubTotal': extracted_data.get('subtotal', 0.00),
                'Tax': extracted_data.get('tax', 0.00),
                'TotalAmount': extracted_data.get('total', 0.00),
                'Currency': extracted_data.get('currency', 'AUD'),
                'Category': category,
                'ProcessingStatus': 'Success',
                'FileHash': file_hash,
                'MovedTo': str(moved_path),
                'NeedsManualReview': needs_manual_review,
                'MissingFields': missing_fields
            }
            
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            
            attempt_count = failed_entry['AttemptCount'] + 1 if failed_entry else 1
            self.failed_files_manager.add_failure(
                str(file_path), file_path.name,
                f"Processing error: {str(e)}",
                attempt_count
            )
            
            return self._create_failed_entry(file_path, file_hash,
                                            f"Processing error: {str(e)}",
                                            "Failed (Error)")
    
    def _create_failed_entry(self, file_path: Path, file_hash: str,
                            error_reason: str, status: str) -> Dict[str, Any]:
        """
        Create a failed entry placeholder
        
        Args:
            file_path: Original file path
            file_hash: File hash
            error_reason: Reason for failure
            status: Processing status
        
        Returns:
            Dictionary with failed entry
        """
        return {
            'FileName': file_path.name,
            'FileType': file_path.suffix.lower(),
            'FilePath': str(file_path),
            'OriginalPath': str(file_path),
            'ProcessedDateTime': datetime.now(),
            'VendorName': 'N/A',
            'VendorABN': '',
            'InvoiceNumber': '',
            'InvoiceDate': '',
            'DueDate': '',
            'SubTotal': 0.00,
            'Tax': 0.00,
            'TotalAmount': 0.00,
            'Currency': 'AUD',
            'Category': 'Non-Invoice/Other',
            'ProcessingStatus': status,
            'FileHash': file_hash,
            'MovedTo': 'N/A - Not moved',
            'NeedsManualReview': True,
            'MissingFields': [error_reason]
        }
    
    def catalog_invoices(self, retry_failed: bool = False, 
                        reprocess: bool = False) -> List[Dict[str, Any]]:
        """
        Main cataloging method - process all invoice files
        
        Args:
            retry_failed: If True, only process previously failed files
            reprocess: If True, ignore cache and reprocess all files
        
        Returns:
            List of catalog entries (NO tax calculations)
        """
        self.logger.section("INVOICE CATALOGING (NO TAX CALCULATIONS)")
        
        # Get files to process
        files = self.get_invoice_files(retry_failed)
        
        if not files:
            self.logger.warning("No invoice files found to process")
            return []
        
        # Process files
        catalog_entries = []
        success_count = 0
        fail_count = 0
        cached_count = 0
        skipped_count = 0
        non_invoice_count = 0
        manual_review_count = 0
        
        if reprocess:
            self.logger.info("REPROCESS MODE: Ignoring cache for all files")
        
        for i, file_path in enumerate(files, 1):
            result = self.process_file(file_path, i, len(files), reprocess=reprocess)
            
            if result:
                catalog_entries.append(result)
                
                status = result['ProcessingStatus']
                if status == 'Success':
                    success_count += 1
                elif status == 'Non-Invoice':
                    non_invoice_count += 1
                elif 'Cached' in status:
                    cached_count += 1
                elif 'Skipped' in status:
                    skipped_count += 1
                else:
                    fail_count += 1
                
                # Track manual review needed
                if result.get('NeedsManualReview', False):
                    manual_review_count += 1
        
        # Save cache and failed files
        self.cache_manager.save()
        self.failed_files_manager.save()
        
        # Summary
        self.logger.section("CATALOGING COMPLETE")
        self.logger.success(f"Successful: {success_count} files")
        if non_invoice_count > 0:
            self.logger.info(f"Non-Invoices: {non_invoice_count} files")
        if fail_count > 0:
            self.logger.warning(f"Failed: {fail_count} files")
        self.logger.info(f"Cached (Duplicates): {cached_count} files")
        if skipped_count > 0:
            self.logger.warning(f"Skipped (Max retries): {skipped_count} files")
        if manual_review_count > 0:
            self.logger.warning(f"Manual Review Required: {manual_review_count} files")
        self.logger.success(f"Total cataloged: {len(catalog_entries)} invoices")
        
        return catalog_entries
