"""Heuristic agent that uses rule-based decision making."""
import logging
from typing import List, Tuple, Optional
from .base_agent import Agent
from ..battle.state import BattleState
from ..connection.protocol import Action
from ..data.models import Pokemon, Move
from ..data.damage_calculator import DamageCalculator
from ..data.type_effectiveness import get_type_effectiveness

logger = logging.getLogger(__name__)


class HeuristicAgent(Agent):
    """Agent that uses heuristics to make decisions."""
    
    def __init__(self):
        super().__init__(name="HeuristicAgent")
        self.damage_calc = DamageCalculator()
    
    def choose_move(self, state: BattleState) -> Action:
        """
        Choose action based on heuristics.
        
        Strategy:
        1. If in danger, consider switching
        2. Otherwise, choose best offensive move
        3. Consider type effectiveness and damage
        
        Args:
            state: Current battle state
            
        Returns:
            Chosen action
        """
        legal_actions = state.get_legal_actions()
        
        if not legal_actions:
            return Action(type="default")
        
        our_pokemon = state.get_our_active_pokemon()
        opp_pokemon = state.get_opponent_active_pokemon()
        
        if not our_pokemon or not opp_pokemon:
            # Can't make informed decision, choose random
            import random
            return random.choice(legal_actions)
        
        # Check if we should switch (if in danger and have good switch)
        if self._should_switch(state, our_pokemon, opp_pokemon):
            switch_action = self._choose_switch(state, opp_pokemon, legal_actions)
            if switch_action:
                logger.info(f"Switching out {our_pokemon.species}")
                return switch_action
        
        # Choose best move
        move_action = self._choose_best_move(state, our_pokemon, opp_pokemon, legal_actions)
        if move_action:
            return move_action
        
        # Fallback: choose first legal action
        return legal_actions[0]
    
    def _should_switch(
        self,
        state: BattleState,
        our_pokemon: Pokemon,
        opp_pokemon: Pokemon
    ) -> bool:
        """
        Decide if we should switch.
        
        Switch if:
        - Our Pokemon is low HP and threatened
        - We have bad type matchup
        - We're at risk of being KO'd
        """
        # Don't switch if we can't
        switch_actions = [a for a in state.get_legal_actions() if a.type == "switch"]
        if not switch_actions:
            return False
        
        # Switch if very low HP
        if our_pokemon.hp_percent < 20:
            return True
        
        # Switch if bad type matchup and decent HP
        if our_pokemon.hp_percent > 50:
            # Simple type check (would need move data for better check)
            # For now, just check if opponent has type advantage
            return False  # Simplified for now
        
        return False
    
    def _choose_switch(
        self,
        state: BattleState,
        opp_pokemon: Pokemon,
        legal_actions: List[Action]
    ) -> Optional[Action]:
        """
        Choose best switch target.
        
        Prefer Pokemon with:
        - Type advantage over opponent
        - High HP
        - Not fainted
        """
        switch_actions = [a for a in legal_actions if a.type == "switch"]
        
        if not switch_actions:
            return None
        
        best_switch = None
        best_score = -999999
        
        for action in switch_actions:
            switch_idx = int(action.value) - 1  # Convert to 0-indexed
            if switch_idx >= len(state.our_side.team):
                continue
            
            pokemon = state.our_side.team[switch_idx]
            
            if not pokemon.is_alive():
                continue
            
            score = self._evaluate_switch(pokemon, opp_pokemon)
            
            if score > best_score:
                best_score = score
                best_switch = action
        
        return best_switch
    
    def _evaluate_switch(self, pokemon: Pokemon, opp_pokemon: Pokemon) -> float:
        """
        Evaluate how good a switch target is.
        
        Returns:
            Score (higher is better)
        """
        score = 0.0
        
        # Prefer high HP
        score += pokemon.hp_percent
        
        # Prefer Pokemon that can take hits
        # (Would need type data and move data for proper calculation)
        
        # Prefer Pokemon that can deal damage
        # (Would need move data for proper calculation)
        
        return score
    
    def _choose_best_move(
        self,
        state: BattleState,
        our_pokemon: Pokemon,
        opp_pokemon: Pokemon,
        legal_actions: List[Action]
    ) -> Optional[Action]:
        """
        Choose best offensive move.
        
        Prefer moves that:
        - Deal more damage
        - Are super effective
        - Have good accuracy
        """
        move_actions = [a for a in legal_actions if a.type == "move"]
        
        if not move_actions:
            return None
        
        best_move = None
        best_score = -999999
        
        for action in move_actions:
            move_idx = int(action.value) - 1  # Convert to 0-indexed
            
            if move_idx >= len(our_pokemon.moves):
                continue
            
            move_name = our_pokemon.moves[move_idx]
            score = self._evaluate_move(move_name, our_pokemon, opp_pokemon, state)
            
            if score > best_score:
                best_score = score
                best_move = action
        
        return best_move
    
    def _evaluate_move(
        self,
        move_name: str,
        our_pokemon: Pokemon,
        opp_pokemon: Pokemon,
        state: BattleState
    ) -> float:
        """
        Evaluate how good a move is.
        
        Returns:
            Score (higher is better)
        """
        # Create simplified move object for damage calculation
        # In a real implementation, we'd load actual move data
        move = Move(
            name=move_name,
            type="Normal",  # Would need to look up actual type
            category="Physical",  # Would need to look up actual category
            power=80,  # Default power
            accuracy=100,
            pp=10
        )
        
        # Simplified scoring based on move name patterns
        score = 0.0
        
        # Prefer attacking moves
        if any(keyword in move_name.lower() for keyword in ["punch", "kick", "slash", "beam", "blast"]):
            score += 50
        
        # Penalize status moves when opponent is low HP
        if any(keyword in move_name.lower() for keyword in ["toxic", "will-o-wisp", "thunder wave"]):
            if opp_pokemon.hp_percent < 50:
                score -= 30
            else:
                score += 20
        
        # Prefer setup moves when we're healthy
        if any(keyword in move_name.lower() for keyword in ["dance", "sharpen", "bulk up", "calm mind"]):
            if our_pokemon.hp_percent > 70:
                score += 30
            else:
                score -= 20
        
        # Prefer recovery when low HP
        if any(keyword in move_name.lower() for keyword in ["recover", "roost", "synthesis"]):
            if our_pokemon.hp_percent < 50:
                score += 100
            else:
                score -= 50
        
        # Base score on estimated damage
        # (Simplified - would use actual move data and damage calc in real implementation)
        estimated_damage = 40  # Default
        score += estimated_damage
        
        # Prefer moves against lower HP opponents (go for KO)
        if opp_pokemon.hp_percent < 50:
            score += 20
        if opp_pokemon.hp_percent < 25:
            score += 30
        
        return score
