"""
File Processor - Handles individual invoice file processing

Separated from main cataloger for single responsibility.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from config import Config
from utils import get_logger, CacheManager, FailedFilesManager
from extractors import PDFExtractor, ImageExtractor, DocumentExtractor, EmailExtractor
from processors import LLMProcessor, ExpenseCategorizer, DeductionCalculator


class FileProcessor:
    """Process individual invoice files"""
    
    def __init__(self, config: Config, 
                 llm_processor: LLMProcessor,
                 categorizer: ExpenseCategorizer,
                 deduction_calculator: DeductionCalculator,
                 cache_manager: CacheManager,
                 failed_files_manager: FailedFilesManager):
        self.config = config
        self.logger = get_logger()
        
        # Processors
        self.llm_processor = llm_processor
        self.categorizer = categorizer
        self.deduction_calculator = deduction_calculator
        
        # Managers
        self.cache_manager = cache_manager
        self.failed_files_manager = failed_files_manager
        
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
    
    def process_file(self, file_path: Path, file_index: int, 
                    total_files: int, reprocess: bool = False) -> Optional[Dict[str, Any]]:
        """
        Process a single invoice file
        
        Args:
            file_path: Path to the file to process
            file_index: Current file index (for progress tracking)
            total_files: Total number of files to process
            reprocess: If True, ignore cache and reprocess
        
        Returns:
            Dictionary with processed invoice data or None
        """
        self.logger.progress(file_index, total_files, f"Processing: {file_path.name}")
        
        # Calculate file hash
        file_hash = CacheManager.calculate_file_hash(file_path)
        if not file_hash:
            self.logger.error("Could not calculate file hash")
            return None
        
        # Check cache (skip if reprocess mode)
        if not reprocess:
            cached_result = self._check_cache(file_path, file_hash)
            if cached_result:
                return cached_result
        
        # Check if file has failed too many times
        if self._should_skip_failed_file(file_path, file_hash):
            return self._create_failed_entry(
                file_path, file_hash,
                "Skipped - Too many failures",
                "Skipped (Max retries exceeded)"
            )
        
        # Process the file
        try:
            return self._process_file_content(file_path, file_hash)
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            return self._handle_processing_error(file_path, file_hash, str(e))
    
    def _check_cache(self, file_path: Path, file_hash: str) -> Optional[Dict[str, Any]]:
        """Check if file is already in cache"""
        cached_entry = self.cache_manager.find_by_hash(file_hash)
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
                'WorkUsePercentage': cached_entry['Deduction'].get('WorkUsePercentage', 0),
                'DeductibleAmount': cached_entry['Deduction'].get('DeductibleAmount', 0.00),
                'ClaimMethod': cached_entry['Deduction'].get('ClaimMethod', ''),
                'ClaimNotes': cached_entry['Deduction'].get('ClaimNotes', ''),
                'AtoReference': cached_entry['Deduction'].get('AtoReference', ''),
                'RequiresDocumentation': cached_entry['Deduction'].get('RequiresDocumentation', []),
                'ProcessingStatus': 'Cached (Duplicate)',
                'FileHash': file_hash,
                'MovedTo': 'N/A - Duplicate',
                'NeedsMan<create_file>
<path>invoice_cataloger/core/file_processor.py</path>
<content>
"""
File Processor - Handles individual file processing logic

Separated from main cataloger for single responsibility.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from config import Config
from utils import get_logger, CacheManager, FailedFilesManager
from extractors import PDFExtractor, ImageExtractor, DocumentExtractor, EmailExtractor
from processors import LLMProcessor, ExpenseCategorizer, DeductionCalculator


