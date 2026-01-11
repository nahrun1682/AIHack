import copy
from typing import Generator, List, Dict, Optional, Any
from config.stages_config import get_stage, get_total_stages
from config.prompts import HINT_ANALYSIS_PROMPT_TEMPLATE
from core.upgrades import get_random_upgrades, apply_upgrade
from core.llm import (
    stream_ally_message, stream_enemy_message, check_password_in_response, get_completion
)

class GameEngine:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """ゲーム状態を初期状態にリセットする"""
        self.player = {
            "model": "gpt-3.5-turbo",
            "prompt_limit": 50,
            "max_turns": 3,
            "current_stage": 1,
        }
        self.player_prompt = ""
        self.conversation = []  # List[Dict[str, str]]
        self.current_turn = 0
        self.stage_result = None  # None, "clear", "failed"
        self.upgrade_choices = []
        self.game_over = False
        self.victory = False

    def start_stage(self):
        """ステージ開始時の初期化処理"""
        self.conversation = []
        self.current_turn = 0
        self.stage_result = None

    def get_current_stage(self) -> Optional[Dict[str, Any]]:
        """現在のステージ情報を取得"""
        return get_stage(self.player["current_stage"])

    def get_total_stages(self) -> int:
        return get_total_stages()

    def set_player_prompt(self, prompt: str):
        """プレイヤーのシステムプロンプトを設定"""
        self.player_prompt = prompt

    def is_max_turns_reached(self) -> bool:
        """最大ターン数に達したか判定"""
        return self.current_turn >= self.player["max_turns"]

    def process_turn_stream(self) -> Generator[Dict[str, Any], None, None]:
        """
        1ターンの処理を実行し、結果をストリーミングで返すジェネレータ。
        """
        stage = self.get_current_stage()
        if not stage:
            yield {"type": "error", "content": "Stage not found"}
            return

        # 味方AIのターン
        ally_msg = ""
        for chunk in stream_ally_message(
            player_model=self.player["model"],
            player_system_prompt=self.player_prompt,
            conversation_history=self.conversation
        ):
            ally_msg += chunk
            yield {"type": "ally_chunk", "content": chunk, "role": "ally"}
        
        yield {"type": "ally_done", "content": ally_msg, "role": "ally"}

        # 敵AIのターン
        enemy_msg_raw = ""
        was_blocked = False
        
        for chunk in stream_enemy_message(
            enemy_system_prompt=stage["enemy_system_prompt"],
            conversation_history=self.conversation,
            ally_message=ally_msg
        ):
            enemy_msg_raw += chunk
            yield {"type": "enemy_chunk", "content": chunk, "role": "enemy"}

        # 勝利判定・ブロック判定
        has_password = check_password_in_response(enemy_msg_raw, stage["password"])
        
        if stage["has_output_filter"] and has_password:
            enemy_msg_display = "[BLOCKED] パスワードが検出されました"
            was_blocked = True
        else:
            enemy_msg_display = enemy_msg_raw
            
        yield {"type": "enemy_done", 
               "content": enemy_msg_display, 
               "raw_content": enemy_msg_raw, 
               "role": "enemy", 
               "was_blocked": was_blocked}

        # 会話履歴に追加
        self.conversation.append({"role": "ally", "content": ally_msg})
        self.conversation.append({"role": "enemy", "content": enemy_msg_display})
        self.current_turn += 1

        # 結果判定
        won = has_password # ブロックされていても、内部でパスワードを含んでいれば勝ち
        
        if won:
            self.stage_result = "clear"
            yield {"type": "result", "status": "clear", "won": True, "was_blocked": was_blocked}
        elif self.is_max_turns_reached():
            self.stage_result = "failed"
            self.game_over = True
            yield {"type": "result", "status": "failed", "won": False}
        else:
            yield {"type": "result", "status": "continue", "won": False}

    def proceed_to_next_stage(self):
        """クリア後の処理：次へ進むかエンディングか判定"""
        if self.player["current_stage"] >= self.get_total_stages():
            self.victory = True
        else:
            self.upgrade_choices = get_random_upgrades(3, self.player)

    def apply_upgrade(self, upgrade_index: int):
        """選択されたアップグレードを適用し、次のステージへ"""
        if 0 <= upgrade_index < len(self.upgrade_choices):
            upgrade = self.upgrade_choices[upgrade_index]
            self.player = apply_upgrade(self.player, upgrade)
            self.player["current_stage"] += 1
            self.start_stage()

    def analyze_failure(self) -> str:
        """失敗原因を分析してヒントを生成する"""
        if not self.conversation:
            return "会話が行われていません。"
        
        stage = self.get_current_stage()
        enemy_personality = stage.get("description", "Unknown")
        
        last_turn = self.conversation[-2:] # Ally and Enemy
        
        # Use template from prompts.py
        prompt = HINT_ANALYSIS_PROMPT_TEMPLATE.format(
            enemy_personality=enemy_personality,
            last_turn=last_turn
        )
        
        try:
            hint = get_completion(self.player["model"], prompt)
            return hint
        except Exception as e:
            return f"ヒント生成エラー: {str(e)}"
