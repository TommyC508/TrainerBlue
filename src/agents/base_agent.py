"""Base agent interface."""
from abc import ABC, abstractmethod
from typing import Optional
import logging
from ..battle.state import BattleState
from ..connection.protocol import Action

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for Pokemon battle agents."""
    
    def __init__(self, name: str = "Agent"):
        """
        Initialize agent.
        
        Args:
            name: Agent name for logging
        """
        self.name = name
        self.battles_played = 0
        self.battles_won = 0
    
    @abstractmethod
    def choose_move(self, state: BattleState) -> Action:
        """
        Choose an action given the current battle state.
        
        Args:
            state: Current battle state
            
        Returns:
            Action to take
        """
        pass
    
    def battle_start(self, state: BattleState):
        """
        Called when battle starts.
        
        Args:
            state: Initial battle state
        """
        logger.info(f"{self.name} starting battle")
    
    def battle_end(self, state: BattleState, won: bool):
        """
        Called when battle ends.
        
        Args:
            state: Final battle state
            won: Whether we won the battle
        """
        self.battles_played += 1
        if won:
            self.battles_won += 1
        
        win_rate = (self.battles_won / self.battles_played * 100) if self.battles_played > 0 else 0
        logger.info(
            f"{self.name} finished battle. "
            f"Result: {'WIN' if won else 'LOSS'}. "
            f"Record: {self.battles_won}/{self.battles_played} ({win_rate:.1f}%)"
        )
    
    def turn_start(self, state: BattleState):
        """
        Called at the start of each turn.
        
        Args:
            state: Current battle state
        """
        pass
    
    def turn_end(self, state: BattleState):
        """
        Called at the end of each turn.
        
        Args:
            state: Current battle state
        """
        pass
    
    @property
    def win_rate(self) -> float:
        """Get win rate as percentage."""
        if self.battles_played == 0:
            return 0.0
        return (self.battles_won / self.battles_played) * 100
