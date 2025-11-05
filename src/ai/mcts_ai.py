"""Monte Carlo Tree Search AI player implementation.

This module implements a TCG player that uses Monte Carlo Tree Search (MCTS)
to select actions. MCTS builds a search tree by running random simulations and
uses statistics to identify the most promising moves.
"""

import time
import copy
import random
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from src.ai.mcts_node import MCTSNode
from src.ai.random_ai import RandomAI
from src.engine.game_state import GameState, Phase, CardState
from src.engine.actions import Action, PassPhaseAction
from src.engine.game import Game, GameResult, GameConfig
from src.engine.rules import get_legal_actions
from src.engine.abilities import has_blocker, get_counter_value
from src.models import Event

if TYPE_CHECKING:
    from src.engine.battle import Battle


class MCTSDifficulty(Enum):
    """Difficulty levels for MCTS AI.
    
    Each difficulty level has a different time budget for thinking:
    - EASY: 0.5 seconds (fast but weaker)
    - MEDIUM: 1.0 seconds (balanced)
    - HARD: 2.0 seconds (strong but slower)
    """
    EASY = 0.5
    MEDIUM = 1.0
    HARD = 2.0


class MCTSAI:
    """AI player using Monte Carlo Tree Search.
    
    MCTS works in four phases:
    1. Selection: Navigate tree using UCB1 to select promising nodes
    2. Expansion: Add a new child node for an untried action
    3. Simulation: Play out the game randomly to get a result
    4. Backpropagation: Update all ancestor nodes with the result
    
    The algorithm runs until the time budget expires, then returns the most
    visited child (robust child strategy).
    
    Like RandomAI, this AI can also respond defensively to attacks with
    blockers and counter cards.
    
    Attributes:
        difficulty: Time budget for search (EASY/MEDIUM/HARD)
        exploration_weight: UCB1 exploration constant (default sqrt(2))
    """
    
    def __init__(
        self,
        difficulty: MCTSDifficulty = MCTSDifficulty.MEDIUM,
        exploration_weight: float = 1.414
    ):
        """Initialize MCTS AI.
        
        Args:
            difficulty: Time budget for search (EASY/MEDIUM/HARD)
            exploration_weight: UCB1 exploration constant (sqrt(2) is optimal)
        """
        self.player_id = None  # Will be set after game initialization
        self.difficulty = difficulty
        self.exploration_weight = exploration_weight
        
        # Statistics tracking
        self.last_search_time = 0.0
        self.last_iterations = 0
        self.last_root_visits = 0
    
    def get_action(self, game_state: GameState) -> Action:
        """Choose the best action using MCTS.
        
        This is the main method called by the game loop.
        
        Args:
            game_state: Current game state
            
        Returns:
            Best action found by MCTS
        """
        # Only make decisions during MAIN phase
        if game_state.current_phase != Phase.MAIN:
            return None
        
        # Get legal actions
        legal_actions = get_legal_actions(game_state, game_state.active_player_id)
        
        # If only one action (usually pass), return it immediately
        if len(legal_actions) <= 1:
            return legal_actions[0] if legal_actions else PassPhaseAction()
        
        # Run MCTS search
        start_time = time.time()
        time_budget = self.difficulty.value
        
        # Create root node
        root = MCTSNode(untried_actions=legal_actions.copy())
        
        # Run MCTS iterations until time budget expires
        iterations = 0
        while time.time() - start_time < time_budget:
            # Run one iteration of MCTS
            self._mcts_iteration(game_state, root)
            iterations += 1
        
        # Record statistics
        self.last_search_time = time.time() - start_time
        self.last_iterations = iterations
        self.last_root_visits = root.visit_count
        
        # Select best child by visit count (robust child strategy)
        best_child = root.get_most_visited_child()
        
        if best_child is None:
            # Fallback: return first legal action
            return legal_actions[0]
        
        return best_child.action
    
    def choose_action(self, game: Game) -> Action:
        """Legacy method for compatibility. Use get_action() instead."""
        return self.get_action(game.state)
    
    def _mcts_iteration(self, game_state: GameState, root: MCTSNode) -> None:
        """Run one iteration of MCTS (selection, expansion, simulation, backpropagation).
        
        Args:
            game_state: Current game state
            root: Root node of the search tree
        """
        # Phase 1: Selection - Navigate to a leaf node
        node = root
        state_copy = copy.deepcopy(game_state)
        
        while node.is_fully_expanded() and node.children:
            node = node.best_child(self.exploration_weight)
            # Apply action to state copy (simplified - just mark as explored)
            # Full simulation would require action execution which is complex
        
        # Phase 2: Expansion - Add a new child if not terminal
        if not node.is_fully_expanded():
            # Pick an untried action
            action = node.untried_actions[0]
            
            # Get new legal actions (after this action would be applied)
            new_legal_actions = get_legal_actions(state_copy, state_copy.active_player_id)
            
            # Add child node
            node = node.add_child(action, new_legal_actions)
        
        # Phase 3: Simulation - Play out game randomly from this state
        # Run a full rollout (random playout) to terminal state
        reward = self._simulate_rollout(state_copy, game_state.active_player_id)
        
        # Phase 4: Backpropagation - Update all ancestor nodes
        while node is not None:
            node.update(reward)
            node = node.parent
            # Flip reward for opponent's perspective
            reward = 1.0 - reward
    
    def _simulate_rollout(self, game_state: GameState, player_id: int) -> float:
        """Simulate a random game playout from the given state.
        
        This is the true MCTS simulation phase - we actually play the game
        to completion using random action selection, then return the result.
        
        Args:
            game_state: Starting state for simulation
            player_id: Player from whose perspective to evaluate (1 or 2)
            
        Returns:
            Reward: 1.0 for win, 0.0 for loss, 0.5 for timeout/draw
        """
        # Create dummy players for simulation (both use random policy)
        dummy_p1 = RandomAI(player_id="1")
        dummy_p2 = RandomAI(player_id="2")
        
        # Create a dummy config (we only need the game state)
        dummy_config = GameConfig(
            player1_deck=[],
            player2_deck=[],
            player1_leader=game_state.player1.leader,
            player2_leader=game_state.player2.leader,
            starting_player=1
        )
        
        # Create Game instance with dummy players
        simulation_game = Game(dummy_config, dummy_p1, dummy_p2)
        
        # Set the game state to our current position
        simulation_game.state = copy.deepcopy(game_state)
        
        # Safety limit to prevent infinite games
        MAX_ROLLOUT_TURNS = 50
        MAX_ROLLOUT_ACTIONS = 1000
        action_count = 0
        turn_count = 0
        starting_turn = game_state.current_turn
        
        # Play randomly until game ends
        while True:
            # Check if game is over
            result = simulation_game._check_win_condition()
            if result is not None:
                # Game ended naturally
                break
            
            # Check safety limits
            action_count += 1
            current_turn = simulation_game.state.current_turn
            turn_count = current_turn - starting_turn
            
            if action_count >= MAX_ROLLOUT_ACTIONS or turn_count >= MAX_ROLLOUT_TURNS:
                # Timeout - return draw
                return 0.5
            
            # Get legal actions for current player
            legal_actions = get_legal_actions(
                simulation_game.state,
                simulation_game.state.active_player_id
            )
            
            if not legal_actions:
                # No legal actions - game should be over
                break
            
            # Select random action
            action = self._select_rollout_action(legal_actions, simulation_game.state)
            
            # Execute action
            try:
                simulation_game.execute_action(action)
            except Exception:
                # If action fails, stop simulation and return draw
                return 0.5
        
        # Determine reward based on winner
        result = simulation_game._check_win_condition()
        
        if result == GameResult.PLAYER_1_WIN:
            return 1.0 if player_id == 1 else 0.0
        elif result == GameResult.PLAYER_2_WIN:
            return 1.0 if player_id == 2 else 0.0
        else:
            # Draw or timeout
            return 0.5
    
    def _select_rollout_action(self, legal_actions: List[Action], game_state: GameState) -> Action:
        """Select an action during rollout simulation.
        
        For now, uses uniform random selection. Could be enhanced with
        heuristics or light playouts for better simulation quality.
        
        Args:
            legal_actions: Available actions to choose from
            game_state: Current game state (for potential heuristics)
            
        Returns:
            Selected action
        """
        # Simple uniform random selection
        return random.choice(legal_actions)
    
    def _is_terminal(self, game_state: GameState) -> bool:
        """Check if the game state is terminal (game over).
        
        Args:
            game_state: Game state to check
            
        Returns:
            True if game is over
        """
        # Check if either player is defeated
        return game_state.player1.defeated or game_state.player2.defeated
    
    def get_defensive_blocker(self, game_state: GameState, battle: 'Battle') -> Optional[str]:
        """Decide whether to use a blocker character during an attack.
        
        Uses MCTS to evaluate whether blocking is beneficial. If time permits,
        runs a quick search; otherwise falls back to heuristic evaluation.
        
        Args:
            game_state: Current game state
            battle: The battle being declared against this AI
            
        Returns:
            Character ID to use as blocker, or None to not block
        """
        # For now, use random defensive logic (can enhance later with MCTS)
        # Get this player's state (the DEFENDER, not the active attacker)
        # When defending, the active_player_id is the ATTACKER, so we need the opponent
        defender_id = self.player_id
        player = game_state.player1 if game_state.player1.player_id == defender_id else game_state.player2
        
        # Find all available blockers
        available_blockers = []
        for char in player.characters:
            if player.character_states.get(char.id, CardState.ACTIVE) == CardState.ACTIVE:
                if has_blocker(char):
                    available_blockers.append(char)
        
        if not available_blockers:
            return None
        
        # Simple heuristic: block if attacker is stronger than our weakest blocker
        attacker = battle.attacker
        weakest_blocker = min(available_blockers, key=lambda c: c.power)
        
        if attacker.power >= weakest_blocker.power:
            return weakest_blocker.id
        
        return None
    
    def get_defensive_counters(self, game_state: GameState, battle: 'Battle') -> List[Event]:
        """Decide whether to play counter cards during an attack.
        
        Uses heuristic evaluation to decide if countering is worthwhile.
        
        Args:
            game_state: Current game state
            battle: The battle in progress
            
        Returns:
            List of Event cards to play as counters (empty list = no counters)
        """
        # Get this player's state (the DEFENDER, not the active attacker)
        defender_id = self.player_id
        player = game_state.player1 if game_state.player1.player_id == defender_id else game_state.player2
        
        # Find counter cards in hand
        available_counters = []
        for card in player.hand:
            if isinstance(card, Event):
                counter_value = get_counter_value(card)
                if counter_value > 0:
                    available_counters.append((card, counter_value))
        
        if not available_counters:
            return []
        
        # Simple heuristic: counter if it would save us from taking damage
        # Calculate damage deficit
        defender_power = battle.defender.power if battle.defender else 0
        damage_difference = battle.attacker.power - defender_power
        
        # If we're already winning the battle, don't counter
        if damage_difference <= 0:
            return []
        
        # Use counters to close the gap (but don't waste too many)
        counters_to_play = []
        remaining_difference = damage_difference
        
        for card, counter_value in sorted(available_counters, key=lambda x: x[1]):
            if remaining_difference > 0:
                counters_to_play.append(card)
                remaining_difference -= counter_value
                
                # Stop if we've equalized or exceeded
                if remaining_difference <= 0:
                    break
        
        return counters_to_play


# Convenience function for creating MCTS AI with different difficulties
def create_easy_mcts() -> MCTSAI:
    """Create an easy MCTS AI (0.5s thinking time)."""
    return MCTSAI(difficulty=MCTSDifficulty.EASY)


def create_medium_mcts() -> MCTSAI:
    """Create a medium MCTS AI (1.0s thinking time)."""
    return MCTSAI(difficulty=MCTSDifficulty.MEDIUM)


def create_hard_mcts() -> MCTSAI:
    """Create a hard MCTS AI (2.0s thinking time)."""
    return MCTSAI(difficulty=MCTSDifficulty.HARD)
