"""Reinforcement learning agent using Stable-Baselines3."""
import logging
from typing import Optional, Dict, Any
import numpy as np
from stable_baselines3 import PPO, DQN, A2C
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
import torch

from ..agents.base_agent import Agent
from ..battle.state import BattleState
from ..connection.protocol import Action
from .pokemon_env import PokemonBattleEnv

logger = logging.getLogger(__name__)


class TensorboardCallback(BaseCallback):
    """Callback for logging training metrics."""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        return True
    
    def _on_rollout_end(self) -> None:
        """Log metrics at end of rollout."""
        if len(self.model.ep_info_buffer) > 0:
            ep_info = self.model.ep_info_buffer[-1]
            if "r" in ep_info:
                self.logger.record("rollout/episode_reward", ep_info["r"])
            if "l" in ep_info:
                self.logger.record("rollout/episode_length", ep_info["l"])


class RLAgent(Agent):
    """
    Reinforcement Learning agent using Stable-Baselines3.
    
    Supports PPO, DQN, and A2C algorithms.
    """
    
    def __init__(
        self,
        algorithm: str = "PPO",
        model_path: Optional[str] = None,
        device: str = "auto",
        **kwargs
    ):
        """
        Initialize RL agent.
        
        Args:
            algorithm: Algorithm to use ("PPO", "DQN", "A2C")
            model_path: Path to load pretrained model
            device: Device to use ("cpu", "cuda", "auto")
            **kwargs: Additional arguments for the algorithm
        """
        super().__init__(name=f"RLAgent-{algorithm}")
        
        self.algorithm_name = algorithm
        self.device = device
        
        # Create environment
        self.env = PokemonBattleEnv()
        
        # Create or load model
        if model_path:
            self.model = self._load_model(model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = self._create_model(**kwargs)
            logger.info(f"Created new {algorithm} model")
    
    def _create_model(self, **kwargs):
        """Create a new model."""
        # Default hyperparameters
        default_params = {
            "policy": "MlpPolicy",
            "env": self.env,
            "verbose": 1,
            "device": self.device,
        }
        
        # Merge with user params
        params = {**default_params, **kwargs}
        
        # Create model based on algorithm
        if self.algorithm_name == "PPO":
            return PPO(**params)
        elif self.algorithm_name == "DQN":
            return DQN(**params)
        elif self.algorithm_name == "A2C":
            return A2C(**params)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
    
    def _load_model(self, model_path: str):
        """Load a pretrained model."""
        if self.algorithm_name == "PPO":
            return PPO.load(model_path, env=self.env, device=self.device)
        elif self.algorithm_name == "DQN":
            return DQN.load(model_path, env=self.env, device=self.device)
        elif self.algorithm_name == "A2C":
            return A2C.load(model_path, env=self.env, device=self.device)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
    
    def train(
        self,
        total_timesteps: int = 100000,
        log_dir: str = "logs/rl",
        save_path: str = "models/rl_agent",
        eval_freq: int = 10000,
        n_eval_episodes: int = 10,
    ):
        """
        Train the RL agent.
        
        Args:
            total_timesteps: Total training steps
            log_dir: Directory for logs
            save_path: Path to save model
            eval_freq: Frequency of evaluation
            n_eval_episodes: Number of episodes for evaluation
        """
        logger.info(f"Starting training for {total_timesteps} timesteps")
        
        # Create callbacks
        callbacks = [
            TensorboardCallback(),
            EvalCallback(
                self.env,
                best_model_save_path=save_path,
                log_path=log_dir,
                eval_freq=eval_freq,
                n_eval_episodes=n_eval_episodes,
                deterministic=True,
            )
        ]
        
        # Train
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callbacks,
            log_interval=100,
        )
        
        # Save final model
        final_path = f"{save_path}/final_model"
        self.model.save(final_path)
        logger.info(f"Training complete. Model saved to {final_path}")
    
    def choose_move(self, state: BattleState) -> Action:
        """
        Choose action using trained policy.
        
        Args:
            state: Current battle state
            
        Returns:
            Chosen action
        """
        # Update environment state
        self.env.state = state
        
        # Get observation
        obs = self.env._get_observation()
        
        # Predict action
        action, _states = self.model.predict(obs, deterministic=True)
        
        # Convert to Action object
        legal_actions = state.get_legal_actions()
        
        if not legal_actions:
            return Action(type="default")
        
        # Map predicted action to legal action
        action_idx = int(action) % len(legal_actions)
        return legal_actions[action_idx]
    
    def save(self, path: str):
        """Save model to disk."""
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk."""
        self.model = self._load_model(path)
        logger.info(f"Model loaded from {path}")


def create_vectorized_env(n_envs: int = 4) -> DummyVecEnv:
    """
    Create vectorized environment for parallel training.
    
    Args:
        n_envs: Number of parallel environments
        
    Returns:
        Vectorized environment
    """
    def make_env():
        env = PokemonBattleEnv()
        env = Monitor(env)
        return env
    
    return DummyVecEnv([make_env for _ in range(n_envs)])
