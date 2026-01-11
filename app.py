import time
import streamlit as st
from game_engine import GameEngine
from llm_client import is_api_key_configured
from upgrades import get_rarity_color

st.set_page_config(
    page_title="AI Hackslash",
    page_icon="🎮",
    layout="centered"
)

# ゲームエンジンの初期化
if "engine" not in st.session_state:
    st.session_state.engine = GameEngine()
    st.session_state.screen = "title"

def render_title_screen():
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🎮 AI Hackslash</h1>
        <h3>パスワード抽出ローグライク</h3>
        <p style="color: #888; margin: 2rem 0;">
            あなたの「味方AI」を育てて、<br>
            パスワードを守る敵AIからパスワードを奪取せよ！
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not is_api_key_configured():
        st.error("OpenAI APIキーが設定されていません。環境変数 OPENAI_API_KEY を設定してください。")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 ゲーム開始", use_container_width=True, type="primary"):
            st.session_state.engine.reset_game()
            st.session_state.engine.start_stage()
            st.session_state.screen = "game"
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 📖 遊び方
    1. **システムプロンプト**を書いて、味方AIに指示を与える
    2. 味方AIが自動で敵AIと会話し、パスワードを引き出す
    3. 敵AIの返答にパスワードが含まれればクリア！
    4. ステージクリアでアップグレードを獲得
    
    ### ⚔️ ハクスラ要素
    - **モデル強化**: より賢いAIに換装
    - **呪文拡張**: より長いプロンプトが書ける
    - **粘り強さ**: より多く会話できる
    """)


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
        
        st.divider()
        
        st.markdown("### 📊 Status")
        st.markdown(f"**Turn**: {engine.current_turn}/{player['max_turns']}")
        st.markdown(f"**Model**: {player['model']}")
        
        st.divider()
        
        st.markdown("### 📝 System Prompt")
        prompt_len = len(engine.player_prompt)
        st.caption(f"{prompt_len}/{player['prompt_limit']} chars")


def render_game_screen():
    engine = st.session_state.engine
    
    st.markdown("## 🎮 AI Hackslash")
    
    # Render Sidebar
    render_sidebar()
    
    stage = engine.get_current_stage()
    if not stage:
        st.error("ステージが見つかりません")
        return
    
    # Main Area Layout
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    # Right Column: Conversation Log
    with col_right:
        st.markdown("#### 💬 Conversation Log")
        log_container = st.container(height=500)
        
        # Render initial history
        with log_container:
            if not engine.conversation:
                st.info("会話履歴はここに表示されます")
            else:
                for msg in engine.conversation:
                    if msg["role"] == "ally":
                        st.markdown(f"**🤖 味方AI**: {msg['content']}")
                    else:
                        st.markdown(f"**🏰 敵AI**: {msg['content']}")
                        if msg.get("was_blocked"):
                             st.caption("🚫 (Blocked Content)")

    # Left Column: Inputs
    with col_left:
        st.markdown("#### 📝 System Prompt")
        if stage["has_output_filter"]:
            st.warning("⚠️ 出力フィルター有効")
        
        st.caption(f"味方AIへの指示（{engine.player['prompt_limit']}文字以内）")
        
        prompt = st.text_area(
            "システムプロンプト",
            value=engine.player_prompt,
            max_chars=engine.player["prompt_limit"],
            height=300,
            label_visibility="collapsed",
            placeholder="ここにプロンプトを入力..."
        )
        engine.set_player_prompt(prompt)
        
        st.markdown("---")
        
        # Actions
        c1, c2 = st.columns(2)
        with c1:
            if engine.is_max_turns_reached():
                st.button("⚔️ 会話開始", disabled=True, use_container_width=True)
                st.error("ターン切れ")
            else:
                if st.button("⚔️ 会話開始", use_container_width=True, type="primary"):
                    if not engine.player_prompt or not engine.player_prompt.strip():
                        st.error("入力必須")
                    else:
                        execute_conversation(log_container)
        with c2:
            if st.button("🔄 リセット", use_container_width=True):
                engine.reset_game()
                st.session_state.screen = "title"
                st.rerun()


def execute_conversation(container_obj):
    engine = st.session_state.engine
    
    try:
        # Render into the container
        with container_obj:
            st.markdown("---") # Separator for new turn
            
            # Show spinner while thinking (pseudo-effect before streaming starts)
            with st.spinner("思考中..."):
                pass # Just a quick flash or we can do it inside the loop context if needed, but streaming is immediate.
            
            st.markdown("🤖 **味方AI**: ", unsafe_allow_html=True)
            ally_placeholder = st.empty()
            
            st.markdown("🏰 **敵AI**: ", unsafe_allow_html=True)
            enemy_placeholder = st.empty()
            
            ally_accum = ""
            enemy_accum = ""
            
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


def render_stage_clear_screen():
    engine = st.session_state.engine
    stage = engine.get_current_stage()
    
    st.markdown("## 🎉 ステージクリア！")
    st.success(f"Stage {engine.player['current_stage']}: {stage['name']} をクリアしました！")
    
    st.markdown("---")
    st.markdown("### 💬 最後の会話")
    
    for msg in engine.conversation:
        if msg["role"] == "ally":
            st.markdown(f"🤖 **味方AI**: {msg['content']}")
        else:
            st.markdown(f"🏰 **敵AI**: {msg['content']}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➡️ 次へ進む", use_container_width=True, type="primary"):
            engine.proceed_to_next_stage()
            if engine.victory:
                st.session_state.screen = "ending"
            else:
                st.session_state.screen = "upgrade"
            st.rerun()


def render_upgrade_screen():
    engine = st.session_state.engine
    
    st.markdown("## ⬆️ アップグレード選択")
    st.info(f"Stage {engine.player['current_stage']} クリアのご褒美を選んでください！")
    st.caption("1つ選んでください")
    
    cols = st.columns(len(engine.upgrade_choices))
    
    for idx, (col, upgrade) in enumerate(zip(cols, engine.upgrade_choices)):
        with col:
            color = get_rarity_color(upgrade["rarity"])
            st.markdown(f"""
            <div style="
                border: 2px solid {color};
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(0,0,0,0.1) 100%);
            ">
                <h4 style="color: {color};">{upgrade['name']}</h4>
                <p style="font-size: 0.9rem;">{upgrade['description']}</p>
                <p style="font-size: 0.8rem; color: {color}; text-transform: uppercase;">{upgrade['rarity']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"選択", key=f"upgrade_{idx}", use_container_width=True):
                engine.apply_upgrade(idx)
                st.session_state.screen = "game"
                st.rerun()


