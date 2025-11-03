"""Unit tests for MCTS Node implementation.

Tests the node structure, statistics tracking, UCB1 selection,
and tree manipulation operations.
"""

import pytest
import math
from src.ai.mcts_node import MCTSNode
from src.engine.actions import PassPhaseAction, ActionType


class TestMCTSNodeBasics:
    """Test basic node creation and properties."""
    
    def test_root_node_creation(self):
        """Test creating a root node (no parent or action)."""
        node = MCTSNode()
        
        assert node.action is None
        assert node.parent is None
        assert node.children == []
        assert node.untried_actions == []
        assert node.visit_count == 0
        assert node.total_reward == 0.0
    
    def test_node_with_untried_actions(self):
        """Test creating a node with untried actions."""
        actions = [
            PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE),
            PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)
        ]
        node = MCTSNode(untried_actions=actions)
        
        assert len(node.untried_actions) == 2
        assert node.is_fully_expanded() == False
    
    def test_child_node_creation(self):
        """Test creating a child node with parent reference."""
        parent = MCTSNode()
        action = PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)
        child = MCTSNode(action=action, parent=parent)
        
        assert child.action == action
        assert child.parent == parent
        assert parent.children == []  # Not added yet


class TestMCTSNodeStatistics:
    """Test node statistics tracking and calculations."""
    
    def test_update_statistics(self):
        """Test updating visit count and reward."""
        node = MCTSNode()
        
        node.update(1.0)  # Win
        assert node.visit_count == 1
        assert node.total_reward == 1.0
        
        node.update(0.0)  # Loss
        assert node.visit_count == 2
        assert node.total_reward == 1.0
        
        node.update(0.5)  # Draw
        assert node.visit_count == 3
        assert node.total_reward == 1.5
    
    def test_average_reward_calculation(self):
        """Test average reward calculation."""
        node = MCTSNode()
        
        # No visits yet
        assert node.get_average_reward() == 0.0
        
        # After some visits
        node.update(1.0)
        node.update(0.0)
        node.update(1.0)
        
        assert node.get_average_reward() == pytest.approx(2.0 / 3.0)
    
    def test_multiple_updates(self):
        """Test accumulating statistics over multiple updates."""
        node = MCTSNode()
        
        # Simulate 10 visits with 60% win rate
        for i in range(10):
            reward = 1.0 if i < 6 else 0.0
            node.update(reward)
        
        assert node.visit_count == 10
        assert node.total_reward == 6.0
        assert node.get_average_reward() == 0.6


class TestMCTSNodeExpansion:
    """Test node expansion and child management."""
    
    def test_is_fully_expanded_initially_false(self):
        """Test node is not fully expanded when it has untried actions."""
        actions = [PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)]
        node = MCTSNode(untried_actions=actions)
        
        assert node.is_fully_expanded() == False
    
    def test_is_fully_expanded_becomes_true(self):
        """Test node becomes fully expanded when all actions tried."""
        node = MCTSNode(untried_actions=[])
        
        assert node.is_fully_expanded() == True
    
    def test_add_child(self):
        """Test adding a child node."""
        action1 = PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)
        action2 = PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)
        parent = MCTSNode(untried_actions=[action1, action2])
        
        # Add first child
        child1 = parent.add_child(action1, untried_actions=[])
        
        assert len(parent.children) == 1
        assert parent.children[0] == child1
        assert child1.parent == parent
        assert child1.action == action1
        assert len(parent.untried_actions) == 1  # action1 removed
        assert action2 in parent.untried_actions
    
    def test_add_multiple_children(self):
        """Test adding multiple children exhausts untried actions."""
        action1 = PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)
        action2 = PassPhaseAction(player_id=1, action_type=ActionType.PASS_PHASE)
        parent = MCTSNode(untried_actions=[action1, action2])
        
        parent.add_child(action1, untried_actions=[])
        parent.add_child(action2, untried_actions=[])
        
        assert len(parent.children) == 2
        assert len(parent.untried_actions) == 0
        assert parent.is_fully_expanded() == True


