"""
Minimax AI with Alpha-Beta Pruning for TCG Deckhand.

This AI "thinks ahead" by exploring possible future game states.
Similar to chess engines, it:
1. Explores possible moves
2. Simulates opponent responses
3. Evaluates resulting positions
4. Chooses the move leading to the best outcome

Alpha-Beta Pruning cuts search time significantly by skipping
branches that can't possibly be better than what we've already found.
"""

import copy
from typing import Optional, List
from src.engine.game_state import GameState, Phase, CardState
from src.engine.actions import Action, PassPhaseAction, ActionType
from src.engine.rules import get_legal_actions
from src.ai.evaluator import BoardEvaluator


class MinimaxAI:
    """
    Strategic AI using Minimax algorithm with alpha-beta pruning.
    
    This AI "thinks ahead" by exploring future game states to depth 2-3.
    It inherits defensive capabilities from RandomAI (can use blockers/counters).
    
    How it works:
    - Maximizing player (us): Try to maximize score
    - Minimizing player (opponent): Try to minimize our score
    - Alpha-beta pruning: Skip branches that can't improve our position
    """
    
    def __init__(
        self,
        player_id: str,
        max_depth: int = 2,
        use_alpha_beta: bool = True
    ):
        """
        Initialize Minimax AI.
        
        Args:
            player_id: The player ID this AI controls
            max_depth: How many turns to look ahead (2-3 recommended)
            use_alpha_beta: Whether to use alpha-beta pruning (faster)
        """
        self.player_id = player_id
        self.max_depth = max_depth
        self.use_alpha_beta = use_alpha_beta
        self.evaluator = BoardEvaluator()
        self.name = f"MinimaxAI-d{max_depth}"
        
        # Statistics for analysis
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
    
    def get_action(self, game_state: GameState) -> Optional[Action]:
        """
        Choose the best action using Minimax search.
        
        This is the main method called by the game loop.
        It explores future possibilities and picks the best move.
        
        Args:
            game_state: Current game state
            
        Returns:
            Best action to take, or None/PassPhaseAction to pass
        """
        # Reset statistics
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
        
        # Only make decisions during MAIN phase
        if game_state.current_phase != Phase.MAIN:
            return None
        
        # Get all legal moves
        legal_actions = get_legal_actions(game_state, self.player_id)
        
        # Filter out pass actions (we'll add it back if needed)
        non_pass_actions = [
            action for action in legal_actions
            if action.action_type != ActionType.PASS_PHASE
        ]
        
        # If no actions available, must pass
        if not non_pass_actions:
            return PassPhaseAction(
                player_id=self.player_id,
                action_type=ActionType.PASS_PHASE
            )
        
        # Run minimax to find best action
        best_action, best_score = self._minimax_root(game_state, non_pass_actions)
        
        # If best action is worse than passing, consider passing
        # For now, we'll take the best action found
        return best_action
    
    def _minimax_root(
        self,
        game_state: GameState,
        actions: List[Action]
    ) -> tuple[Action, float]:
        """
        Root of minimax search - tries all possible actions.
        
        Args:
            game_state: Current game state
            actions: List of possible actions
            
        Returns:
            Tuple of (best_action, score)
        """
        best_action = actions[0]
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for action in actions:
            # Simulate taking this action
            new_state = self._simulate_action(game_state, action)
            
            if new_state is None:
                continue  # Invalid action, skip
            
            # Evaluate this branch (opponent's turn, so minimize)
            score = self._minimax(
                new_state,
                depth=1,
                is_maximizing=False,
                alpha=alpha,
                beta=beta
            )
            
            # Track best action
            if score > best_score:
                best_score = score
                best_action = action
            
            # Update alpha for pruning
            if self.use_alpha_beta:
                alpha = max(alpha, score)
        
        return best_action, best_score
    
    def _minimax(
        self,
        game_state: GameState,
        depth: int,
        is_maximizing: bool,
        alpha: float,
        beta: float
    ) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            game_state: Current game state
            depth: Current search depth
            is_maximizing: True if maximizing player's turn, False if minimizing
            alpha: Alpha value for pruning (best for maximizer)
            beta: Beta value for pruning (best for minimizer)
            
        Returns:
            Evaluation score for this position
        """
        self.nodes_evaluated += 1
        
        # Base cases: terminal state or max depth reached
        if self.evaluator.is_terminal_state(game_state):
            return self.evaluator.get_terminal_score(game_state, self.player_id)
        
        if depth >= self.max_depth:
            return self.evaluator.evaluate(game_state, self.player_id)
        
        # Get current player
        current_player_id = game_state.active_player_id
        
        # Get legal actions for current player
        legal_actions = get_legal_actions(game_state, current_player_id)
        
        # Filter out pass actions for now (simplified)
        non_pass_actions = [
            action for action in legal_actions
            if action.action_type != ActionType.PASS_PHASE
        ]
        
        # If no actions, evaluate current position
        if not non_pass_actions:
            return self.evaluator.evaluate(game_state, self.player_id)
        
        # Limit branching factor (explore top N moves to keep performance reasonable)
        MAX_ACTIONS_PER_LEVEL = 5
        if len(non_pass_actions) > MAX_ACTIONS_PER_LEVEL:
            # TODO: Add move ordering heuristic here
            # For now, just take first N
            non_pass_actions = non_pass_actions[:MAX_ACTIONS_PER_LEVEL]
        
        if is_maximizing:
            # Maximizing player (us)
            max_eval = float('-inf')
            
            for action in non_pass_actions:
                new_state = self._simulate_action(game_state, action)
                if new_state is None:
                    continue
                
                eval_score = self._minimax(
                    new_state,
                    depth + 1,
                    False,
                    alpha,
                    beta
                )
                
                max_eval = max(max_eval, eval_score)
                
                # Alpha-beta pruning
                if self.use_alpha_beta:
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        self.nodes_pruned += 1
                        break  # Beta cutoff
            
            return max_eval
        
        else:
            # Minimizing player (opponent)
            min_eval = float('inf')
            
            for action in non_pass_actions:
                new_state = self._simulate_action(game_state, action)
                if new_state is None:
                    continue
                
                eval_score = self._minimax(
                    new_state,
                    depth + 1,
                    True,
                    alpha,
                    beta
                )
                
                min_eval = min(min_eval, eval_score)
                
                # Alpha-beta pruning
                if self.use_alpha_beta:
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        self.nodes_pruned += 1
                        break  # Alpha cutoff
            
            return min_eval
    
    def _simulate_action(self, game_state: GameState, action: Action) -> Optional[GameState]:
        """
        Simulate taking an action and return the resulting game state.
        
        This creates a deep copy of the game state and applies the action.
        
        Args:
            game_state: Current game state
            action: Action to simulate
            
        Returns:
            New game state after action, or None if action invalid
        """
        # Create deep copy of game state
        try:
            new_state = copy.deepcopy(game_state)
            
            # Apply action based on type
            if action.action_type == ActionType.PLAY_CARD:
                success = self._simulate_play_card(new_state, action)
            elif action.action_type == ActionType.ATTACK:
                success = self._simulate_attack(new_state, action)
            elif action.action_type == ActionType.ATTACH_DON:
                success = self._simulate_attach_don(new_state, action)
            elif action.action_type == ActionType.PASS_PHASE:
                success = self._simulate_pass_phase(new_state, action)
            else:
                # Unsupported action type
                return None
            
            return new_state if success else None
            
        except Exception as e:
            # If simulation fails, return None
            return None
    
    def _simulate_play_card(self, game_state: GameState, action: Action) -> bool:
        """Simulate playing a card."""
        from src.engine.actions import PlayCardAction
        from src.models import Character, Event
        
        if not isinstance(action, PlayCardAction):
            return False
        
        current_player = game_state.get_active_player()
        card = action.card
        
        # Remove from hand
        if card not in current_player.hand:
            return False
        current_player.hand.remove(card)
        
        # Pay DON!! cost
        cost = action.don_to_rest
        if current_player.active_don < cost:
            current_player.hand.append(card)
            return False
        current_player.active_don -= cost
        
        # Add to appropriate zone
        if isinstance(card, Character):
            current_player.characters.append(card)
            current_player.played_this_turn.add(card.id)
            current_player.character_states[card.id] = CardState.ACTIVE
        elif isinstance(card, Event):
            current_player.trash.append(card)
        
        return True
    
    def _simulate_attack(self, game_state: GameState, action: Action) -> bool:
        """
        Simulate an attack action.
        
        For simulation purposes, we use simplified battle resolution without
        interactive defender choices (no blockers or counters).
        """
        from src.engine.actions import AttackAction
        from src.engine.battle import initiate_battle, resolve_battle, BattlePhase
        
        if not isinstance(action, AttackAction):
            return False
        
        current_player = game_state.get_active_player()
        opponent = game_state.get_opponent()
        
        # Create battle using the proper function
        try:
            battle = initiate_battle(
                game=game_state,
                attacker_id=action.attacker_id,
                target_id=action.target_id,
                is_leader_attack=action.is_leader_attack
            )
        except (ValueError, AttributeError) as e:
            # Attack setup failed
            return False
        
        # For simulation: skip blocker and counter phases
        # Go directly to resolve phase
        battle.phase = BattlePhase.RESOLVE
        
        # Resolve battle (this also rests the attacker)
        resolve_battle(game_state, battle)
        
        return True
    
    def _simulate_attach_don(self, game_state: GameState, action: Action) -> bool:
        """Simulate attaching DON!!."""
        from src.engine.actions import AttachDonAction
        
        if not isinstance(action, AttachDonAction):
            return False
        
        current_player = game_state.get_active_player()
        
        # Verify sufficient DON!!
        if current_player.active_don < action.don_count:
            return False
        
        # Move DON!!
        current_player.active_don -= action.don_count
        
        if action.target_id not in current_player.attached_don:
            current_player.attached_don[action.target_id] = 0
        current_player.attached_don[action.target_id] += action.don_count
        
        return True
    
    def _simulate_pass_phase(self, game_state: GameState, action: Action) -> bool:
        """Simulate passing phase."""
        # Just advance to next phase
        game_state.advance_phase()
        return True
    
    def get_defensive_blocker(self, game_state: GameState, battle) -> Optional[str]:
        """
        Choose a blocker during opponent's attack.
        
        For now, uses simple heuristic (can be improved later).
        
        Args:
            game_state: Current game state
            battle: The battle in progress
            
        Returns:
            Blocker character ID, or None
        """
        # TODO: Use minimax to evaluate blocking vs not blocking
        # For now, simple heuristic: block if we have a low-power blocker
        from src.engine.game_state import CardState
        from src.engine.abilities import has_blocker
        
        player = game_state.player1 if game_state.player1.player_id == self.player_id else game_state.player2
        
        # Find available blockers
        available_blockers = []
        for char in player.characters:
            if player.character_states.get(char.id, CardState.ACTIVE) == CardState.ACTIVE:
                if has_blocker(char):
                    available_blockers.append(char)
        
        if not available_blockers:
            return None
        
        # Use cheapest blocker (preserve stronger characters)
        available_blockers.sort(key=lambda c: c.cost)
        return available_blockers[0].id
    
    def get_defensive_counters(self, game_state: GameState, battle) -> List:
        """
        Choose counter cards during opponent's attack.
        
        For now, uses simple heuristic (can be improved later).
        
        Args:
            game_state: Current game state
            battle: The battle in progress
            
        Returns:
            List of counter Event cards to play
        """
        # TODO: Use minimax to evaluate counter value
        # For now, simple heuristic: use one counter if available
        from src.models import Event
        from src.engine.abilities import get_counter_value
        
        player = game_state.player1 if game_state.player1.player_id == self.player_id else game_state.player2
        
        # Find counter cards
        counters = []
        for card in player.hand:
            if isinstance(card, Event) and get_counter_value(card) > 0:
                counters.append(card)
        
        # Use one counter (can improve this logic)
        if counters:
            return [counters[0]]
        
        return []
    
    def reset(self):
        """Reset AI statistics."""
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
    
    def __repr__(self):
        return f"MinimaxAI(player={self.player_id}, depth={self.max_depth}, alpha_beta={self.use_alpha_beta})"
