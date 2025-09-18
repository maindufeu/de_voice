import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional

class StreamHandler:
    """
    Handles streaming updates from DataAnalysisFlow and forwards them to WebSocket clients.
    """
    
    def __init__(self):
        """Initialize the stream handler."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.analysis_results: Dict[str, Dict] = {}
    
    # async def connect(self, websocket: WebSocket, client_id: str):
    #     """
    #     Establish WebSocket connection with a client.
        
    #     Args:
    #         websocket (WebSocket): The WebSocket connection
    #         client_id (str): Unique identifier for the client
    #     """
    #     await websocket.accept()
    #     self.active_connections[client_id] = websocket
    
    # def disconnect(self, client_id: str):
    #     """
    #     Remove a client connection.
        
    #     Args:
    #         client_id (str): Client ID to disconnect
    #     """
    #     if client_id in self.active_connections:
    #         del self.active_connections[client_id]
    
    async def stream_handler(self, message: str, percent: int, job_id: str, result: dict = None):
        """
        Handler function for DataAnalysisFlow progress updates.
        
        Args:
            message (str): Progress message
            percent (int): Completion percentage
            job_id (str): Unique job identifier
            result (dict, optional): Result data
        """
        # Store the latest result for this job
        if result:
            self.analysis_results[job_id] = result
        
        # Find all clients associated with this job and send updates
        #for client_id, websocket in self.active_connections.items():
        #if client_id.startswith(f"{job_id}:"):
        try:
            # Send different types of messages based on result content
            if result and "token" in result:
                # Send streaming token
                # await websocket.send_json({
                #     "type": "token",
                #     "content": result["token"],
                #     "percent": percent
                # })
                yield {
                    "type": "token",
                    "content": result["token"],
                    "percent": percent
                }
            else:
                # Send progress update
                # await websocket.send_json({
                #     "type": "progress",
                #     "message": message,
                #     "percent": percent,
                #     "facial_expression": result.get("facialExpression") if result else None,
                #     "animation": result.get("animation") if result else None
                # })
                yield {
                    "type": "progress",
                    "message": message,
                    "percent": percent,
                    "facial_expression": result.get("facialExpression") if result else None,
                    "animation": result.get("animation") if result else None
                }
            
            # If analysis is complete, send the full result
            if percent == 100 and "error" not in result:
                # await websocket.send_json({
                #     "type": "complete",
                #     "result": {
                #         "text": result.get("text"),
                #         "data": result.get("data"),
                #         "images": result.get("images", [])
                #     }
                # })
                yield {
                    "type": "complete",
                    "result": {
                        "text": result.get("text"),
                        "data": result.get("data"),
                        "images": result.get("images", [])
                    }
                }
        except Exception as e:
            print(f"Error sending to client: {str(e)}")