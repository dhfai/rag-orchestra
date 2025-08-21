"""
WebSocket Handler
================

WebSocket handler untuk real-time user-system interaction
Menangani connection management dan message routing
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from ..utils.logger import get_logger

logger = get_logger("WebSocketHandler")

class WebSocketManager:
    """
    Manager untuk WebSocket connections dan broadcasting
    """

    def __init__(self):
        # Active connections by session_id
        self.connections: Dict[str, List[WebSocket]] = {}

        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}

        # Connection stats
        self.total_connections = 0
        self.active_sessions = 0

        logger.info("WebSocket Manager initialized")

    def register_message_handler(self, message_type: str, handler: Callable):
        """Register handler untuk message type tertentu"""
        self.message_handlers[message_type] = handler
        logger.debug(f"Message handler registered for type: {message_type}")

    async def connect(self, websocket: WebSocket, session_id: str) -> bool:
        """
        Connect WebSocket untuk session

        Args:
            websocket: WebSocket connection
            session_id: ID session

        Returns:
            bool: True jika berhasil connect
        """
        try:
            await websocket.accept()

            # Add to connections
            if session_id not in self.connections:
                self.connections[session_id] = []
                self.active_sessions += 1

            self.connections[session_id].append(websocket)
            self.total_connections += 1

            logger.info(f"WebSocket connected for session: {session_id}")

            # Send connection confirmation
            await self.send_to_session(session_id, {
                "type": "connection_established",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "connection_id": id(websocket)
            })

            return True

        except Exception as e:
            logger.error(f"Error connecting WebSocket for session {session_id}: {str(e)}")
            return False

    async def disconnect(self, websocket: WebSocket, session_id: str):
        """
        Disconnect WebSocket untuk session

        Args:
            websocket: WebSocket connection
            session_id: ID session
        """
        try:
            if session_id in self.connections:
                if websocket in self.connections[session_id]:
                    self.connections[session_id].remove(websocket)
                    self.total_connections -= 1

                # Remove session if no more connections
                if not self.connections[session_id]:
                    del self.connections[session_id]
                    self.active_sessions -= 1

            logger.info(f"WebSocket disconnected for session: {session_id}")

        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for session {session_id}: {str(e)}")

    async def send_to_session(self, session_id: str, message: Dict[str, Any]):
        """
        Send message ke semua connections untuk session

        Args:
            session_id: ID session
            message: Message to send
        """
        if session_id not in self.connections:
            logger.warning(f"No connections found for session: {session_id}")
            return

        message_json = json.dumps(message)
        connections = self.connections[session_id].copy()

        for websocket in connections:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {str(e)}")
                # Remove dead connection
                await self.disconnect(websocket, session_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast message ke semua sessions

        Args:
            message: Message to broadcast
        """
        message_json = json.dumps(message)

        for session_id, connections in self.connections.items():
            for websocket in connections.copy():
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"Failed to broadcast to session {session_id}: {str(e)}")
                    await self.disconnect(websocket, session_id)

    async def handle_message(self, session_id: str, websocket: WebSocket, message_data: Dict[str, Any]):
        """
        Handle incoming WebSocket message

        Args:
            session_id: ID session
            websocket: WebSocket connection
            message_data: Parsed message data
        """
        message_type = message_data.get("type")

        if not message_type:
            await self.send_error(websocket, "Missing message type")
            return

        try:
            # Handle built-in message types
            if message_type == "ping":
                await self.handle_ping(websocket)
            elif message_type == "get_connection_info":
                await self.handle_get_connection_info(session_id, websocket)
            elif message_type in self.message_handlers:
                # Call registered handler
                handler = self.message_handlers[message_type]
                await handler(session_id, websocket, message_data)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling message type '{message_type}': {str(e)}")
            await self.send_error(websocket, f"Message handling error: {str(e)}")

    async def handle_ping(self, websocket: WebSocket):
        """Handle ping message"""
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))

    async def handle_get_connection_info(self, session_id: str, websocket: WebSocket):
        """Handle get connection info request"""
        connection_count = len(self.connections.get(session_id, []))

        await websocket.send_text(json.dumps({
            "type": "connection_info",
            "session_id": session_id,
            "connection_count": connection_count,
            "connection_id": id(websocket),
            "timestamp": datetime.now().isoformat()
        }))

    async def send_error(self, websocket: WebSocket, error_message: str):
        """Send error message via WebSocket"""
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error_message": error_message,
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Failed to send error message: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            "total_connections": self.total_connections,
            "active_sessions": self.active_sessions,
            "session_connection_counts": {
                session_id: len(connections)
                for session_id, connections in self.connections.items()
            },
            "registered_handlers": list(self.message_handlers.keys())
        }

    async def close_session_connections(self, session_id: str):
        """Close all connections untuk session"""
        if session_id not in self.connections:
            return

        connections = self.connections[session_id].copy()

        for websocket in connections:
            try:
                await websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {str(e)}")

        # Clean up
        if session_id in self.connections:
            del self.connections[session_id]
            self.active_sessions -= 1

        logger.info(f"All connections closed for session: {session_id}")

    async def shutdown(self):
        """Shutdown WebSocket manager"""
        logger.info("Shutting down WebSocket manager...")

        # Close all connections
        for session_id in list(self.connections.keys()):
            await self.close_session_connections(session_id)

        logger.info("WebSocket manager shutdown completed")

class WebSocketHandler:
    """
    Handler untuk WebSocket endpoint dengan message processing
    """

    def __init__(self, manager: WebSocketManager):
        self.manager = manager
        logger.info("WebSocket Handler initialized")

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """
        Handle WebSocket connection untuk session

        Args:
            websocket: WebSocket connection
            session_id: ID session
        """
        # Connect WebSocket
        connected = await self.manager.connect(websocket, session_id)
        if not connected:
            return

        try:
            # Listen for messages
            while True:
                try:
                    # Receive message
                    data = await websocket.receive_text()

                    # Parse JSON
                    try:
                        message_data = json.loads(data)
                    except json.JSONDecodeError as e:
                        await self.manager.send_error(websocket, f"Invalid JSON: {str(e)}")
                        continue

                    # Handle message
                    await self.manager.handle_message(session_id, websocket, message_data)

                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for session: {session_id}")
                    break
                except Exception as e:
                    logger.error(f"Error in WebSocket message loop: {str(e)}")
                    await self.manager.send_error(websocket, f"Connection error: {str(e)}")
                    break

        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {str(e)}")
        finally:
            # Cleanup
            await self.manager.disconnect(websocket, session_id)

# === Message Handler Functions ===

async def handle_status_request(session_id: str, websocket: WebSocket, message_data: Dict[str, Any]):
    """Handle status request message"""
    # This will be implemented to integrate with processing service
    await websocket.send_text(json.dumps({
        "type": "status_response",
        "session_id": session_id,
        "status": "handler_not_implemented",
        "timestamp": datetime.now().isoformat()
    }))

async def handle_cancel_request(session_id: str, websocket: WebSocket, message_data: Dict[str, Any]):
    """Handle cancel processing request"""
    # This will be implemented to integrate with processing service
    await websocket.send_text(json.dumps({
        "type": "cancel_response",
        "session_id": session_id,
        "result": "handler_not_implemented",
        "timestamp": datetime.now().isoformat()
    }))

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# Register default handlers
websocket_manager.register_message_handler("get_status", handle_status_request)
websocket_manager.register_message_handler("cancel_processing", handle_cancel_request)
