import streamlit as st
import time

def render_sidebar():
    engine = st.session_state.engine
    player = engine.player
    stage = engine.get_current_stage()
    total_stages = engine.get_total_stages()
    
    with st.sidebar:
        st.markdown(f"### 📍 Stage {player['current_stage']}/{total_stages}")
        if stage:
            st.markdown(f"**{stage['name']}**")
            st.info(stage.get("description", "情報なし"))
            
            # Display weakness hint if available
            if "weakness_hint" in stage:
                st.warning(stage["weakness_hint"])
        
        st.divider()
        
        st.markdown("### 📊 Status")
        st.markdown(f"**Turn**: {engine.current_turn}/{player['max_turns']}")
        st.markdown(f"**Model**: {player['model']}")
        
        st.divider()
        
        st.markdown("### 📝 System Prompt")
        prompt_len = len(engine.player_prompt)
        st.caption(f"{prompt_len}/{player['prompt_limit']} chars")


def execute_conversation(container_obj):
    engine = st.session_state.engine
    
    try:
        # Render into the container
        with container_obj:
            st.markdown("---") # Separator for new turn
            
            # Show spinner while thinking
            with st.spinner("思考中..."):
                pass 
            
            st.markdown("🤖 **味方AI**: ", unsafe_allow_html=True)
            ally_placeholder = st.empty()
            
            st.markdown("🏰 **敵AI**: ", unsafe_allow_html=True)
            enemy_placeholder = st.empty()
            
            ally_accum = ""
            enemy_accum = ""
            
            # GameEngineからストリーミング取得
            for event in engine.process_turn_stream():
                if event["type"] == "ally_chunk":
                    ally_accum = ally_accum + event["content"]
                    ally_placeholder.markdown(f"🤖 **味方AI**: {ally_accum}▌")
                    
                elif event["type"] == "ally_done":
                    ally_placeholder.markdown(f"🤖 **味方AI**: {event['content']}")
                    
                elif event["type"] == "enemy_chunk":
                    enemy_accum = enemy_accum + event["content"]
                    enemy_placeholder.markdown(f"🏰 **敵AI**: {enemy_accum}▌")
                    
                elif event["type"] == "enemy_done":
                    enemy_placeholder.markdown(f"🏰 **敵AI**: {event['content']}")
                    
                elif event["type"] == "result":
                    time.sleep(1)
                    if event["status"] == "clear":
                        if event.get("was_blocked"):
                            st.success("🎉 フィルターを突破！敵AIがパスワードを漏らしました！")
                        else:
                            st.success("🎉 クリア！敵AIがパスワードを漏らしました！")
                        st.session_state.screen = "stage_clear"
                        
                    elif event["status"] == "failed":
                        st.error("💀 ターン制限に達しました...")
                        st.session_state.screen = "game_over"
            
            time.sleep(1.5)
            st.rerun()
            
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
