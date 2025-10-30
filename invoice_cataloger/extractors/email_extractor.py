"""
Email Text Extraction for .eml and .msg files
"""
from pathlib import Path
from typing import Optional, Tuple
import email
from email import policy

try:
    import extract_msg
    EXTRACT_MSG_AVAILABLE = True
except ImportError:
    EXTRACT_MSG_AVAILABLE = False

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False


class EmailExtractor:
    """Extract text from email files"""
    
    def extract_from_eml(self, eml_path: Path) -> Tuple[Optional[str], str]:
        """
        Extract text from .eml file
        
        Returns:
            Tuple[Optional[str], str]: (extracted_text, method_used)
        """
        eml_path = Path(eml_path)
        
        if not eml_path.exists():
            return None, "File not found"
        
        try:
            with open(eml_path, 'rb') as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
            
            text = ""
            
            # Extract headers
            text += f"From: {msg.get('From', 'Unknown')}\n"
            text += f"To: {msg.get('To', 'Unknown')}\n"
            text += f"Subject: {msg.get('Subject', 'No Subject')}\n"
            text += f"Date: {msg.get('Date', 'Unknown')}\n\n"
            
            # Extract body
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body = part.get_payload(decode=True)
                        if body:
                            text += body.decode('utf-8', errors='ignore')
                    elif content_type == 'text/html':
                        # Fallback to HTML if no plain text
                        if 'text/plain' not in text:
                            body = part.get_payload(decode=True)
                            if body:
                                text += body.decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload(decode=True)
                if body:
                    text += body.decode('utf-8', errors='ignore')
            
            # List attachments
            attachments = []
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
            
            if attachments:
                text += f"\n\nAttachments:\n"
                for attachment in attachments:
                    text += f"- {attachment}\n"
            
            if text and len(text.strip()) > 20:
                return text, "Python email library"
            
            return None, "No content extracted"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def extract_from_msg(self, msg_path: Path) -> Tuple[Optional[str], str]:
        """
        Extract text from .msg file (Outlook)
        
        Returns:
            Tuple[Optional[str], str]: (extracted_text, method_used)
        """
        msg_path = Path(msg_path)
        
        if not msg_path.exists():
            return None, "File not found"
        
        # Try extract-msg library first
        if EXTRACT_MSG_AVAILABLE:
            text, success = self._extract_msg_with_library(msg_path)
            if success:
                return text, "extract-msg library"
        
        # Fallback to COM (Windows only)
        if WIN32COM_AVAILABLE:
            text, success = self._extract_msg_with_com(msg_path)
            if success:
                return text, "Outlook COM"
        
        return None, "No MSG extraction method available"
    
    def _extract_msg_with_library(self, msg_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text from .msg using extract-msg library"""
        try:
            msg = extract_msg.Message(msg_path)
            
            text = ""
            text += f"From: {msg.sender or 'Unknown'}\n"
            text += f"To: {msg.to or 'Unknown'}\n"
            text += f"Subject: {msg.subject or 'No Subject'}\n"
            text += f"Date: {msg.date or 'Unknown'}\n\n"
            text += msg.body or ""
            
            # List attachments
            if msg.attachments:
                text += f"\n\nAttachments:\n"
                for attachment in msg.attachments:
                    text += f"- {attachment.longFilename or attachment.shortFilename}\n"
            
            msg.close()
            
            if text and len(text.strip()) > 20:
                return text, True
            
            return None, False
        except Exception:
            return None, False
    
    def _extract_msg_with_com(self, msg_path: Path) -> Tuple[Optional[str], bool]:
        """Extract text from .msg using Outlook COM"""
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            msg = outlook.Session.OpenSharedItem(str(msg_path.absolute()))
            
            text = ""
            text += f"From: {msg.SenderName} <{msg.SenderEmailAddress}>\n"
            text += f"To: {msg.To}\n"
            text += f"Subject: {msg.Subject}\n"
            text += f"Date: {msg.ReceivedTime}\n\n"
            text += msg.Body
            
            # List attachments
            if msg.Attachments.Count > 0:
                text += f"\n\nAttachments:\n"
                for attachment in msg.Attachments:
                    text += f"- {attachment.FileName}\n"
            
            if text and len(text.strip()) > 20:
                return text, True
            
            return None, False
        except Exception:
            return None, False
    
    @staticmethod
    def get_available_methods() -> dict:
        """Get information about available extraction methods"""
        return {
            'extract-msg': EXTRACT_MSG_AVAILABLE,
            'Win32COM': WIN32COM_AVAILABLE,
        }
