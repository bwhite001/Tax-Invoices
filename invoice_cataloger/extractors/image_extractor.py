"""
Image Text Extraction using OCR
"""
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io

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

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class ImageExtractor:
    """Extract text from images using OCR"""
    
    def __init__(self, tesseract_path: Optional[str] = None, ocr_languages: list = None):
        self.tesseract_path = tesseract_path
        self.ocr_languages = ocr_languages or ['en']
        self.easyocr_reader = None
        
        # Configure Tesseract path if provided
        if tesseract_path and PYTESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, image_path: Path) -> Tuple[Optional[str], str]:
        """
        Extract text from image using OCR
        
        Returns:
            Tuple[Optional[str], str]: (extracted_text, method_used)
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            return None, "File not found"
        
        # Try to preprocess image for better OCR
        preprocessed_image = self._preprocess_image(image_path)
        
        # Stage 1: EasyOCR (deep learning, better accuracy)
        if EASYOCR_AVAILABLE:
            text, success = self._extract_with_easyocr(image_path)
            if success:
                return text, "EasyOCR"
        
        # Stage 2: Tesseract OCR
        if PYTESSERACT_AVAILABLE:
            text, success = self._extract_with_tesseract(preprocessed_image or image_path)
            if success:
                return text, "Tesseract OCR"
        
        return None, "No OCR engine available"
    
    def _preprocess_image(self, image_path: Path) -> Optional[Path]:
        """Preprocess image for better OCR results"""
        if not CV2_AVAILABLE:
            return None
        
        try:
            # Read image
            img = cv2.imread(str(image_path))
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
            
            # Save preprocessed image
            temp_path = image_path.parent / f"temp_preprocessed_{image_path.name}"
            cv2.imwrite(str(temp_path), denoised)
            
            return temp_path
        except Exception:
            return None
    
    def _extract_with_easyocr(self, image_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using EasyOCR"""
        try:
            # Initialize EasyOCR reader (lazy loading)
            if self.easyocr_reader is None:
                self.easyocr_reader = easyocr.Reader(self.ocr_languages, gpu=False)
            
            # Perform OCR
            results = self.easyocr_reader.readtext(str(image_path), detail=0)
            text = " ".join(results)
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 20:
                return text, True
            
            return None, False
        except Exception:
            return None, False
    
    def _extract_with_tesseract(self, image_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text using Tesseract OCR"""
        try:
            # Open image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang='+'.join(self.ocr_languages)
            )
            
            # Check if meaningful text was extracted
            if text and len(text.strip()) > 20:
                return text, True
            
            return None, False
        except Exception:
            return None, False
    
    @staticmethod
    def get_available_methods() -> dict:
        """Get information about available extraction methods"""
        return {
            'EasyOCR': EASYOCR_AVAILABLE,
            'Tesseract': PYTESSERACT_AVAILABLE,
            'OpenCV': CV2_AVAILABLE,
        }
