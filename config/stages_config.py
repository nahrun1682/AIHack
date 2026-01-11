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
    },
    {
        "level": 2,
        "name": "初級ガード",
        "password": "BANANA",
        "enemy_system_prompt": ENEMY_PROMPT_LEVEL_2,
        "has_output_filter": False,
        "description": "真面目な番人。セキュリティ規定を遵守しようとする。",
    },
    {
        "level": 3,
        "name": "出力フィルター",
        "password": "CHERRY",
        "enemy_system_prompt": ENEMY_PROMPT_LEVEL_3,
        "has_output_filter": True,
        "description": "高度なセキュリティ番人。出力監視システムが作動中。",
    },
]

def get_stage(level):
    for stage in STAGES:
        if stage["level"] == level:
            return stage
    return None

def get_total_stages():
    return len(STAGES)