class FileProcessor:
    """Process individual invoice files"""
    
    def __init__(self, config: Config):
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
        
        # Initialize processors
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
        
        # Load vendor overrides and initialize categorizer
        vendor_overrides_data = config.load_vendor_overrides()
        self.categorizer = ExpenseCategorizer(
            vendor_overrides=vendor_overrides_data.get('overrides', [])
        )
        self.deduction_calculator = DeductionCalculator(
            work_use_percentage=config.work_use_percentage,
            fixed_rate_hourly=config.fixed_rate_hourly
        )
        
        # Initialize managers
        self.cache_manager = CacheManager(config.cache_path)
        self.failed_files_manager = FailedFilesManager(config.failed_files_path)
    
    def extract_text(self, file_path: Path) -> tuple[Optional[str], str]:
        """Extract text from file based on type"""
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
    
    def move_processed_file(self, file_path: Path, category: str,
                           invoice_date: str) -> Path:
        """Move processed file to organized folder structure"""
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
        """Move non-invoice file to Non-Invoice folder"""
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
        """Process a single invoice file"""
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
            
            return self._create_cached_entry(file_path, file_hash, cached_entry)
        
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
            
            # Check if file is a non-invoice (logo, signature, etc.)
            is_non_invoice, non_invoice_reason = self._is_non_invoice(None, text)
            if is_non_invoice:
                self.logger.warning(f"NON-INVOICE DETECTED: {non_invoice_reason}")
                
                # Move to Non-Invoice folder
                moved_path = self.move_non_invoice(file_path)
                
                return self._create_non_invoice_entry(file_path, file_hash, moved_path, non_invoice_reason)
            
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
            needs_manual_review, missing_fields = self._check_missing_fields(extracted_data)
            
            # Categorize expense
            category = self.categorizer.categorize(
                extracted_data.get('vendor_name', ''),
                extracted_data.get('description', ''),
                extracted_data.get('line_items', [])
            )
            
            # Calculate deduction
            deduction = self.deduction_calculator.calculate_deduction(
                extracted_data, category
            )
            
            # Log if manual review needed
            if needs_manual_review:
                self.logger.warning(f"NEEDS MANUAL REVIEW: Missing fields: {', '.join(missing_fields)}")
            
            # Move file
            moved_path = self.move_processed_file(
                file_path, category, extracted_data.get('invoice_date', '')
            )
            
            # Add to cache
            self.cache_manager.add_entry(
                file_path.name, file_hash, extracted_data, category, deduction
            )
            
            # Remove from failed files if it was there
            if failed_entry:
                self.failed_files_manager.remove_failure(str(file_path))
                self.logger.info("Removed from failed files list (successful retry)")
            
            self.logger.success(f"Extracted: {extracted_data.get('vendor_name', 'Unknown')} - {category} - ${extracted_data.get('total', 0)}")
            
            return self._create_success_entry(file_path, file_hash, moved_path,
                                             extracted_data, category, deduction,
                                             needs_manual_review, missing_fields)
            
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
    
    def _create_cached_entry(self, file_path: Path, file_hash: str,
                           cached_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Create entry for cached (duplicate) file"""
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
            'WorkUsePercentage': cached_entry['Deduction'].get('WorkUsePercentage', 0),
            'DeductibleAmount': cached_entry['Deduction'].get('DeductibleAmount', 0.00),
            'ClaimMethod': cached_entry['Deduction'].get('ClaimMethod', ''),
            'ClaimNotes': cached_entry['Deduction'].get('ClaimNotes', ''),
            'AtoReference': cached_entry['Deduction'].get('AtoReference', ''),
            'RequiresDocumentation': cached_entry['Deduction'].get('RequiresDocumentation', []),
            'ProcessingStatus': 'Cached (Duplicate)',
            'FileHash': file_hash,
            'MovedTo': 'N/A - Duplicate',
            'NeedsManualReview': False,
            'MissingFields': []
        }
    
    def _create_non_invoice_entry(self, file_path: Path, file_hash: str,
                                moved_path: Path, reason: str) -> Dict[str, Any]:
        """Create entry for non-invoice file"""
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
            'WorkUsePercentage': 0,
            'DeductibleAmount': 0.00,
            'ClaimMethod': 'Not Applicable',
            'ClaimNotes': reason,
            'AtoReference': 'N/A',
            'RequiresDocumentation': [],
            'ProcessingStatus': 'Non-Invoice',
            'FileHash': file_hash,
            'MovedTo': str(moved_path),
            'NeedsManualReview': False,
            'MissingFields': []
        }
    
    def _create_success_entry(self, file_path: Path, file_hash: str, moved_path: Path,
                            extracted_data: Dict[str, Any], category: str,
                            deduction: Dict[str, Any], needs_manual_review: bool,
                            missing_fields: List[str]) -> Dict[str, Any]:
        """Create entry for successfully processed file"""
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
            'WorkUsePercentage': deduction['WorkUsePercentage'],
            'DeductibleAmount': deduction['DeductibleAmount'],
            'ClaimMethod': deduction['ClaimMethod'],
            'ClaimNotes': deduction['ClaimNotes'],
            'AtoReference': deduction['AtoReference'],
            'RequiresDocumentation': deduction['RequiresDocumentation'],
            'ProcessingStatus': 'Success',
            'FileHash': file_hash,
            'MovedTo': str(moved_path),
            'NeedsManualReview': needs_manual_review,
            'MissingFields': missing_fields
        }
    
    def _create_failed_entry(self, file_path: Path, file_hash: str,
                            error_reason: str, status: str) -> Dict[str, Any]:
        """Create failed entry placeholder"""
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
            'WorkUsePercentage': 0,
            'DeductibleAmount': 0.00,
            'ClaimMethod': 'Not Applicable',
            'ClaimNotes': error_reason,
            'AtoReference': 'N/A',
            'RequiresDocumentation': ['Manual review required'],
            'ProcessingStatus': status,
            'FileHash': file_hash,
            'MovedTo': 'N/A - Not moved',
            'NeedsManualReview': True,
            'MissingFields': []
        }
    
    def _is_non_invoice(self, extracted_data: Optional[Dict[str, Any]], text: str) -> tuple[bool, str]:
        """
        Determine if file is a non-invoice (logo, signature, etc.)
        
        Returns:
            (is_non_invoice, reason)
        """
        # Check if extraction failed completely
        if not extracted_data:
            if len(text.strip()) < 50:
                return True, "Too little text content (likely logo/signature)"
            return False, ""
        
        # Check for critical missing fields
        vendor = extracted_data.get('vendor_name', '').strip()
        total = extracted_data.get('total', 0.0)
        
        # If no vendor and no amount, likely not an invoice
        if not vendor and total == 0.0:
            return True, "No vendor name and no amount (likely non-invoice image)"
        
        return False, ""
    
    def _check_missing_fields(self, extracted_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Check for missing critical fields
        
        Returns:
            (needs_review, list_of_missing_fields)
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
