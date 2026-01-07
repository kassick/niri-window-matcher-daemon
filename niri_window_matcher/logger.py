import logging
import os

# Get log level from environment variable, default to INFO
log_level_str = os.environ.get("NIRI_WINDOW_MATCHER_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Configure the logger
logger = logging.getLogger("niri_window_matcher")
logger.setLevel(log_level)

# Create console handler with formatting
handler = logging.StreamHandler()
handler.setLevel(log_level)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)

# Add handler to logger if not already present
if not logger.handlers:
    logger.addHandler(handler)
