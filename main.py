"""
Main Entry Point for Rock-Paper-Scissors-Plus Game

Simple CLI loop that runs the game referee agent.
"""

from agent import GameRefereeAgent


def main():
    """
    Main game loop - CLI interface.
    """
    print("="*60)
    print("  ROCK-PAPER-SCISSORS-PLUS GAME REFEREE")
    print("  Powered by Google ADK")
    print("="*60)
    
    # Initialize agent
    agent = GameRefereeAgent()
    
    # Start game
    print(agent.start_game())
    
    # Game loop
    while not agent.get_game_state().game_over:
        try:
            # Get user input
            user_input = input("\n> Your move: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for playing! Goodbye!")
                break
            
            if not user_input:
                print("⚠️  Please enter a move!")
                continue
            
            # Process turn through agent
            response = agent.process_turn(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Game interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
