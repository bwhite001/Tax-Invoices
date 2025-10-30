"""
Multi-Stage PDF Text Extraction
Tries multiple methods for maximum reliability
"""
from pathlib import Path
from typing import Optional, Tuple
import io

# PDF Libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# OCR Libraries
try:
    from pdf2image import convert_from_path
    from PIL import Image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class PDFExtractor:
    """Multi-stage PDF text extraction with automatic fallback"""
    
    def __init__(self, tesseract_path: Optional[str] = None, ocr_languages: list = None):
        self.tesseract_path = tesseract_path
        self.ocr_languages = ocr_languages or ['en']
        self.easyocr_reader = None
        
        # Configure Tesseract path if provided
        if tesseract_path and PYTESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, pdf_path: Path) -> Tuple[Optional[str], str]:
        """
        Extract text from PDF using multiple methods with automatic fallback
        
        Returns:
            Tuple[Optional[str], str]: (extracted_text, method_used)
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            return None, "File not found"
        
        # Stage 1: PyMuPDF (fastest, most reliable for text PDFs)
        if PYMUPDF_AVAILABLE:
            text, success = self._extract_with_pymupdf(pdf_path)
            if success:
                return text, "PyMuPDF (native text)"
        
        # Stage 2: pdfplumber (better for tables/structured data)
        if PDFPLUMBER_AVAILABLE:
            text, success = self._extract_with_pdfplumber(pdf_path)
            if success:
                return text, "pdfplumber (native text)"
        
        # Stage 3: pypdf (pure Python fallback)
        if PYPDF_AVAILABLE:
            text, success = self._extract_with_pypdf(pdf_path)
            if success:
                return text, "pypdf (native text)"
        
        # Stage 4: EasyOCR (deep learning OCR, no Tesseract needed)
        if EASYOCR_AVAILABLE and PDF2IMAGE_AVAILABLE:
            text, success = self._extract_with_easyocr(pdf_path)
            if success:
                return text, "EasyOCR"
        
        # Stage 5: Tesseract OCR (if installed)
        if PYTESSERACT_AVAILABLE and PDF2IMAGE_AVAILABLE:
            text, success = self._extract_with_tesseract(pdf_path)
            if success:
                return text, "Tesseract OCR"
        
        return None, "All extraction methods failed"
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using PyMuPDF (fitz)"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 50:
                return text, True
            
            return None, False
        except Exception as e:
            return None, False
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using pdfplumber"""
        try:
            text = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 50:
                return text, True
            
            return None, False
        except Exception as e:
            return None, False
    
    def _extract_with_pypdf(self, pdf_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using pypdf"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 50:
                return text, True
            
            return None, False
        except Exception as e:
            return None, False
    
    def _extract_with_easyocr(self, pdf_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using EasyOCR (deep learning)"""
        try:
            # Initialize EasyOCR reader (lazy loading)
            if self.easyocr_reader is None:
                self.easyocr_reader = easyocr.Reader(self.ocr_languages, gpu=False)
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=3)
            
            text = ""
            for i, image in enumerate(images):
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Perform OCR
                results = self.easyocr_reader.readtext(img_byte_arr, detail=0)
                text += " ".join(results) + "\n"
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 50:
                return text, True
            
            return None, False
        except Exception as e:
            return None, False
    
    def _extract_with_tesseract(self, pdf_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using Tesseract OCR"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=3)
            
            text = ""
            for image in images:
                # Perform OCR
                page_text = pytesseract.image_to_string(
                    image,
                    lang='+'.join(self.ocr_languages)
                )
                text += page_text + "\n"
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 50:
                return text, True
            
            return None, False
        except Exception as e:
            return None, False
    
    @staticmethod
    def get_available_methods() -> dict:
        """Get information about available extraction methods"""
        return {
            'PyMuPDF': PYMUPDF_AVAILABLE,
            'pdfplumber': PDFPLUMBER_AVAILABLE,
            'pypdf': PYPDF_AVAILABLE,
            'EasyOCR': EASYOCR_AVAILABLE,
            'Tesseract': PYTESSERACT_AVAILABLE,
            'pdf2image': PDF2IMAGE_AVAILABLE,
        }
    
    @staticmethod
    def check_dependencies() -> Tuple[bool, list]:
        """
        Check if minimum dependencies are available
        
        Returns:
            Tuple[bool, list]: (all_ok, missing_dependencies)
        """
        missing = []
        
        # At least one native PDF reader required
        if not (PYMUPDF_AVAILABLE or PDFPLUMBER_AVAILABLE or PYPDF_AVAILABLE):
            missing.append("PDF reader (install: pip install PyMuPDF pdfplumber pypdf)")
        
        # OCR is optional but recommended
        if not (EASYOCR_AVAILABLE or PYTESSERACT_AVAILABLE):
            missing.append("OCR engine (optional, install: pip install easyocr pytesseract)")
        
        if not PDF2IMAGE_AVAILABLE:
            missing.append("pdf2image (optional for OCR, install: pip install pdf2image)")
        
        return len(missing) == 0, missing
