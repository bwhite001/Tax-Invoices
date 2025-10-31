"""
Professional Invoice Cataloging System using LM Studio (Local LLM)
For ATO-Compliant Work Expense Tracking - Software Developers

Python implementation with robust PDF extraction
"""
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from tqdm import tqdm

# Import modules
from config import Config
from utils import setup_logger, get_logger, CacheManager, FailedFilesManager
from extractors import PDFExtractor, ImageExtractor, DocumentExtractor, EmailExtractor
from processors import LLMProcessor, ExpenseCategorizer, DeductionCalculator
from exporters import ExcelExporter, CSVExporter


class InvoiceCataloger:
    """Main invoice cataloging system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        
        # Initialize components
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
        
        # Initialize LLM processor based on API provider
        self.llm_processor = LLMProcessor(
            api_provider=config.api_provider,
            # LM Studio params
            endpoint=config.lm_studio_endpoint,
            model=config.lm_studio_model,
            # OpenAI params
            openai_api_key=config.openai_api_key,
            openai_model=config.openai_model,
            openai_api_base=config.openai_api_base,
            # OpenRouter params
            openrouter_api_key=config.openrouter_api_key,
            openrouter_model=config.openrouter_model,
            openrouter_api_base=config.openrouter_api_base,
            openrouter_app_name=config.openrouter_app_name,
            # Custom prompt
            use_custom_prompt=config.use_custom_prompt,
            custom_extraction_prompt=config.custom_extraction_prompt,
            # Common params
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
        
        self.cache_manager = CacheManager(config.cache_path)
        self.failed_files_manager = FailedFilesManager(config.failed_files_path)
        
        self.excel_exporter = ExcelExporter(config.output_folder)
        self.csv_exporter = CSVExporter(config.output_folder)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.logger.section("CHECKING PREREQUISITES")
        self.logger.info(f"Processing Financial Year: FY{self.config.financial_year}")
        self.logger.info(f"API Provider: {self.config.api_provider.upper()}")
        
        # Validate financial year
        if not self.config.validate_financial_year():
            self.logger.error(f"Invalid financial year format: {self.config.financial_year}")
            self.logger.error("Use format: YYYY-YYYY (e.g., '2024-2025')")
            return False
        
        # Check invoice folder
        if not self.config.invoice_folder.exists():
            self.logger.error(f"Invoice folder not found: {self.config.invoice_folder}")
            self.logger.error("Please create the folder and add invoice files.")
            return False
        
        self.logger.success(f"Invoice folder exists: {self.config.invoice_folder}")
        
        # Create output folders
        self.config.ensure_directories()
        self.logger.success(f"Output folder ready: {self.config.output_folder}")
        
        # Validate API configuration
        api_valid, api_message = self.config.validate_api_config()
        if not api_valid:
            self.logger.error(api_message)
            self.logger.error("Please check your .env file configuration")
            return False
        
        self.logger.success(api_message)
        
        # Test API connection based on provider
        self.logger.info(f"Testing {self.config.api_provider.upper()} connection...")
        
        if self.config.api_provider == "lmstudio":
            success, message = LLMProcessor.test_connection(
                "lmstudio",
                endpoint=self.config.lm_studio_endpoint,
                models_endpoint=self.config.lm_studio_models_endpoint
            )
            
            if not success:
                self.logger.error(message)
                self.logger.error("Please ensure:")
                self.logger.error("  1. LM Studio is running")
                self.logger.error("  2. A model is loaded (e.g., Mistral 7B)")
                self.logger.error("  3. Developer Server is started")
                return False
        
        elif self.config.api_provider == "openai":
            success, message = LLMProcessor.test_connection(
                "openai",
                api_key=self.config.openai_api_key,
                model=self.config.openai_model,
                api_base=self.config.openai_api_base
            )
            
            if not success:
                self.logger.error(message)
                self.logger.error("Please ensure:")
                self.logger.error("  1. OPENAI_API_KEY is set in .env file")
                self.logger.error("  2. API key is valid and has credits")
                self.logger.error("  3. Model name is correct")
                return False
        
        elif self.config.api_provider == "openrouter":
            success, message = LLMProcessor.test_connection(
                "openrouter",
                api_key=self.config.openrouter_api_key,
                model=self.config.openrouter_model,
                api_base=self.config.openrouter_api_base,
                app_name=self.config.openrouter_app_name
            )
            
            if not success:
                self.logger.error(message)
                self.logger.error("Please ensure:")
                self.logger.error("  1. OPENROUTER_API_KEY is set in .env file")
                self.logger.error("  2. API key is valid and has credits")
                self.logger.error("  3. Model name is correct")
                return False
        
        self.logger.success(message)
        
        # Show custom prompt status
        if self.config.use_custom_prompt:
            self.logger.info("Using custom extraction prompt")
        else:
            self.logger.info("Using default optimized extraction prompt")
        
        # Check extraction dependencies
        pdf_ok, pdf_missing = PDFExtractor.check_dependencies()
        if not pdf_ok:
            self.logger.warning("Missing PDF dependencies:")
            for dep in pdf_missing:
                self.logger.warning(f"  - {dep}")
        
        # Show available extraction methods
        self.logger.info("\nAvailable extraction methods:")
        pdf_methods = PDFExtractor.get_available_methods()
        for method, available in pdf_methods.items():
            status = "✓" if available else "✗"
            self.logger.info(f"  {status} {method}")
        
        return True
    
    def get_invoice_files(self, retry_failed: bool = False) -> List[Path]:
        """Get list of invoice files to process"""
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
                    'ClaimNotes': non_invoice_reason,
                    'AtoReference': 'N/A',
                    'RequiresDocumentation': [],
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
        """Create a failed entry placeholder"""
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
    
    def cleanup_non_invoices(self, dry_run: bool = True) -> tuple[int, int]:
        """
        Clean up non-invoice files from the Non-Invoice folder
        
        Args:
            dry_run: If True, only show what would be deleted without actually deleting
        
        Returns:
            Tuple of (files_found, files_deleted)
        """
        non_invoice_folder = self.config.output_folder / "Non-Invoice"
        
        if not non_invoice_folder.exists():
            self.logger.warning(f"Non-Invoice folder does not exist: {non_invoice_folder}")
            return 0, 0
        
        # Get all files in Non-Invoice folder
        files = []
        for ext in self.config.file_extensions:
            files.extend(non_invoice_folder.rglob(f"*{ext}"))
        
        if not files:
            self.logger.info("No files found in Non-Invoice folder")
            return 0, 0
        
        self.logger.section("NON-INVOICE CLEANUP")
        self.logger.info(f"Found {len(files)} file(s) in Non-Invoice folder")
        
        if dry_run:
            self.logger.info("\n=== DRY RUN MODE - No files will be deleted ===\n")
        
        # Show files to be deleted
        self.logger.info("Files to be deleted:")
        for i, file_path in enumerate(files, 1):
            file_size = file_path.stat().st_size / 1024  # KB
            self.logger.info(f"  {i}. {file_path.name} ({file_size:.2f} KB)")
        
        if dry_run:
            self.logger.info("\nTo actually delete these files, run with --cleanup-non-invoices (without --dry-run)")
            return len(files), 0
        
        # Confirm deletion
        self.logger.warning(f"\nAbout to delete {len(files)} file(s) from Non-Invoice folder")
        self.logger.warning("This action cannot be undone!")
        
        # Delete files
        deleted_count = 0
        for file_path in files:
            try:
                file_path.unlink()
                deleted_count += 1
                self.logger.success(f"Deleted: {file_path.name}")
            except Exception as e:
                self.logger.error(f"Failed to delete {file_path.name}: {e}")
        
        self.logger.success(f"\nDeleted {deleted_count} out of {len(files)} file(s)")
        return len(files), deleted_count
    
    def run(self, retry_failed: bool = False, reprocess: bool = False):
        """Main processing loop"""
        start_time = datetime.now()
        
        self.logger.section("LM STUDIO INVOICE CATALOGING SYSTEM")
        self.logger.info(f"Financial Year: FY{self.config.financial_year}")
        self.logger.info("ATO Work Expense Deductions")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.logger.error("Prerequisites check failed. Exiting.")
            return
        
        # Load cache and failed files
        cache_stats = self.cache_manager.get_stats()
        failed_stats = self.failed_files_manager.get_stats()
        
        self.logger.info(f"\nCache loaded: {cache_stats['total_entries']} entries")
        self.logger.info(f"Failed files tracked: {failed_stats['total_failed']} entries")
        
        # Get files to process
        files = self.get_invoice_files(retry_failed)
        
        if not files:
            self.logger.warning("No invoice files found to process")
            return
        
        # Process files
        processed_invoices = []
        success_count = 0
        fail_count = 0
        cached_count = 0
        skipped_count = 0
        non_invoice_count = 0
        manual_review_count = 0
        
        self.logger.section("PROCESSING INVOICES")
        
        if reprocess:
            self.logger.info("REPROCESS MODE: Ignoring cache for all files")
        
        for i, file_path in enumerate(files, 1):
            result = self.process_file(file_path, i, len(files), reprocess=reprocess)
            
            if result:
                processed_invoices.append(result)
                
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
        
        self.logger.success(f"\nCache saved with {len(self.cache_manager.cache)} entries")
        self.logger.success(f"Failed files list saved with {len(self.failed_files_manager.failed_files)} entries")
        
        # Export results
        if processed_invoices:
            self.logger.section("EXPORTING RESULTS")
            
            # Export CSV
            catalog_path, summary_path, manual_review_path = self.csv_exporter.export(processed_invoices)
            self.logger.success(f"CSV catalog: {catalog_path}")
            self.logger.success(f"CSV summary: {summary_path}")
            if manual_review_path:
                self.logger.success(f"Manual review list: {manual_review_path}")
            
            # Export Excel
            try:
                excel_path = self.excel_exporter.export(
                    processed_invoices,
                    self.config.to_dict()
                )
                self.logger.success(f"Excel file: {excel_path}")
            except Exception as e:
                self.logger.warning(f"Excel export failed: {e}")
        
        # Final summary
        elapsed = datetime.now() - start_time
        
        self.logger.section("PROCESSING COMPLETE")
        self.logger.success(f"Successful: {success_count} files")
        if non_invoice_count > 0:
            self.logger.info(f"Non-Invoices: {non_invoice_count} files (moved to Non-Invoice folder)")
        if fail_count > 0:
            self.logger.warning(f"Failed: {fail_count} files")
        else:
            self.logger.success(f"Failed: {fail_count} files")
        self.logger.info(f"Cached (Duplicates): {cached_count} files")
        if skipped_count > 0:
            self.logger.warning(f"Skipped (Max retries): {skipped_count} files")
        else:
            self.logger.success(f"Skipped (Max retries): {skipped_count} files")
        if manual_review_count > 0:
            self.logger.warning(f"Manual Review Required: {manual_review_count} files (missing critical fields)")
        else:
            self.logger.success(f"Manual Review Required: {manual_review_count} files")
        self.logger.success(f"Total processed: {len(processed_invoices)} invoices")
        self.logger.info(f"Time elapsed: {elapsed}")
        
        if fail_count > 0:
            self.logger.info("\nTIP: Run with --retry-failed to retry failed files")
        if manual_review_count > 0:
            self.logger.info("TIP: Check Manual_Review_Required.csv for files needing attention")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Professional Invoice Cataloging System using LM Studio"
    )
    parser.add_argument(
        '--financial-year',
        type=str,
        default='2024-2025',
        help='Financial year in format YYYY-YYYY (e.g., 2024-2025)'
    )
    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Retry only failed files'
    )
    parser.add_argument(
        '--reprocess',
        action='store_true',
        help='Reprocess all files, ignoring cache (useful for testing changes)'
    )
    parser.add_argument(
        '--cleanup-non-invoices',
        action='store_true',
        help='Clean up files in the Non-Invoice folder'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview cleanup without actually deleting files (use with --cleanup-non-invoices)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Check prerequisites only, do not process files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )
    
    args = parser.parse_args()
    
    # Create config
    config = Config()
    config.financial_year = args.financial_year
    
    # Setup logger
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logger(config.log_folder, log_level)
    
    # Create cataloger
    cataloger = InvoiceCataloger(config)
    
    # Check only mode
    if args.check_only:
        if cataloger.check_prerequisites():
            print("\n✓ All prerequisites met")
            sys.exit(0)
        else:
            print("\n✗ Prerequisites check failed")
            sys.exit(1)
    
    # Cleanup non-invoices mode
    if args.cleanup_non_invoices:
        try:
            files_found, files_deleted = cataloger.cleanup_non_invoices(dry_run=args.dry_run)
            if args.dry_run:
                print(f"\n✓ Dry run complete: {files_found} file(s) would be deleted")
            else:
                print(f"\n✓ Cleanup complete: {files_deleted} out of {files_found} file(s) deleted")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Cleanup failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Run processing
    try:
        cataloger.run(retry_failed=args.retry_failed, reprocess=args.reprocess)
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
