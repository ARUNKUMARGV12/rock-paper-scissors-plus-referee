"""
Rock-Paper-Scissors-Plus Game Referee Agent

Google ADK agent that orchestrates the game using strict tool-based architecture.
The agent NEVER directly modifies state - all mutations happen via tools.
"""

import random
from typing import Dict, Optional
from state import GameState, initialize_game_state, get_state_summary
from tools import validate_move, resolve_round, update_game_state, VALID_MOVES


class GameRefereeAgent:
    """
    Game referee agent that enforces rules and manages game flow.
    
    Architecture:
        User Input → validate_move → resolve_round → update_game_state → Response
        
    The agent orchestrates but does NOT directly mutate state.
    """
    
    def __init__(self):
        """Initialize the agent with a fresh game state."""
        self.game_state: GameState = initialize_game_state()
        self.game_started = False
    
    def start_game(self) -> str:
        """
        Initialize a new game and provide rules.
        
        Returns:
            str: Welcome message with concise rules
        """
        self.game_state = initialize_game_state()
        self.game_started = True
        
        return """
🎮 Welcome to Rock-Paper-Scissors-Plus!

📜 Rules (Best of 3):
   • Valid moves: rock, paper, scissors, bomb
   • Bomb can be used once per game and beats all other moves
   • Bomb vs Bomb = draw
   • Invalid input wastes the round (bot wins by default)
   • Game ends automatically after 3 rounds

Let's begin! What's your move for Round 1?
""".strip()
    
    def generate_bot_move(self) -> str:
        """
        Generate bot's move respecting bomb constraint.
        
        The bot checks game_state.bomb_used but does NOT mutate it.
        Random strategy is acceptable per specification.
        
        Returns:
            str: Bot's chosen move
        """
        # Available moves for bot
        available_moves = list(VALID_MOVES)
        
        # Remove bomb if already used
        if self.game_state.bomb_used["bot"]:
            available_moves.remove("bomb")
        
        # Random selection (simple strategy is acceptable)
        return random.choice(available_moves)
    
    def process_turn(self, user_input: str) -> str:
        """
        Process a single turn using the three mandatory tools.
        
        Flow (CRITICAL - agent must invoke all tools):
            1. validate_move (validation)
            2. generate bot move
            3. resolve_round (logic)
            4. update_game_state (mutation)
            5. generate response
        
        Args:
            user_input: Raw user input string
            
        Returns:
            str: Natural language response with round results
        """
        if not self.game_started:
            return "Game not started. Please start a new game first."
        
        # Guard against playing after game over
        if self.game_state.game_over:
            return "🚫 The game is already over. Please start a new game."
        
        current_round = self.game_state.round
        
        # TOOL 1: Validate user input (safe handling)
        validation_result = validate_move(user_input, self.game_state)
        
        # Safe extraction of user move
        if not validation_result["valid"]:
            user_move = None
        else:
            user_move = validation_result["normalized_move"]
        
        # Generate bot move (respects state but doesn't mutate)
        bot_move = self.generate_bot_move()
        
        # TOOL 2: Resolve round (pure logic for valid moves only)
        # Explicit branching for invalid input (maintains pure logic separation)
        if user_move is None:
            # Invalid input: agent produces deterministic result directly
            round_result = {
                "winner": "bot",
                "reason": "Invalid input - bot wins by default"
            }
        else:
            # Valid moves: use pure game logic tool
            round_result = resolve_round(user_move, bot_move)
        
        # TOOL 3: Update game state (ONLY mutation point)
        self.game_state = update_game_state(
            self.game_state,
            user_move,
            bot_move,
            round_result
        )
        
        # Generate natural language response
        response = self._format_round_response(
            current_round,
            user_move,
            bot_move,
            round_result,
            validation_result
        )
        
        return response
    
    def _format_round_response(
        self,
        round_num: int,
        user_move: Optional[str],
        bot_move: str,
        round_result: Dict,
        validation_result: Dict
    ) -> str:
        """
        Format the round result as a natural language response.
        
        Args:
            round_num: Round number that just completed
            user_move: User's move (None if invalid)
            bot_move: Bot's move
            round_result: Result from resolve_round
            validation_result: Result from validate_move
            
        Returns:
            str: Formatted response
        """
        lines = [f"\n🎯 Round {round_num} Results:"]
        
        # Show validation error if any
        if not validation_result["valid"]:
            lines.append(f"   ⚠️  {validation_result['error']}")
            lines.append(f"   You: INVALID INPUT")
        else:
            lines.append(f"   You: {user_move} {'💣' if user_move == 'bomb' else ''}")
        
        lines.append(f"   Bot: {bot_move} {'💣' if bot_move == 'bomb' else ''}")
        lines.append(f"   Result: {round_result['reason']}")
        
        # Show winner
        if round_result["winner"] == "user":
            lines.append("   🏆 You win this round!")
        elif round_result["winner"] == "bot":
            lines.append("   🤖 Bot wins this round!")
        else:
            lines.append("   🤝 Draw!")
        
        # Show current score
        lines.append(f"\n📊 Score: You {self.game_state.score['user']} - {self.game_state.score['bot']} Bot")
        
        # Check if game is over
        if self.game_state.game_over:
            lines.append(self._format_final_result())
        else:
            # Prompt for next round
            lines.append(f"\nWhat's your move for Round {self.game_state.round}?")
        
        return "\n".join(lines)
    
    def _format_final_result(self) -> str:
        """
        Format the final game result.
        
        Returns:
            str: Final result message
        """
        user_score = self.game_state.score["user"]
        bot_score = self.game_state.score["bot"]
        
        result_lines = [
            "\n" + "="*50,
            "🎮 GAME OVER - Final Results",
            "="*50,
            f"Final Score: You {user_score} - {bot_score} Bot"
        ]
        
        if user_score > bot_score:
            result_lines.append("\n🎉 YOU WIN THE GAME! 🎉")
        elif bot_score > user_score:
            result_lines.append("\n🤖 BOT WINS THE GAME! 🤖")
        else:
            result_lines.append("\n🤝 IT'S A DRAW! 🤝")
        
        result_lines.append("\nThanks for playing!")
        
        return "\n".join(result_lines)
    
    def get_game_state(self) -> GameState:
        """
        Get current game state (for debugging/testing).
        
        Returns:
            GameState: Current state
        """
        return self.game_state
