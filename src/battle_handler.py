"""Battle handler to coordinate agent and battle state."""
import asyncio
import logging
from typing import Optional
from .connection import ShowdownClient, Action
from .battle import BattleState
from .agents import Agent

logger = logging.getLogger(__name__)


class BattleHandler:
    """Handles a single battle with an agent."""
    
    def __init__(self, client: ShowdownClient, agent: Agent, room_id: str):
        """
        Initialize battle handler.
        
        Args:
            client: Showdown client
            agent: Agent to use
            room_id: Battle room ID
        """
        self.client = client
        self.agent = agent
        self.room_id = room_id
        self.state: Optional[BattleState] = None
        self.our_player_id: Optional[str] = None
        self.finished = False
    
    async def handle_message(self, room_id: str, line: str):
        """
        Handle a battle message.
        
        Args:
            room_id: Room ID
            line: Message line
        """
        if self.state is None:
            # Determine our player ID
            if "|player|p1|" in line and self.client.username in line:
                self.our_player_id = "p1"
            elif "|player|p2|" in line and self.client.username in line:
                self.our_player_id = "p2"
            
            if self.our_player_id:
                self.state = BattleState(our_player_id=self.our_player_id)
                logger.info(f"Initialized battle state as {self.our_player_id}")
        
        if self.state:
            # Update state
            self.state.update(line)
            
            # Check if battle started
            if "|start" in line and not self.finished:
                self.agent.battle_start(self.state)
            
            # Check if we need to make a decision
            if "|request|" in line:
                await self._make_decision()
            
            # Check if battle ended
            if "|win|" in line or "|tie" in line:
                await self._handle_battle_end()
    
    async def _make_decision(self):
        """Make a decision and send action."""
        if not self.state or self.finished:
            return
        
        try:
            # Get legal actions
            legal_actions = self.state.get_legal_actions()
            
            if not legal_actions:
                logger.debug("No legal actions available")
                return
            
            # Agent chooses action
            action = self.agent.choose_move(self.state)
            
            logger.info(f"Chose action: {action.type} {action.value}")
            
            # Send action
            await self.client.send_action(self.room_id, action)
            
        except Exception as e:
            logger.error(f"Error making decision: {e}", exc_info=True)
    
    async def _handle_battle_end(self):
        """Handle battle end."""
        if self.finished or not self.state:
            return
        
        self.finished = True
        
        # Determine if we won
        won = False
        if self.state.winner:
            if self.state.winner == self.state.our_side.username:
                won = True
            elif self.state.winner == "tie":
                won = False  # Treat tie as loss
        
        # Notify agent
        self.agent.battle_end(self.state, won)
        
        # Leave battle
        await asyncio.sleep(2)  # Wait a bit before leaving
        await self.client.leave_battle(self.room_id)
