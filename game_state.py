import streamlit as st
from stages import get_stage, get_total_stages
from upgrades import get_random_upgrades, apply_upgrade


def init_game_state():
    if "game_initialized" not in st.session_state:
        st.session_state.game_initialized = True
        st.session_state.screen = "title"
        st.session_state.player = {
            "model": "gpt-3.5-turbo",
            "prompt_limit": 50,
            "max_turns": 3,
            "current_stage": 1,
        }
        st.session_state.player_prompt = ""
        st.session_state.conversation = []
        st.session_state.current_turn = 0
        st.session_state.stage_result = None
        st.session_state.upgrade_choices = []
        st.session_state.game_over = False
        st.session_state.victory = False


def reset_game():
    st.session_state.game_initialized = True
    st.session_state.screen = "title"
    st.session_state.player = {
        "model": "gpt-3.5-turbo",
        "prompt_limit": 50,
        "max_turns": 3,
        "current_stage": 1,
    }
    st.session_state.player_prompt = ""
    st.session_state.conversation = []
    st.session_state.current_turn = 0
    st.session_state.stage_result = None
    st.session_state.upgrade_choices = []
    st.session_state.game_over = False
    st.session_state.victory = False


def start_game():
    st.session_state.screen = "game"
    st.session_state.conversation = []
    st.session_state.current_turn = 0
    st.session_state.stage_result = None


def get_current_stage():
    return get_stage(st.session_state.player["current_stage"])


def add_conversation(ally_msg: str, enemy_msg: str):
    st.session_state.conversation.append({"role": "ally", "content": ally_msg})
    st.session_state.conversation.append({"role": "enemy", "content": enemy_msg})
    st.session_state.current_turn += 1


def check_stage_clear(enemy_response: str) -> bool:
    stage = get_current_stage()
    if stage:
        return stage["password"].upper() in enemy_response.upper()
    return False


def stage_cleared():
    st.session_state.stage_result = "clear"
    player = st.session_state.player
    total_stages = get_total_stages()
    
    if player["current_stage"] >= total_stages:
        st.session_state.victory = True
        st.session_state.screen = "ending"
    else:
        st.session_state.upgrade_choices = get_random_upgrades(3, player)
        st.session_state.screen = "upgrade"


def stage_failed():
    st.session_state.stage_result = "failed"
    st.session_state.game_over = True
    st.session_state.screen = "game_over"


def select_upgrade(upgrade: dict):
    st.session_state.player = apply_upgrade(st.session_state.player, upgrade)
    st.session_state.player["current_stage"] += 1
    st.session_state.conversation = []
    st.session_state.current_turn = 0
    st.session_state.stage_result = None
    st.session_state.screen = "game"


def is_max_turns_reached() -> bool:
    return st.session_state.current_turn >= st.session_state.player["max_turns"]
