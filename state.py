"""
Game State Model for Rock-Paper-Scissors-Plus

Defines the core state structure that persists across all game turns.
State is NEVER modified by the LLM directly - only through update_game_state tool.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class GameState:
    """
    Persistent game state for Rock-Paper-Scissors-Plus.
    
    Fields:
        round: Current round number (1-3)
        max_rounds: Fixed at 3 rounds
        score: Win count for user and bot
        bomb_used: Tracks if bomb has been used (once per player per game)
        history: List of all round results for explainability
        game_over: Flag set to True after round 3
                   (stored explicitly to simplify agent flow control and avoid
                   recalculating terminal conditions on every turn)
    """
    round: int = 1
    max_rounds: int = 3
    score: Dict[str, int] = field(default_factory=lambda: {"user": 0, "bot": 0})
    bomb_used: Dict[str, bool] = field(default_factory=lambda: {"user": False, "bot": False})
    history: List[Dict] = field(default_factory=list)
    game_over: bool = False


def initialize_game_state() -> GameState:
    """
    Create a fresh game state for a new game.
    
    Returns:
        GameState: Initialized state ready for round 1
    """
    return GameState()


def get_state_summary(state: GameState) -> str:
    """
    Generate a human-readable summary of the current game state.
    
    Args:
        state: Current game state
        
    Returns:
        str: Formatted state summary
    """
    return f"""
📊 Game State:
   Round: {state.round}/{state.max_rounds}
   Score: User {state.score['user']} - {state.score['bot']} Bot
   Bombs: User {'✓' if state.bomb_used['user'] else '✗'} | Bot {'✓' if state.bomb_used['bot'] else '✗'}
   Status: {'GAME OVER' if state.game_over else 'In Progress'}
""".strip()
