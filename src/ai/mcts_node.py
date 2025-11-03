"""Monte Carlo Tree Search node for game state exploration.

This module implements the node structure used in MCTS, storing visit statistics,
rewards, and managing the tree structure through parent-child relationships.
"""

import math
from typing import Optional, List
from src.engine.actions import Action


class MCTSNode:
    """Node in the Monte Carlo Tree Search tree.
    
    Each node represents a game state and tracks:
    - Visit count: How many times this node has been visited
    - Total reward: Sum of rewards from all simulations through this node
    - Children: Child nodes representing actions taken from this state
    - Untried actions: Legal actions that haven't been explored yet
    
    Attributes:
        action: The action that led to this node (None for root)
        parent: Parent node in the tree (None for root)
        children: List of child nodes
        untried_actions: Actions that haven't been tried yet
        visit_count: Number of times this node has been visited
        total_reward: Sum of rewards from all simulations
    """
    
    def __init__(
        self,
        action: Optional[Action] = None,
        parent: Optional['MCTSNode'] = None,
        untried_actions: Optional[List[Action]] = None
    ):
        """Initialize a new MCTS node.
        
        Args:
            action: The action that led to this node (None for root)
            parent: Parent node (None for root)
            untried_actions: List of legal actions from this state
        """
        self.action = action
        self.parent = parent
        self.children: List[MCTSNode] = []
        self.untried_actions = untried_actions if untried_actions else []
        self.visit_count = 0
        self.total_reward = 0.0
        
    def is_fully_expanded(self) -> bool:
        """Check if all legal actions have been tried.
        
        Returns:
            True if no untried actions remain
        """
        return len(self.untried_actions) == 0
    
    def best_child(self, exploration_weight: float = 1.414) -> 'MCTSNode':
        """Select the best child using UCB1 formula.
        
        UCB1 (Upper Confidence Bound) balances exploitation (high reward) with
        exploration (few visits). The formula is:
        
        UCB1 = (reward / visits) + C * sqrt(ln(parent_visits) / visits)
        
        Where C is the exploration weight (typically sqrt(2) ≈ 1.414).
        
        Args:
            exploration_weight: Controls exploration vs exploitation trade-off
                Higher values = more exploration
                Lower values = more exploitation
                Default sqrt(2) is theoretically optimal
        
        Returns:
            Child node with highest UCB1 score
            
        Raises:
            ValueError: If called on a node with no children
        """
        if not self.children:
            raise ValueError("Cannot select best child: node has no children")
        
        # Calculate UCB1 score for each child
        def ucb1_score(child: 'MCTSNode') -> float:
            if child.visit_count == 0:
                return float('inf')  # Prioritize unvisited children
            
            # Exploitation term: average reward
            exploitation = child.total_reward / child.visit_count
            
            # Exploration term: uncertainty bonus
            exploration = exploration_weight * math.sqrt(
                math.log(self.visit_count) / child.visit_count
            )
            
            return exploitation + exploration
        
        return max(self.children, key=ucb1_score)
    
    def add_child(self, action: Action, untried_actions: List[Action]) -> 'MCTSNode':
        """Add a child node for the given action.
        
        This removes the action from untried_actions and creates a new child node.
        
        Args:
            action: The action to take
            untried_actions: Legal actions from the new state
            
        Returns:
            The newly created child node
        """
        # Remove action from untried list
        self.untried_actions.remove(action)
        
        # Create child node
        child = MCTSNode(
            action=action,
            parent=self,
            untried_actions=untried_actions
        )
        
        self.children.append(child)
        return child
    
    def update(self, reward: float) -> None:
        """Update node statistics after a simulation.
        
        Args:
            reward: Reward from the simulation (1.0 for win, 0.0 for loss, 0.5 for draw)
        """
        self.visit_count += 1
        self.total_reward += reward
    
    def get_average_reward(self) -> float:
        """Get the average reward per visit.
        
        Returns:
            Average reward (0.0 if never visited)
        """
        if self.visit_count == 0:
            return 0.0
        return self.total_reward / self.visit_count
    
    def get_most_visited_child(self) -> Optional['MCTSNode']:
        """Get the child with the most visits.
        
        Used for final action selection (robust child strategy).
        
        Returns:
            Child with highest visit count, or None if no children
        """
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.visit_count)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MCTSNode(action={self.action}, "
            f"visits={self.visit_count}, "
            f"reward={self.total_reward:.2f}, "
            f"avg={self.get_average_reward():.3f}, "
            f"children={len(self.children)}, "
            f"untried={len(self.untried_actions)})"
        )
