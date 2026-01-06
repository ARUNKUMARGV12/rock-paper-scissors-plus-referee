"""
Game Tools for Rock-Paper-Scissors-Plus

Three mandatory tools with strict separation of concerns:
1. validate_move: Input validation only (no state mutation)
2. resolve_round: Pure game logic (no state mutation)
3. update_game_state: ONLY place where state is modified
"""

from typing import Dict, Optional
from state import GameState
import copy


# Valid moves in the game
VALID_MOVES = {"rock", "paper", "scissors", "bomb"}


def validate_move(move: str, game_state: GameState) -> Dict:
    """
    Tool 1: Validate and normalize user input.
    
    This tool performs ONLY validation - it does NOT mutate state.
    
    Args:
        move: Raw user input string
        game_state: Current game state (read-only)
        
    Returns:
        dict: {
            "valid": bool,
            "normalized_move": str or None,
            "error": str or None
        }
    """
    # Normalize input
    normalized = move.strip().lower()
    
    # Check if move is valid
    if normalized not in VALID_MOVES:
        return {
            "valid": False,
            "normalized_move": None,
            "error": f"Invalid move '{move}'. Valid moves: rock, paper, scissors, bomb"
        }
    
    # Check bomb usage constraint
    if normalized == "bomb" and game_state.bomb_used["user"]:
        return {
            "valid": False,
            "normalized_move": None,
            "error": "You have already used your bomb! Choose: rock, paper, or scissors"
        }
    
    # Valid move
    return {
        "valid": True,
        "normalized_move": normalized,
        "error": None
    }


def resolve_round(user_move: str, bot_move: str) -> Dict:
    """
    Tool 2: Pure game logic - determine round winner.
    
    This tool is deterministic and has NO side effects.
    Assumes both moves are valid (validation happens separately).
    
    Args:
        user_move: User's move (must be valid: rock/paper/scissors/bomb)
        bot_move: Bot's move (always valid)
        
    Returns:
        dict: {
            "winner": "user" | "bot" | "draw",
            "reason": str (explanation)
        }
    """
    # Bomb logic
    if user_move == "bomb" and bot_move == "bomb":
        return {
            "winner": "draw",
            "reason": "Both players used bomb - it's a draw!"
        }
    
    if user_move == "bomb":
        return {
            "winner": "user",
            "reason": "Bomb beats everything!"
        }
    
    if bot_move == "bomb":
        return {
            "winner": "bot",
            "reason": "Bot's bomb beats everything!"
        }
    
    # Standard Rock-Paper-Scissors logic
    if user_move == bot_move:
        return {
            "winner": "draw",
            "reason": f"Both played {user_move}"
        }
    
    # Determine winner
    win_conditions = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }
    
    if win_conditions[user_move] == bot_move:
        return {
            "winner": "user",
            "reason": f"{user_move.capitalize()} beats {bot_move}"
        }
    else:
        return {
            "winner": "bot",
            "reason": f"{bot_move.capitalize()} beats {user_move}"
        }


def update_game_state(
    game_state: GameState,
    user_move: Optional[str],
    bot_move: str,
    round_result: Dict
) -> GameState:
    """
    Tool 3: Apply round results to game state.
    
    This is the ONLY place where state is mutated.
    
    Although in-place mutation is acceptable in ADK, this implementation
    returns a new state for easier debugging and testability.
    
    Args:
        game_state: Current game state
        user_move: User's move (None if invalid)
        bot_move: Bot's move
        round_result: Result from resolve_round or agent-determined result
        
    Returns:
        GameState: Updated game state (new copy)
    """
    # Create a deep copy to avoid mutating the original
    new_state = copy.deepcopy(game_state)
    
    # Update scores based on winner
    if round_result["winner"] == "user":
        new_state.score["user"] += 1
    elif round_result["winner"] == "bot":
        new_state.score["bot"] += 1
    # Draw: no score change
    
    # Mark bomb usage
    if user_move == "bomb":
        new_state.bomb_used["user"] = True
    if bot_move == "bomb":
        new_state.bomb_used["bot"] = True
    
    # Record in history (including invalid moves for explainability)
    new_state.history.append({
        "round": new_state.round,
        "user_move": user_move if user_move is not None else "INVALID",
        "bot_move": bot_move,
        "winner": round_result["winner"],
        "reason": round_result["reason"]
    })
    
    # Increment round counter
    new_state.round += 1
    
    # Check if game is over
    if new_state.round > new_state.max_rounds:
        new_state.game_over = True
    
    return new_state
