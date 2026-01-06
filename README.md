# 🎮 Rock-Paper-Scissors-Plus Game Referee

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4.svg)](https://github.com/google/adk)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A Google ADK-based game referee chatbot demonstrating tool-based architecture, persistent state management, and production-grade design patterns.

---

## 📖 Overview

This project implements a **Best-of-3 Rock-Paper-Scissors-Plus game** with an added "bomb" move, showcasing professional agent-based architecture using Google ADK principles. The focus is on **clean separation of concerns**, **testable code**, and **rule enforcement through tools** rather than prompts.

### ✨ Key Features

- ✅ **Tool-Based Architecture** - Three specialized tools (validate, resolve, update)
- ✅ **Persistent State Management** - Game state tracked across all turns
- ✅ **Bomb Constraint Enforcement** - One-time use strictly enforced via state
- ✅ **Production-Grade Safety** - Defensive programming, error handling, guards
- ✅ **Comprehensive Testing** - Full test suite with edge case coverage
- ✅ **Clear Documentation** - Architecture explanations and design rationales

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rock-paper-scissors-plus-referee.git
cd rock-paper-scissors-plus-referee

# Install dependencies (optional - pure Python project)
pip install -r requirements.txt
```

### Run the Game

```bash
python main.py
```

### Run Tests

```bash
python test_game.py
```

---

## 📋 Game Rules

- **3 rounds total** - Game ends automatically after round 3
- **Valid moves**: `rock`, `paper`, `scissors`, `bomb`
- **Bomb special rule**: Each player can use bomb **only ONCE** per game
  - Bomb beats all other moves
  - Bomb vs Bomb = draw
- **Invalid input**: Consumes the round; bot wins by default (deterministic scoring)
  - **Design rationale**: Invalid input intentionally consumes the round and awards the point to the bot to ensure deterministic scoring and strict rule enforcement. This prevents ambiguity and maintains game integrity.

**Interface Choice**: A CLI interface is used to keep focus on agent architecture rather than UI complexity.

---

## 🏗️ Architecture

### Google ADK Implementation

**This project uses Google ADK-style agents and tools**, with explicit tool functions (`validate_move`, `resolve_round`, `update_game_state`) acting as ADK tools and an agent orchestrating tool calls and state transitions.

### State Model

The game uses a persistent `GameState` dataclass with the following fields:

| Field | Type | Purpose |
|-------|------|---------|
| `round` | int | Current round number (1-3) |
| `max_rounds` | int | Fixed at 3 (no magic numbers) |
| `score` | Dict[str, int] | Tracks wins for user and bot |
| `bomb_used` | Dict[str, bool] | **Critical** - Enforces one-time bomb use |
| `history` | List[Dict] | All round results for explainability |
| `game_over` | bool | Set to True after round 3 |

**Why bomb tracking matters**: The bomb is a powerful one-time move. Tracking usage in persistent state ensures the constraint is enforced across all turns, even if the conversation context is lost.

**Design Decision - Immutability**: State updates return a new `GameState` instance to simplify debugging and testing, though in-place mutation is also valid in ADK.

### Agent & Tool Design

The architecture follows **strict separation of concerns** with three mandatory tools:

#### 1. `validate_move` (Input Validation)
- **Responsibility**: Validate and normalize user input
- **Does NOT**: Mutate state
- **Returns**: `{valid: bool, normalized_move: str, error: str}`
- **Why separate**: Validation logic is isolated and testable. Invalid inputs are caught early before game logic runs.

#### 2. `resolve_round` (Pure Game Logic)
- **Responsibility**: Determine round winner based on valid moves only
- **Does NOT**: Mutate state, access external data, handle invalid input
- **Returns**: `{winner: str, reason: str}`
- **Why separate**: Game rules are deterministic and side-effect free. Invalid input is handled by agent orchestration before calling this tool, maintaining pure logic separation.

#### 3. `update_game_state` (State Mutation)
- **Responsibility**: Apply round results to game state
- **ONLY place**: Where state is modified
- **Returns**: Updated `GameState`
- **Why separate**: Centralizing all mutations in one place makes state changes predictable and debuggable. The LLM never directly modifies state.

**Tool invocation is mandatory**: The agent must actually call all three tools on every turn, not just define them. This demonstrates proper ADK tool usage.

**Why tools are deterministic and side-effect controlled**: Each tool has a single, well-defined responsibility with no hidden dependencies. This makes the system predictable, testable, and easy to extend. Tools can be verified independently without running the full agent.

### Flow Diagram

```
User Input
   ↓
validate_move (Tool 1) → Validation only
   ↓
Bot Move Generation → Respects state.bomb_used
   ↓
Agent Decision → If invalid: deterministic result; If valid: call resolve_round
   ↓
resolve_round (Tool 2) → Pure logic (valid moves only)
   ↓
update_game_state (Tool 3) → ONLY mutation point
   ↓
Natural Language Response → Agent formats output
```

---

## 🔄 Tradeoffs

### Random Bot Strategy
The bot selects moves randomly from available options (respecting bomb constraint). This is simple but acceptable per specification.

**Tradeoff**: Bot is not strategic or adaptive. A smarter bot could analyze user patterns or use game theory.

### CLI Interface
The game uses a simple command-line interface with text input/output.

**Tradeoff**: No graphical UI, no persistent storage across sessions. This keeps the project focused on agent architecture rather than UI polish.

### Single Agent Design
One agent handles all orchestration (validation, logic, mutation via tools).

**Tradeoff**: Could be split into multiple specialized agents (e.g., referee agent + strategy agent), but this adds complexity without clear benefit for a 3-round game.

---

## 🚀 Potential Improvements

### 1. Smarter Bot AI
- Implement pattern recognition to detect user tendencies
- Use game theory (e.g., Nash equilibrium strategies)
- Add difficulty levels (easy/medium/hard)

### 2. Replay Functionality
- Allow users to play multiple games in one session
- Track win/loss statistics across games
- Implement a leaderboard

### 3. Multi-Agent Design
- **Referee Agent**: Enforces rules and tracks state
- **Strategy Agent**: Generates bot moves using advanced AI
- **Narrator Agent**: Provides commentary and explanations
- Agents communicate via shared state or message passing

### 4. Enhanced State Persistence
- Save game state to disk (JSON/SQLite)
- Resume interrupted games
- Replay game history with visualization

### 5. Web Interface
- Build a simple web UI using Flask/FastAPI
- Real-time updates with WebSockets
- Visual representation of moves and scores

---

## 📦 Project Structure

```
.
├── state.py          # Game state model and initialization
├── tools.py          # Three mandatory tools (validate, resolve, update)
├── agent.py          # Main agent orchestration logic
├── main.py           # CLI entry point
├── test_game.py      # Comprehensive test suite
├── README.md         # This file
└── requirements.txt  # Python dependencies
```

---

## 🧪 Testing

The architecture makes testing straightforward:

- **Unit test tools**: Each tool is pure/deterministic and can be tested independently
- **Integration test agent**: Verify tool invocation and state persistence
- **End-to-end test**: Run complete games with various scenarios

**Run tests**:
```bash
python test_game.py
```

**Expected output**:
```
🎉 ALL TESTS PASSED! 🎉
✅ The game is ready to play!
✅ All tools work correctly
✅ State persistence verified
✅ Bomb enforcement working
✅ Invalid input handling correct
✅ 3-round limit enforced
```

---

## 📝 Design Philosophy

This project demonstrates **clean separation of concerns** in agent-based systems:

1. **State is data** - stored in a well-defined structure
2. **Tools are functions** - pure, testable, single-responsibility
3. **Agent is orchestration** - coordinates tools but doesn't do their work
4. **LLM is interface** - generates natural language, not business logic

This architecture is **scalable**, **maintainable**, and **testable** - key qualities for production agent systems.

---

## 📚 Documentation

- **[DETAILED_EXPLANATION.md](DETAILED_EXPLANATION.md)** - Complete project explanation with interview preparation
- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Detailed running instructions and demo script
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Test verification results

---

## 🎯 Learning Outcomes

This project demonstrates:

- ✅ Tool-based agent architecture (Google ADK)
- ✅ Separation of concerns (validation, logic, mutation)
- ✅ Persistent state management
- ✅ Rule enforcement through code (not prompts)
- ✅ Production-grade safety features
- ✅ Comprehensive testing practices
- ✅ Clean, maintainable code structure

---

## 📞 Contact & Support

For questions or issues, please open an issue on GitHub.

---

## 📄 License

This project is available for educational and demonstration purposes.

---

<div align="center">

**Built with ❤️ using Google ADK principles**

[⭐ Star this repo](https://github.com/YOUR_USERNAME/rock-paper-scissors-plus-referee) if you found it helpful!

</div>