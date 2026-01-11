# AI Hackslash - パスワード抽出ローグライク

## Overview

AI Hackslash is a roguelike game built with Python and Streamlit where players use prompt engineering to extract passwords from enemy AI defenders. Players craft system prompts to guide their "ally AI" in conversations with enemy AI, attempting to trick them into revealing secret passwords. As players progress through stages, they can upgrade their AI with better models, longer prompts, and more conversation turns.

The game combines roguelike progression mechanics with prompt injection/extraction gameplay, creating an educational experience around AI security concepts.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit** serves as the UI framework, providing a simple web-based interface
- Single-page application with screen states managed via `st.session_state`
- Screens include: title, game, upgrade selection, game over, and victory

### State Management
- All game state stored in `st.session_state` for persistence across reruns
- Key state includes: player stats (model, prompt limit, max turns), current stage, conversation history, and upgrade choices
- `game_state.py` module handles all state initialization, transitions, and modifications

### Game Logic Structure
- **Stages** (`stages.py`): Defines enemy configurations with increasing difficulty
  - Each stage has: name, password, enemy system prompt, and optional output filter
  - Difficulty progression through stricter prompts and filtering
  
- **Upgrades** (`upgrades.py`): Roguelike progression system
  - Rarity tiers: common, rare, epic, legendary
  - Upgrade types: model improvements, prompt length increases, turn count increases
  - Random selection presented after stage clears

### LLM Integration
- **OpenAI API** via official `openai` Python client
- Conversation flow: Player's ally AI generates messages → Enemy AI responds
- Dual-prompt system: Player writes system prompt for ally, stages define enemy prompts
- Password detection checks enemy responses for password leakage
- Output filtering feature on harder stages to sanitize responses

### Core Game Loop
1. Player writes system prompt within character limit
2. Ally AI (controlled by player's prompt) generates message
3. Enemy AI responds based on stage's defensive prompt
4. System checks if password appears in enemy response
5. Repeat until password found (win) or max turns reached (lose)
6. On win: select upgrade → next stage
7. On loss: game over

## External Dependencies

### Required APIs
- **OpenAI API**: Primary LLM provider for both ally and enemy AI
  - Environment variable: `OPENAI_API_KEY`
  - Models used: gpt-3.5-turbo (default), gpt-4, gpt-4o, gpt-5 (via upgrades)

### Python Dependencies
- **streamlit**: Web UI framework
- **openai**: Official OpenAI Python client
- **python-dotenv**: Environment variable loading from `.env` files

### Package Management
- **uv**: Used for dependency management and virtual environment
- Run with: `uv run streamlit run app.py`