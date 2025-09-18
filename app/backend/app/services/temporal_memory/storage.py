import os
import json
import base64
import uuid
import time
import shutil
from typing import Dict, List, Union, Optional
from pathlib import Path
from datetime import datetime, timedelta
from core.logger import logger

# Configure storage paths
STORAGE_BASE_DIR = Path("services/temporal_memory")
IMAGES_DIR = STORAGE_BASE_DIR / "images"
DATA_DIR = STORAGE_BASE_DIR / "data"

# Asset expiration time (in hours)
ASSET_EXPIRATION_HOURS = 1

def ensure_storage_dirs():
    """Create storage directories if they don't exist"""
    for directory in [IMAGES_DIR, DATA_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured storage directory exists: {directory}")

# Initialize storage directories
ensure_storage_dirs()

def generate_unique_id() -> str:
    """Generate a unique ID for an asset"""
    return str(uuid.uuid4())

def store_image(image_data: str, prefix: str = "img") -> str:
    """
    Store a base64 encoded image and return its ID
    
    Args:
        image_data: Base64 encoded image data
        prefix: Optional prefix for the ID
        
    Returns:
        str: Unique ID for the stored image
    """
    try:
        # Strip any data URL prefix if present
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
            
        # Generate a unique ID
        image_id = f"{prefix}_{generate_unique_id()}"
        
        # Store the image data
        image_path = IMAGES_DIR / f"{image_id}.b64"
        with open(image_path, "w") as f:
            f.write(image_data)
            
        logger.info(f"Stored image with ID: {image_id}")
        return image_id
    except Exception as e:
        logger.error(f"Error storing image: {str(e)}")
        raise

def store_data(data_obj: Union[Dict, List], prefix: str = "data") -> str:
    """
    Store a data object as JSON and return its ID
    
    Args:
        data_obj: Data object to store (must be JSON serializable)
        prefix: Optional prefix for the ID
        
    Returns:
        str: Unique ID for the stored data
    """
    try:
        # Generate a unique ID
        data_id = f"{prefix}_{generate_unique_id()}"
        
        # Store the data as JSON
        data_path = DATA_DIR / f"{data_id}.json"
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data_obj, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Stored data with ID: {data_id}")
        return data_id
    except Exception as e:
        logger.error(f"Error storing data: {str(e)}")
        raise

def get_image(image_id: str) -> Optional[str]:
    """
    Retrieve a stored image by ID
    
    Args:
        image_id: ID of the image to retrieve
        
    Returns:
        str: Base64 encoded image data, or None if not found
    """
    try:
        image_path = IMAGES_DIR / f"{image_id}.b64"
        if not image_path.exists():
            logger.warning(f"Image not found: {image_id}")
            return None
            
        with open(image_path, "r") as f:
            image_data = f.read()
            
        return image_data
    except Exception as e:
        logger.error(f"Error retrieving image {image_id}: {str(e)}")
        return None

def get_data(data_id: str) -> Optional[Union[Dict, List]]:
    """
    Retrieve stored data by ID
    
    Args:
        data_id: ID of the data to retrieve
        
    Returns:
        Dict or List: The stored data object, or None if not found
    """
    try:
        data_path = DATA_DIR / f"{data_id}.json"
        if not data_path.exists():
            logger.warning(f"Data not found: {data_id}")
            return None
            
        with open(data_path, "r", encoding="utf-8") as f:
            data_obj = json.load(f)
            
        return data_obj
    except Exception as e:
        logger.error(f"Error retrieving data {data_id}: {str(e)}")
        return None

def clean_old_assets():
    """Remove assets older than the expiration time"""
    try:
        now = datetime.now()
        expiration_time = now - timedelta(hours=ASSET_EXPIRATION_HOURS)
        
        # Clean images
        for image_file in IMAGES_DIR.glob("*.b64"):
            if datetime.fromtimestamp(image_file.stat().st_mtime) < expiration_time:
                image_file.unlink()
                logger.info(f"Removed expired image: {image_file.name}")
                
        # Clean data
        for data_file in DATA_DIR.glob("*.json"):
            if datetime.fromtimestamp(data_file.stat().st_mtime) < expiration_time:
                data_file.unlink()
                logger.info(f"Removed expired data: {data_file.name}")
    except Exception as e:
        logger.error(f"Error cleaning old assets: {str(e)}")