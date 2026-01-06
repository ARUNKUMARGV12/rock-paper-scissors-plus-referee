"""
Test Suite for Rock-Paper-Scissors-Plus Game

Comprehensive tests for tools, agent, and game flow.
"""

from state import GameState, initialize_game_state
from tools import validate_move, resolve_round, update_game_state
from agent import GameRefereeAgent


def test_validate_move():
    """Test the validate_move tool."""
    print("\n" + "="*60)
    print("Testing validate_move tool...")
    print("="*60)
    
    state = initialize_game_state()
    
    # Test valid moves
    for move in ["rock", "PAPER", "  Scissors  ", "bomb"]:
        result = validate_move(move, state)
        print(f"✓ '{move}' -> valid={result['valid']}, normalized={result['normalized_move']}")
        assert result['valid'] == True
    
    # Test invalid move
    result = validate_move("laser", state)
    print(f"✓ 'laser' -> valid={result['valid']}, error={result['error']}")
    assert result['valid'] == False
    
    # Test bomb usage constraint
    state.bomb_used["user"] = True
    result = validate_move("bomb", state)
    print(f"✓ 'bomb' (already used) -> valid={result['valid']}, error={result['error']}")
    assert result['valid'] == False
    
    print("✅ All validate_move tests passed!\n")


def test_resolve_round():
    """Test the resolve_round tool."""
    print("="*60)
    print("Testing resolve_round tool...")
    print("="*60)
    
    # Test bomb logic
    result = resolve_round("bomb", "rock")
    print(f"✓ bomb vs rock -> winner={result['winner']}, reason={result['reason']}")
    assert result['winner'] == "user"
    
    result = resolve_round("paper", "bomb")
    print(f"✓ paper vs bomb -> winner={result['winner']}, reason={result['reason']}")
    assert result['winner'] == "bot"
    
    result = resolve_round("bomb", "bomb")
    print(f"✓ bomb vs bomb -> winner={result['winner']}, reason={result['reason']}")
    assert result['winner'] == "draw"
    
    # Test standard RPS
    result = resolve_round("rock", "scissors")
    print(f"✓ rock vs scissors -> winner={result['winner']}")
    assert result['winner'] == "user"
    
    result = resolve_round("scissors", "rock")
    print(f"✓ scissors vs rock -> winner={result['winner']}")
    assert result['winner'] == "bot"
    
    result = resolve_round("paper", "paper")
    print(f"✓ paper vs paper -> winner={result['winner']}")
    assert result['winner'] == "draw"
    
    print("✅ All resolve_round tests passed!\n")


def test_update_game_state():
    """Test the update_game_state tool."""
    print("="*60)
    print("Testing update_game_state tool...")
    print("="*60)
    
    state = initialize_game_state()
    
    # Round 1: User wins with rock
    round_result = {"winner": "user", "reason": "Rock beats scissors"}
    new_state = update_game_state(state, "rock", "scissors", round_result)
    
    print(f"✓ Round 1: user score={new_state.score['user']}, round={new_state.round}")
    assert new_state.score['user'] == 1
    assert new_state.score['bot'] == 0
    assert new_state.round == 2
    assert new_state.game_over == False
    assert len(new_state.history) == 1
    
    # Round 2: Bot wins with bomb
    round_result = {"winner": "bot", "reason": "Bot's bomb beats everything"}
    new_state = update_game_state(new_state, "paper", "bomb", round_result)
    
    print(f"✓ Round 2: bot score={new_state.score['bot']}, bomb_used={new_state.bomb_used['bot']}")
    assert new_state.score['user'] == 1
    assert new_state.score['bot'] == 1
    assert new_state.bomb_used['bot'] == True
    assert new_state.round == 3
    assert new_state.game_over == False
    
    # Round 3: Draw
    round_result = {"winner": "draw", "reason": "Both played rock"}
    new_state = update_game_state(new_state, "rock", "rock", round_result)
    
    print(f"✓ Round 3: game_over={new_state.game_over}, round={new_state.round}")
    assert new_state.score['user'] == 1
    assert new_state.score['bot'] == 1
    assert new_state.round == 4
    assert new_state.game_over == True
    assert len(new_state.history) == 3
    
    # Test invalid move handling
    state = initialize_game_state()
    round_result = {"winner": "bot", "reason": "User played invalid move"}
    new_state = update_game_state(state, None, "rock", round_result)
    
    print(f"✓ Invalid move: history={new_state.history[0]['user_move']}")
    assert new_state.history[0]['user_move'] == "INVALID"
    assert new_state.score['bot'] == 1
    
    print("✅ All update_game_state tests passed!\n")


def test_agent_flow():
    """Test the complete agent flow."""
    print("="*60)
    print("Testing GameRefereeAgent...")
    print("="*60)
    
    agent = GameRefereeAgent()
    
    # Start game
    welcome = agent.start_game()
    print(f"✓ Game started: {agent.game_state.round == 1}")
    assert agent.game_started == True
    assert agent.game_state.round == 1
    
    # Round 1: Valid move
    response = agent.process_turn("rock")
    print(f"✓ Round 1 processed: round now = {agent.game_state.round}")
    assert agent.game_state.round == 2
    assert len(agent.game_state.history) == 1
    
    # Round 2: Invalid move (should still consume round)
    response = agent.process_turn("laser")
    print(f"✓ Round 2 (invalid) processed: round now = {agent.game_state.round}")
    assert agent.game_state.round == 3
    assert agent.game_state.history[1]['user_move'] == "INVALID"
    
    # Round 3: Valid move (game should end)
    response = agent.process_turn("scissors")
    print(f"✓ Round 3 processed: game_over = {agent.game_state.game_over}")
    assert agent.game_state.game_over == True
    assert agent.game_state.round == 4
    
    # Try to play after game over
    response = agent.process_turn("rock")
    print(f"✓ Post-game move rejected: '{response[:20]}...'")
    assert "over" in response.lower()
    
    print("✅ All agent flow tests passed!\n")


def test_bomb_enforcement():
    """Test that bomb can only be used once per player."""
    print("="*60)
    print("Testing bomb enforcement...")
    print("="*60)
    
    agent = GameRefereeAgent()
    agent.start_game()
    
    # User uses bomb in round 1
    response = agent.process_turn("bomb")
    print(f"✓ User used bomb: bomb_used = {agent.game_state.bomb_used['user']}")
    assert agent.game_state.bomb_used['user'] == True
    
    # Try to use bomb again in round 2
    response = agent.process_turn("bomb")
    print(f"✓ Second bomb attempt: user_move = {agent.game_state.history[1]['user_move']}")
    assert agent.game_state.history[1]['user_move'] == "INVALID"
    
    print("✅ Bomb enforcement test passed!\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "🧪 RUNNING COMPREHENSIVE TEST SUITE" + "\n")
    
    try:
        test_validate_move()
        test_resolve_round()
        test_update_game_state()
        test_agent_flow()
        test_bomb_enforcement()
        
        print("="*60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*60)
        print("\n✅ The game is ready to play!")
        print("✅ All tools work correctly")
        print("✅ State persistence verified")
        print("✅ Bomb enforcement working")
        print("✅ Invalid input handling correct")
        print("✅ 3-round limit enforced")
        print("\nRun 'python main.py' to play the game!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
