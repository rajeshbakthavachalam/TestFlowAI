import sys
import os
from loguru import logger

def setup_logging(log_level: str = "INFO"):
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Clear any default logger configurations
    logger.remove()

    # Console handler: colorized output with a nice format
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
    )

    # File handler: logs to file with rotation, retention, and compression for production
    logger.add(
        os.path.join(log_dir, "agenticsdlc.log"),
        rotation="10 MB",     # Rotate after 10 MB
        retention="10 days",    # Keep logs for 10 days
        compression="zip",      # Compress archived logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
        level=log_level,
    )