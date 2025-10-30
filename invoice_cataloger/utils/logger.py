"""
Logging Utility for Invoice Cataloger
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for Windows
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.WHITE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
        'SUCCESS': Fore.GREEN,
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        
        return super().format(record)


class InvoiceLogger:
    """Custom logger for invoice processing"""
    
    def __init__(self, name: str = "InvoiceCataloger", log_folder: Path = None, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_formatter = ColoredFormatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if log folder provided)
        if log_folder:
            log_folder = Path(log_folder)
            log_folder.mkdir(parents=True, exist_ok=True)
            
            log_file = log_folder / f"processing_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def success(self, message: str):
        """Log success message (custom level)"""
        # Use INFO level but with green color
        self.logger.info(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
    
    def section(self, message: str):
        """Log section header"""
        separator = "=" * 60
        self.logger.info(f"\n{separator}")
        self.logger.info(message)
        self.logger.info(separator)
    
    def progress(self, current: int, total: int, message: str = ""):
        """Log progress"""
        percentage = (current / total * 100) if total > 0 else 0
        progress_msg = f"[{current}/{total}] ({percentage:.1f}%)"
        if message:
            progress_msg += f" {message}"
        self.logger.info(progress_msg)


# Global logger instance
logger = None


def setup_logger(log_folder: Path = None, log_level: str = "INFO") -> InvoiceLogger:
    """Setup and return global logger instance"""
    global logger
    logger = InvoiceLogger(log_folder=log_folder, log_level=log_level)
    return logger


def get_logger() -> InvoiceLogger:
    """Get global logger instance"""
    global logger
    if logger is None:
        logger = InvoiceLogger()
    return logger
