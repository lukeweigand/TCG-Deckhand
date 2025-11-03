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
from src.engine.game import Game, GameResult
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
        self.difficulty = difficulty
        self.exploration_weight = exploration_weight
        
        # Statistics tracking
        self.last_search_time = 0.0
        self.last_iterations = 0
        self.last_root_visits = 0
    
    def choose_action(self, game: Game) -> Action:
        """Choose the best action using MCTS.
        
        Args:
            game: Current game state
            
        Returns:
            Best action found by MCTS
        """
        # Get legal actions
        legal_actions = get_legal_actions(game.state, game.state.active_player_id)
        
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
            self._mcts_iteration(game, root)
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
    
    def _mcts_iteration(self, game: Game, root: MCTSNode) -> None:
        """Run one iteration of MCTS (selection, expansion, simulation, backpropagation).
        
        Args:
            game: Current game state
            root: Root node of the search tree
        """
        # Phase 1: Selection - Navigate to a leaf node
        node = root
        game_copy = self._copy_game_state(game)
        
        while node.is_fully_expanded() and node.children:
            node = node.best_child(self.exploration_weight)
            # Apply action to game copy
            if node.action:
                game_copy.execute_action(node.action)
        
        # Phase 2: Expansion - Add a new child if not terminal
        if not node.is_fully_expanded() and not self._is_terminal(game_copy):
            # Pick an untried action
            action = node.untried_actions[0]
            
            # Apply action and get new legal actions
            game_copy.execute_action(action)
            new_legal_actions = get_legal_actions(
                game_copy.state,
                game_copy.state.active_player_id
            )
            
            # Add child node
            node = node.add_child(action, new_legal_actions)
        
        # Phase 3: Simulation - Play out the game randomly
        reward = self._simulate(game_copy, root)
        
        # Phase 4: Backpropagation - Update all ancestor nodes
        while node is not None:
            node.update(reward)
            node = node.parent
            # Flip reward for opponent's perspective
            reward = 1.0 - reward
    
    def _simulate(self, game: Game, root: MCTSNode) -> float:
        """Simulate a random game to completion.
        
        Args:
            game: Game state to simulate from
            root: Root node (to determine perspective)
            
        Returns:
            Reward from root player's perspective (1.0 = win, 0.0 = loss, 0.5 = draw)
        """
        # Remember which player is making the decision at root
        root_player_id = game.state.active_player_id
        
        # Play out the game with random moves (limit to 50 turns to avoid infinite loops)
        max_simulation_turns = 50
        simulation_turns = 0
        
        while not self._is_terminal(game) and simulation_turns < max_simulation_turns:
            # Get legal actions for current player
            legal_actions = get_legal_actions(game.state, game.state.active_player_id)
            
            if not legal_actions:
                break
            
            # Choose random action
            action = random.choice(legal_actions)
            
            # Execute action
            game.execute_action(action)
            
            simulation_turns += 1
        
        # Evaluate result from root player's perspective
        if game.state.result == GameResult.ONGOING:
            # Timeout - use board evaluation as tiebreaker
            from src.ai.evaluator import BoardEvaluator
            evaluator = BoardEvaluator()
            score = evaluator.evaluate(game.state, root_player_id)
            # Normalize score to [0, 1] range
            return (score + 1000) / 2000  # Assuming scores are roughly -1000 to +1000
        
        # Check if root player won
        winner_id = game.state.result.value.lower()
        if winner_id == f"player{root_player_id}_wins":
            return 1.0  # Win
        elif winner_id == "draw":
            return 0.5  # Draw
        else:
            return 0.0  # Loss
    
    def _copy_game_state(self, game: Game) -> Game:
        """Create a deep copy of the game state for simulation.
        
        Args:
            game: Game to copy
            
        Returns:
            Independent copy of the game
        """
        return copy.deepcopy(game)
    
    def _is_terminal(self, game: Game) -> bool:
        """Check if the game is in a terminal state.
        
        Args:
            game: Game to check
            
        Returns:
            True if game is over
        """
        return game.state.result != GameResult.ONGOING
    
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
        # Get this player's state
        player_id = game_state.active_player_id
        opponent_id = 2 if player_id == 1 else 1
        player = game_state.player1 if game_state.player1.player_id == opponent_id else game_state.player2
        
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
        # Get this player's state
        player_id = game_state.active_player_id
        opponent_id = 2 if player_id == 1 else 1
        player = game_state.player1 if game_state.player1.player_id == opponent_id else game_state.player2
        
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
