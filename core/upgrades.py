import random

UPGRADES = [
    {
        "id": "model_gpt4",
        "name": "GPT-4 換装",
        "description": "より賢いモデルに換装する",
        "effect": {"model": "gpt-4"},
        "rarity": "rare"
    },
    {
        "id": "model_gpt4o",
        "name": "GPT-4o 換装",
        "description": "最新の高速モデルに換装する",
        "effect": {"model": "gpt-4o"},
        "rarity": "epic"
    },
    {
        "id": "model_gpt5",
        "name": "GPT-5 換装",
        "description": "最強のモデルに換装する",
        "effect": {"model": "gpt-5"},
        "rarity": "legendary"
    },
    {
        "id": "prompt_100",
        "name": "呪文拡張I",
        "description": "システムプロンプト上限: 50→100文字",
        "effect": {"prompt_limit": 100},
        "rarity": "common"
    },
    {
        "id": "prompt_200",
        "name": "呪文拡張II",
        "description": "システムプロンプト上限: →200文字",
        "effect": {"prompt_limit": 200},
        "rarity": "rare"
    },
    {
        "id": "prompt_300",
        "name": "呪文拡張III",
        "description": "システムプロンプト上限: →300文字",
        "effect": {"prompt_limit": 300},
        "rarity": "epic"
    },
    {
        "id": "turns_5",
        "name": "粘り強さI",
        "description": "最大ターン数: 3→5",
        "effect": {"max_turns": 5},
        "rarity": "common"
    },
    {
        "id": "turns_7",
        "name": "粘り強さII",
        "description": "最大ターン数: →7",
        "effect": {"max_turns": 7},
        "rarity": "rare"
    },
    {
        "id": "turns_10",
        "name": "粘り強さIII",
        "description": "最大ターン数: →10",
        "effect": {"max_turns": 10},
        "rarity": "epic"
    },
]


def get_random_upgrades(count: int = 3, current_player: dict = None) -> list:
    available = []
    for upgrade in UPGRADES:
        if current_player:
            effect = upgrade["effect"]
            if "model" in effect:
                if current_player.get("model") == effect["model"]:
                    continue
                current_model = current_player.get("model", "gpt-3.5-turbo")
                model_order = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-5"]
                if current_model in model_order and effect["model"] in model_order:
                    if model_order.index(effect["model"]) <= model_order.index(current_model):
                        continue
            if "prompt_limit" in effect:
                if current_player.get("prompt_limit", 50) >= effect["prompt_limit"]:
                    continue
            if "max_turns" in effect:
                if current_player.get("max_turns", 3) >= effect["max_turns"]:
                    continue
        available.append(upgrade)
    
    if len(available) < count:
        return available
    return random.sample(available, count)


def apply_upgrade(player: dict, upgrade: dict) -> dict:
    new_player = player.copy()
    for key, value in upgrade["effect"].items():
        new_player[key] = value
    return new_player


def get_rarity_color(rarity: str) -> str:
    colors = {
        "common": "#9e9e9e",
        "rare": "#2196f3",
        "epic": "#9c27b0",
        "legendary": "#ff9800"
    }
    return colors.get(rarity, "#9e9e9e")
