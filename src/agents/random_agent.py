"""Random agent that chooses actions randomly."""
import random
from .base_agent import Agent
from ..battle.state import BattleState
from ..connection.protocol import Action


class RandomAgent(Agent):
    """Agent that chooses actions randomly."""
    
    def __init__(self):
        super().__init__(name="RandomAgent")
    
    def choose_move(self, state: BattleState) -> Action:
        """
        Choose a random legal action.
        
        Args:
            state: Current battle state
            
        Returns:
            Random action
        """
        legal_actions = state.get_legal_actions()
        
        if not legal_actions:
            # No legal actions, return default
            return Action(type="default")
        
        # Choose random action
        return random.choice(legal_actions)
