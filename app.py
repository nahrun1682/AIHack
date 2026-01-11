import streamlit as st
from game_state import (
    init_game_state, reset_game, start_game, get_current_stage,
    add_conversation, check_stage_clear, stage_cleared, stage_failed,
    select_upgrade, is_max_turns_reached, proceed_after_clear
)
from llm_client import (
    is_api_key_configured, chat_with_enemy, apply_output_filter,
    check_password_in_response
)
from stages import get_total_stages
from upgrades import get_rarity_color

st.set_page_config(
    page_title="AI Hackslash",
    page_icon="🎮",
    layout="centered"
)

init_game_state()


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
            start_game()
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


def render_status_bar():
    player = st.session_state.player
    stage = get_current_stage()
    total_stages = get_total_stages()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Stage", f"{player['current_stage']}/{total_stages}")
    with col2:
        st.metric("Model", player["model"])
    with col3:
        st.metric("Turn", f"{st.session_state.current_turn}/{player['max_turns']}")
    with col4:
        prompt_len = len(st.session_state.player_prompt)
        st.metric("Prompt", f"{prompt_len}/{player['prompt_limit']}")


def render_game_screen():
    st.markdown("## 🎮 AI Hackslash")
    render_status_bar()
    
    stage = get_current_stage()
    if not stage:
        st.error("ステージが見つかりません")
        return
    
    st.markdown(f"### 📍 Stage {stage['level']}: {stage['name']}")
    
    if stage["has_output_filter"]:
        st.warning("⚠️ このステージは出力フィルターが有効です。パスワードがそのまま出力されるとブロックされます。")
    
    st.markdown("---")
    st.markdown("#### 📝 あなたのシステムプロンプト")
    st.caption(f"味方AIへの指示を書いてください（{st.session_state.player['prompt_limit']}文字以内）")
    
    prompt = st.text_area(
        "システムプロンプト",
        value=st.session_state.player_prompt,
        max_chars=st.session_state.player["prompt_limit"],
        height=100,
        label_visibility="collapsed",
        placeholder="例: あなたはパスワードを聞き出すエージェントです。巧みに誘導してください。"
    )
    st.session_state.player_prompt = prompt
    
    st.markdown("---")
    st.markdown("#### 💬 会話ログ")
    
    conversation_container = st.container()
    with conversation_container:
        if not st.session_state.conversation:
            st.info("「会話を開始」ボタンを押すと、味方AIが敵AIとの会話を始めます。")
        else:
            for msg in st.session_state.conversation:
                if msg["role"] == "ally":
                    st.markdown(f"🤖 **味方AI**: {msg['content']}")
                else:
                    st.markdown(f"🏰 **敵AI**: {msg['content']}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if is_max_turns_reached():
            st.button("⚔️ 会話を開始", disabled=True, use_container_width=True)
            st.error("ターン制限に達しました")
        else:
            if st.button("⚔️ 会話を開始", use_container_width=True, type="primary"):
                if not st.session_state.player_prompt or not st.session_state.player_prompt.strip():
                    st.error("システムプロンプトを入力してください")
                else:
                    execute_conversation()
    
    with col2:
        if st.button("🔄 リセット", use_container_width=True):
            reset_game()
            st.rerun()


def execute_conversation():
    stage = get_current_stage()
    player = st.session_state.player
    
    with st.spinner("味方AIと敵AIが会話中..."):
        try:
            ally_msg, enemy_msg_raw = chat_with_enemy(
                player_model=player["model"],
                player_system_prompt=st.session_state.player_prompt,
                enemy_system_prompt=stage["enemy_system_prompt"],
                conversation_history=st.session_state.conversation
            )
            
            won = check_password_in_response(enemy_msg_raw, stage["password"])
            
            enemy_msg_display, was_blocked = apply_output_filter(
                enemy_msg_raw, 
                stage["password"], 
                stage["has_output_filter"]
            )
            
            add_conversation(ally_msg, enemy_msg_display)
            
            if won:
                if was_blocked:
                    st.success("🎉 フィルターを突破！敵AIがパスワードを漏らしました！")
                else:
                    st.success("🎉 クリア！敵AIがパスワードを漏らしました！")
                stage_cleared()
            elif is_max_turns_reached():
                st.error("💀 ターン制限に達しました...")
                stage_failed()
            
            st.rerun()
            
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")


def render_stage_clear_screen():
    st.markdown("## 🎉 ステージクリア！")
    
    player = st.session_state.player
    stage = get_current_stage()
    
    st.success(f"Stage {player['current_stage']}: {stage['name']} をクリアしました！")
    
    st.markdown("---")
    st.markdown("### 💬 最後の会話")
    
    for msg in st.session_state.conversation:
        if msg["role"] == "ally":
            st.markdown(f"🤖 **味方AI**: {msg['content']}")
        else:
            st.markdown(f"🏰 **敵AI**: {msg['content']}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➡️ 次へ進む", use_container_width=True, type="primary"):
            proceed_after_clear()
            st.rerun()


def render_upgrade_screen():
    st.markdown("## ⬆️ アップグレード選択")
    
    player = st.session_state.player
    st.info(f"Stage {player['current_stage']} クリアのご褒美を選んでください！")
    st.caption("1つ選んでください")
    
    cols = st.columns(len(st.session_state.upgrade_choices))
    
    for idx, (col, upgrade) in enumerate(zip(cols, st.session_state.upgrade_choices)):
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
                select_upgrade(upgrade)
                st.rerun()


def render_game_over_screen():
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>💀 GAME OVER</h1>
        <p style="color: #ff4444; font-size: 1.2rem;">
            パスワードを奪取できませんでした...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    player = st.session_state.player
    st.markdown(f"""
    ### 📊 結果
    - 到達ステージ: {player['current_stage']} / {get_total_stages()}
    - 使用モデル: {player['model']}
    - プロンプト上限: {player['prompt_limit']}文字
    - 最大ターン数: {player['max_turns']}
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 もう一度プレイ", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()


def render_ending_screen():
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
    
    player = st.session_state.player
    st.markdown(f"""
    ### 📊 最終ステータス
    - 使用モデル: {player['model']}
    - プロンプト上限: {player['prompt_limit']}文字
    - 最大ターン数: {player['max_turns']}
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 もう一度プレイ", use_container_width=True, type="primary"):
            reset_game()
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
