"""WebSocket client for Pokemon Showdown."""
import asyncio
import json
import logging
import websockets
from typing import Optional, Callable, Dict
from urllib.parse import urlencode
import aiohttp

from .protocol import Action
from .message_parser import MessageParser


logger = logging.getLogger(__name__)


class ShowdownClient:
    """Client for connecting to Pokemon Showdown via WebSocket."""
    
    def __init__(self, server_url: str, username: str, password: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            server_url: WebSocket server URL (e.g., "sim3.psim.us" or "sim3.psim.us:8000")
            username: Pokemon Showdown username
            password: Pokemon Showdown password (optional for guests)
        """
        # Use secure WebSocket (wss://) if no port specified, or ws:// if port 8000
        if ':8000' in server_url:
            self.server_url = f"ws://{server_url}/showdown/websocket"
        else:
            # Remove port if present and use wss:// (port 443)
            server_url = server_url.replace(':443', '').replace(':8000', '')
            self.server_url = f"wss://{server_url}/showdown/websocket"
        self.username = username
        self.password = password
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.parser = MessageParser()
        self.logged_in = False
        self.challenge_str: Optional[str] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.current_battles: Dict[str, 'BattleHandler'] = {}
        
    async def connect(self, max_retries: int = 3):
        """Connect to Pokemon Showdown server with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to {self.server_url} (attempt {attempt + 1}/{max_retries})")
                
                # Add longer timeout and better connection parameters
                self.websocket = await websockets.connect(
                    self.server_url,
                    open_timeout=30,  # 30 second timeout instead of default 10
                    ping_timeout=20,
                    close_timeout=10,
                    max_size=None,  # No message size limit
                    compression=None  # Disable compression for compatibility
                )
                logger.info("Connected to Pokemon Showdown")
                return
                
            except asyncio.TimeoutError:
                logger.warning(f"Connection timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Failed to connect after all retries")
                    raise ConnectionError(
                        f"Could not connect to {self.server_url} after {max_retries} attempts. "
                        "Please check:\n"
                        "1. Your internet connection\n"
                        "2. The server URL in .env (try 'sim.smogon.com:8000' or 'sim.psim.us:8000')\n"
                        "3. If Pokemon Showdown servers are online"
                    )
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                raise
        
    async def login(self):
        """Authenticate with Pokemon Showdown."""
        if not self.websocket:
            raise RuntimeError("Not connected to server")
        
        # Wait for challenge string
        while not self.challenge_str:
            message = await self.websocket.recv()
            await self._handle_message(message)
        
        # Login
        if self.password:
            # Login with password
            assertion = await self._get_assertion()
            login_cmd = f"|/trn {self.username},0,{assertion}"
        else:
            # Login as guest
            login_cmd = f"|/trn {self.username},0,"
        
        await self.websocket.send(login_cmd)
        
        # Wait for login confirmation
        while not self.logged_in:
            message = await self.websocket.recv()
            await self._handle_message(message)
        
        logger.info(f"Logged in as {self.username}")
    
    async def _get_assertion(self) -> str:
        """Get login assertion from Pokemon Showdown login server."""
        if not self.challenge_str or not self.password:
            raise RuntimeError("Need challenge string and password")
        
        url = "https://play.pokemonshowdown.com/action.php"
        data = {
            "act": "login",
            "name": self.username,
            "pass": self.password,
            "challstr": self.challenge_str
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_text = await response.text()
                response_json = json.loads(response_text[1:])  # Skip leading ']'
                
                if not response_json.get("actionsuccess"):
                    raise RuntimeError(f"Login failed: {response_json}")
                
                return response_json["assertion"]
    
    async def search_battle(self, format_name: str = "gen9randombattle"):
        """Search for a battle in the specified format."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        cmd = f"|/search {format_name}"
        await self.websocket.send(cmd)
        logger.info(f"Searching for {format_name} battle")
    
    async def cancel_search(self):
        """Cancel battle search."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        await self.websocket.send("|/cancelsearch")
        logger.info("Cancelled battle search")
    
    async def challenge_user(self, username: str, format_name: str = "gen9randombattle"):
        """Challenge a specific user to a battle."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        cmd = f"|/challenge {username}, {format_name}"
        await self.websocket.send(cmd)
        logger.info(f"Challenged {username} to {format_name}")
    
    async def accept_challenge(self, username: str):
        """Accept a challenge from a user."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        cmd = f"|/accept {username}"
        await self.websocket.send(cmd)
        logger.info(f"Accepted challenge from {username}")
    
    async def send_message(self, room_id: str, message: str):
        """Send a message to a room."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        formatted = f"{room_id}|{message}"
        await self.websocket.send(formatted)
        logger.debug(f"Sent to {room_id}: {message}")
    
    async def send_action(self, room_id: str, action: Action):
        """Send a battle action."""
        action_str = action.to_showdown_format()
        await self.send_message(room_id, action_str)
        logger.info(f"Action in {room_id}: {action_str}")
    
    async def leave_battle(self, room_id: str):
        """Leave a battle room."""
        await self.send_message(room_id, "/leave")
        if room_id in self.current_battles:
            del self.current_battles[room_id]
        logger.info(f"Left battle {room_id}")
    
    async def _handle_message(self, raw_message: str):
        """Handle incoming message from server."""
        lines = raw_message.split("\n")
        room_id = ""
        
        # First line might be room ID
        if lines[0].startswith(">"):
            room_id = lines[0][1:]
            lines = lines[1:]
        
        for line in lines:
            if not line.strip():
                continue
            
            # Parse message type
            parts = line.split("|")
            if len(parts) < 2:
                continue
            
            msg_type = parts[1]
            
            # Handle global messages
            if msg_type == "challstr":
                self.challenge_str = "|".join(parts[2:])
                logger.debug(f"Received challenge string: {self.challenge_str}")
            
            elif msg_type == "updateuser":
                if len(parts) >= 3 and parts[2] == self.username and parts[3] != "0":
                    self.logged_in = True
                    logger.info(f"Login confirmed: {parts[2]}")
            
            elif msg_type == "popup":
                popup_msg = parts[2] if len(parts) > 2 else "(empty)"
                logger.warning(f"Popup: {popup_msg}")
                # Print full message for debugging
                logger.warning(f"Full popup line: {line}")
            
            elif msg_type == "pm":
                logger.info(f"PM from {parts[2]}: {parts[4]}")
            
            # Handle battle messages
            if room_id and room_id.startswith("battle-"):
                if room_id not in self.current_battles:
                    logger.info(f"New battle detected: {room_id}")
                
                # Call registered handler
                if room_id in self.message_handlers:
                    await self.message_handlers[room_id](room_id, line)
    
    def register_battle_handler(self, room_id: str, handler: Callable):
        """Register a message handler for a battle room."""
        self.message_handlers[room_id] = handler
        logger.debug(f"Registered handler for {room_id}")
    
    def unregister_battle_handler(self, room_id: str):
        """Unregister a battle handler."""
        if room_id in self.message_handlers:
            del self.message_handlers[room_id]
            logger.debug(f"Unregistered handler for {room_id}")
    
    async def listen(self):
        """Listen for messages from the server."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed by server")
        except Exception as e:
            logger.error(f"Error in listen loop: {e}", exc_info=True)
    
    async def disconnect(self):
        """Disconnect from the server."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from Pokemon Showdown")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        await self.login()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