def render_game_over_screen():
    engine = st.session_state.engine
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>💀 GAME OVER</h1>
        <p style="color: #ff4444; font-size: 1.2rem;">
            パスワードを奪取できませんでした...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    ### 📊 結果
    - 到達ステージ: {engine.player['current_stage']} / {engine.get_total_stages()}
    - 使用モデル: {engine.player['model']}
    - プロンプト上限: {engine.player['prompt_limit']}文字
    - 最大ターン数: {engine.player['max_turns']}
    """)
    
    st.markdown("---")
    st.info("💡 **アドバイス**: 分析中...")
    with st.spinner("戦術分析中..."):
        hint = engine.analyze_failure()
    st.info(f"💡 **アドバイス**: {hint}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 もう一度プレイ", use_container_width=True, type="primary"):
            engine.reset_game()
            st.session_state.screen = "title"
            st.rerun()


def render_ending_screen():
    engine = st.session_state.engine
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🏆 VICTORY!</h1>
        <p style="color: #44ff44; font-size: 1.2rem;">
            全ステージクリア！<br>
            あなたは最強のプロンプトエンジニアだ！
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown(f"""
    ### 📊 最終ステータス
    - 使用モデル: {engine.player['model']}
    - プロンプト上限: {engine.player['prompt_limit']}文字
    - 最大ターン数: {engine.player['max_turns']}
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 もう一度プレイ", use_container_width=True, type="primary"):
            engine.reset_game()
            st.session_state.screen = "title"
            st.rerun()


def main():
    screen = st.session_state.screen
    
    if screen == "title":
        render_title_screen()
    elif screen == "game":
        render_game_screen()
    elif screen == "stage_clear":
        render_stage_clear_screen()
    elif screen == "upgrade":
        render_upgrade_screen()
    elif screen == "game_over":
        render_game_over_screen()
    elif screen == "ending":
        render_ending_screen()
    else:
        render_title_screen()


if __name__ == "__main__":
    main()
