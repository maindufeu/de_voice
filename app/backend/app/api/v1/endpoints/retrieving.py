from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from services.temporal_memory.storage import get_image, get_data
from core.logger import logger

router = APIRouter()

@router.get("/image/{image_id}")
async def retrieve_image(image_id: str):
    """
    Retrieve a stored image by ID
    
    Args:
        image_id: ID of the image to retrieve
        
    Returns:
        The image data with appropriate Content-Type
    """
    try:
        image_data = get_image(image_id)
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found")
            
        # Determine the content type (assuming most images will be png/jpeg)
        # A more robust implementation would detect the actual image type
        content_type = "image/png"
        
        # Return the base64 image data
        return Response(
            content=image_data,
            media_type="text/plain",  # We're returning base64 text, not raw binary
            headers={"Content-Type": "text/plain"}
        )
    except Exception as e:
        logger.error(f"Error retrieving image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")

@router.get("/data/{data_id}")
async def retrieve_data(data_id: str):
    """
    Retrieve stored data by ID
    
    Args:
        data_id: ID of the data to retrieve
        
    Returns:
        JSON response with the stored data
    """
    try:
        data_obj = get_data(data_id)
        if not data_obj:
            raise HTTPException(status_code=404, detail="Data not found")
            
        return JSONResponse(content=data_obj)
    except Exception as e:
        logger.error(f"Error retrieving data {data_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")