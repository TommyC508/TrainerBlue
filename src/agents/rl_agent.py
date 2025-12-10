"""RL agent that uses trained Stable-Baselines3 models."""
import logging
from typing import Optional
import numpy as np

from ..agents.base_agent import Agent
from ..battle.state import BattleState
from ..connection.protocol import Action
from .environment import PokemonBattleEnv

logger = logging.getLogger(__name__)


class RLAgent(Agent):
    """Agent that uses a trained RL model to make decisions."""
    
    def __init__(self, model_path: str, algorithm: str = "PPO"):
        """
        Initialize RL agent.
        
        Args:
            model_path: Path to the trained model
            algorithm: Algorithm used (PPO, DQN, A2C)
        """
        super().__init__(name=f"RLAgent-{algorithm}")
        
        self.model_path = model_path
        self.algorithm = algorithm
        self.model = None
        self.env = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model."""
        try:
            from stable_baselines3 import PPO, DQN, A2C
            
            logger.info(f"Loading {self.algorithm} model from {self.model_path}")
            
            if self.algorithm == "PPO":
                self.model = PPO.load(self.model_path)
            elif self.algorithm == "DQN":
                self.model = DQN.load(self.model_path)
            elif self.algorithm == "A2C":
                self.model = A2C.load(self.model_path)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
            
            logger.info(f"Model loaded successfully")
            
            # Create environment for observation conversion
            self.env = PokemonBattleEnv()
            
        except ImportError:
            logger.error("stable-baselines3 not installed. Install with: pip install stable-baselines3")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def choose_move(self, state: BattleState) -> Action:
        """
        Choose an action using the trained RL model.
        
        Args:
            state: Current battle state
            
        Returns:
            Action chosen by the model
        """
        if self.model is None or self.env is None:
            logger.error("Model not loaded")
            legal_actions = state.get_legal_actions()
            return legal_actions[0] if legal_actions else Action(type="default")
        
        try:
            # Update environment state
            self.env.state = state
            
            # Get observation
            observation = self.env._get_observation()
            
            # Predict action
            action_idx, _states = self.model.predict(observation, deterministic=True)
            
            # Convert to Pokemon Showdown action
            action = self.env._action_to_showdown_action(int(action_idx))
            
            # Verify action is legal
            legal_actions = state.get_legal_actions()
            if action not in legal_actions and legal_actions:
                logger.warning(f"Model chose illegal action, using first legal action")
                return legal_actions[0]
            
            logger.debug(f"RL model chose: {action.type} {action.value}")
            return action
            
        except Exception as e:
            logger.error(f"Error predicting action: {e}")
            # Fallback to first legal action
            legal_actions = state.get_legal_actions()
            return legal_actions[0] if legal_actions else Action(type="default")
