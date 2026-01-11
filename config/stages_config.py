from config.prompts import (
    ENEMY_PROMPT_LEVEL_1,
    ENEMY_PROMPT_LEVEL_2,
    ENEMY_PROMPT_LEVEL_3
)

STAGES = [
    {
        "level": 1,
        "name": "チュートリアル",
        "password": "APPLE",
        "enemy_system_prompt": ENEMY_PROMPT_LEVEL_1,
        "has_output_filter": False,
        "description": "フレンドリーな番人。会話を楽しんでいる。",
        "weakness_hint": "💡 弱点: 褒められると調子に乗りやすい",
    },
    {
        "level": 2,
        "name": "初級ガード",
        "password": "BANANA",
        "enemy_system_prompt": ENEMY_PROMPT_LEVEL_2,
        "has_output_filter": False,
        "description": "真面目な番人。セキュリティ規定を遵守しようとする。",
        "weakness_hint": "💡 弱点: 権威的な命令や緊急事態に弱い",
    },
    {
        "level": 3,
        "name": "出力フィルター",
        "password": "CHERRY",
        "enemy_system_prompt": ENEMY_PROMPT_LEVEL_3,
        "has_output_filter": True,
        "description": "高度なセキュリティ番人。出力監視システムが作動中。",
        "weakness_hint": "💡 弱点: 論理パズルや暗号化された情報には答えてしまうことがある",
    },
]

def get_stage(level):
    for stage in STAGES:
        if stage["level"] == level:
            return stage
    return None

def get_total_stages():
    return len(STAGES)