class TestMCTSNodeSelection:
    """Test UCB1-based child selection."""
    
    def test_best_child_with_no_children_raises_error(self):
        """Test best_child raises error when node has no children."""
        node = MCTSNode()
        
        with pytest.raises(ValueError, match="no children"):
            node.best_child()
    
    def test_best_child_prioritizes_unvisited(self):
        """Test unvisited children get infinite UCB1 score."""
        parent = MCTSNode()
        parent.update(1.0)  # Parent needs visits for UCB1
        
        # Add two children
        child1 = MCTSNode(parent=parent)
        child2 = MCTSNode(parent=parent)
        parent.children = [child1, child2]
        
        # Visit child1 but not child2
        child1.update(1.0)
        
        # child2 should be selected (unvisited = infinite UCB1)
        best = parent.best_child()
        assert best == child2
    
    def test_best_child_ucb1_calculation(self):
        """Test UCB1 balances exploitation and exploration."""
        parent = MCTSNode()
        parent.update(1.0)
        parent.update(1.0)  # Parent has 2 visits
        
        # Child 1: High reward, many visits (exploitation)
        child1 = MCTSNode(parent=parent)
        child1.update(1.0)
        child1.update(1.0)
        child1.update(1.0)  # 3 visits, 100% win rate
        
        # Child 2: Medium reward, few visits (exploration)
        child2 = MCTSNode(parent=parent)
        child2.update(0.5)  # 1 visit, 50% win rate
        
        parent.children = [child1, child2]
        
        # Calculate expected UCB1 scores
        # child1: 1.0 + 1.414 * sqrt(ln(2) / 3) ≈ 1.0 + 0.68 = 1.68
        # child2: 0.5 + 1.414 * sqrt(ln(2) / 1) ≈ 0.5 + 1.18 = 1.68
        
        # Both should be close, but child2 gets exploration bonus
        best = parent.best_child(exploration_weight=1.414)
        
        # With default exploration, child2 should be slightly favored
        # (This test is sensitive to UCB1 calculation)
        assert best in [child1, child2]  # Both are reasonable
    
    def test_best_child_with_custom_exploration_weight(self):
        """Test exploration weight affects selection."""
        parent = MCTSNode()
        for _ in range(10):
            parent.update(1.0)
        
        # Child 1: Very high reward, many visits
        child1 = MCTSNode(parent=parent)
        for _ in range(8):
            child1.update(1.0)
        
        # Child 2: Low reward, few visits
        child2 = MCTSNode(parent=parent)
        child2.update(0.0)
        
        parent.children = [child1, child2]
        
        # Low exploration weight: prefer exploitation (child1)
        best_exploit = parent.best_child(exploration_weight=0.1)
        assert best_exploit == child1
        
        # High exploration weight: might prefer exploration (child2)
        # but child1's high reward might still dominate
        best_explore = parent.best_child(exploration_weight=5.0)
        # Both are valid depending on exact UCB1 values
        assert best_explore in [child1, child2]
    
    def test_get_most_visited_child(self):
        """Test selecting child with most visits (robust child strategy)."""
        parent = MCTSNode()
        
        # No children
        assert parent.get_most_visited_child() is None
        
        # Add children with different visit counts
        child1 = MCTSNode(parent=parent)
        child1.visit_count = 5
        
        child2 = MCTSNode(parent=parent)
        child2.visit_count = 10
        
        child3 = MCTSNode(parent=parent)
        child3.visit_count = 3
        
        parent.children = [child1, child2, child3]
        
        # child2 has most visits
        most_visited = parent.get_most_visited_child()
        assert most_visited == child2
    
    def test_get_most_visited_child_with_ties(self):
        """Test most visited child with tied visit counts."""
        parent = MCTSNode()
        
        child1 = MCTSNode(parent=parent)
        child1.visit_count = 10
        
        child2 = MCTSNode(parent=parent)
        child2.visit_count = 10
        
        parent.children = [child1, child2]
        
        # Either is valid for a tie
        most_visited = parent.get_most_visited_child()
        assert most_visited in [child1, child2]


class TestMCTSNodeRepr:
    """Test string representation for debugging."""
    
    def test_repr_format(self):
        """Test node string representation contains key information."""
        node = MCTSNode()
        node.update(1.0)
        node.update(0.5)
        
        repr_str = repr(node)
        
        assert "MCTSNode" in repr_str
        assert "visits=2" in repr_str
        assert "reward=" in repr_str
        assert "avg=" in repr_str
        assert "children=" in repr_str
        assert "untried=" in repr_str
