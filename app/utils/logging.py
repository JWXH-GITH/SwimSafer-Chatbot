import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Create a logger instance
logger = logging.getLogger(__name__)
