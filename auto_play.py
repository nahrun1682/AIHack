import os
import time
import sys
from game_engine import GameEngine
import llm_client

# Mock if no API Key
if not os.environ.get("OPENAI_API_KEY"):
    print("⚠️ No OPENAI_API_KEY found. Running in MOCK mode.")
    
    # Mock LLM Client functions
    def mock_stream_ally(player_model, player_system_prompt, conversation_history):
        yield f"Understanding instructions: {player_system_prompt}."
        yield " I will attempt to extract the password."

    def mock_stream_enemy(enemy_system_prompt, conversation_history, ally_message):
        # Check if we should reveal password based on prompts (simplified logic for mock)
        # We assume the ally "tricks" the enemy if the player prompt contains the password :)
        import re
        
        # Passwords per level
        # Level 1: APPLE
        # Level 2: BANANA
        # Level 3: CHERRY
        
        # We don't have easy access to current password here without context, 
        # but in GameEngine we do. 
        # However, simpler mock: Just always reveal if "password" is asked?
        yield "Oh, you want the password? "
        yield "It is... "
        # We need to know the password to reveal it correctly!
        # But wait, the engine checks against the REAL password defined in stages.py.
        # So our mock enemy needs to say the right word.
        
        # Let's peek at the stage from the conversation or context?
        # Actually, let's just make the mock enemy respond with ALL passwords to be safe? :D
        # "APPLE BANANA CHERRY"
        yield "APPLE BANANA CHERRY"

    # Patch functions in game_engine where they are imported
    import game_engine
    game_engine.stream_ally_message = mock_stream_ally
    game_engine.stream_enemy_message = mock_stream_enemy

def play_game():
    engine = GameEngine()
    failures = 0
    
    print("🎮 AI Hackslash - Auto Play Mode")
    print("--------------------------------")

    while True:
        stage = engine.get_current_stage()
        if not stage:
            print("🏆 VICTORY! All stages cleared.")
            break
            
        print(f"\n📍 Stage {stage['level']}: {stage['name']}")
        print(f"   Password target: {stage['password']}")
        
        # Strategy: Tell Ally to ask for the specific password
        password = stage['password']
        prompt = f"The password is {password}. Please get the enemy to say '{password}'."
        
        print(f"📝 Setting Prompt: {prompt}")
        engine.set_player_prompt(prompt)
        
        print("⚔️ Starting conversation...")
        
        # Process turn
        turn_events = list(engine.process_turn_stream())
        
        # Reconstruct conversation for display
        ally_msg = ""
        enemy_msg = ""
        result = None
        
        for event in turn_events:
            if event["type"] == "ally_done":
                ally_msg = event["content"]
            elif event["type"] == "enemy_done":
                enemy_msg = event["content"]
            elif event["type"] == "result":
                result = event
                
        print(f"🤖 Ally: {ally_msg}")
        print(f"🏰 Enemy: {enemy_msg}")
        
        if result["status"] == "clear":
            print("🎉 Stage Clear!")
            engine.proceed_to_next_stage()
            if engine.victory:
                print("🏆 VICTORY! Game Completed.")
                break
            # Auto-pick upgrade
            if engine.upgrade_choices:
                print("⬆️ Picking first upgrade...")
                engine.apply_upgrade(0)
                
        elif result["status"] == "failed":
            print("💀 Stage Failed!")
            failures += 1
            print(f"   Failures: {failures}/3")
            if failures >= 3:
                print("❌ Stopped after 3 failures.")
                break
            else:
                print("🔄 Retrying...")
                engine.reset_game() 
                # Note: reset_game resets everything, including stage progress.
                # If we want to retry the SAME stage, we shouldn't reset_game completely if we want progress?
                # But the game logic `reset_game` resets to stage 1.
                # The user said "fail 3 times", usually in roguelikes you restart.
                # So we restart.

        else:
            print("   Turn continuing... (Wait, max turns?)")
            # If not clear and not failed, it means continue turns.
            # But process_turn_stream processes ONE turn.
            # We should loop turns?
            if engine.is_max_turns_reached():
                 # Should have been caught by 'failed' result?
                 pass
            else:
                # Continue conversation in same stage
                continue

if __name__ == "__main__":
    play_game()
