from pathlib import Path
from core.logger import logger

# Create necessary directories during module initialization
def ensure_directories():
    """Ensure the required directories exist for the temporal memory module"""
    base_dir = Path("services/temporal_memory")
    images_dir = base_dir / "images"
    data_dir = base_dir / "data"
    
    # Create directories if they don't exist
    for directory in [base_dir, images_dir, data_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        
    logger.info(f"Initialized temporal memory directories")

# Run initialization
ensure_directories()