"""
Game engine package for TCG Deckhand.

This package contains the core game logic, state management,
and rules engine for One Piece TCG.
"""

from .game_state import GameState, PlayerState, Phase, CardState
from .game_init import initialize_game, get_game_summary, mulligan
from .actions import (
    Action, ActionType, AnyAction,
    PlayCardAction, AttackAction, AttachDonAction, DetachDonAction,
    UseCounterAction, UseBlockerAction, ActivateAbilityAction,
    UseTriggerAction, DeclineTriggerAction, PassPhaseAction, MulliganAction
)
from .battle import Battle, BattlePhase, initiate_battle, apply_blocker, apply_counter, resolve_battle, execute_full_battle
from .rules import validate_action, get_legal_actions, ValidationError
from .abilities import (
    AbilityType, Ability, parse_abilities, has_ability,
    has_rush, has_blocker, has_trigger, get_counter_value, get_ability_don_cost
)

__all__ = [
    # Game State
    "GameState",
    "PlayerState",
    "Phase",
    "CardState",
    # Initialization
    "initialize_game",
    "get_game_summary",
    "mulligan",
    # Actions
    "Action",
    "ActionType",
    "AnyAction",
    "PlayCardAction",
    "AttackAction",
    "AttachDonAction",
    "DetachDonAction",
    "UseCounterAction",
    "UseBlockerAction",
    "ActivateAbilityAction",
    "UseTriggerAction",
    "DeclineTriggerAction",
    "PassPhaseAction",
    "MulliganAction",
    # Battle System
    "Battle",
    "BattlePhase",
    "initiate_battle",
    "apply_blocker",
    "apply_counter",
    "resolve_battle",
    "execute_full_battle",
    # Rules
    "validate_action",
    "get_legal_actions",
    "ValidationError",
    # Abilities
    "AbilityType",
    "Ability",
    "parse_abilities",
    "has_ability",
    "has_rush",
    "has_blocker",
    "has_trigger",
    "get_counter_value",
    "get_ability_don_cost",
]

