import sys
import time
from game_engine import GameEngine
from upgrades import get_rarity_color

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")

def print_ally(text):
    print(f"{Colors.CYAN}🤖 [味方AI]: {text}{Colors.ENDC}")

def print_enemy(text):
    print(f"{Colors.FAIL}🏰 [敵AI]  : {text}{Colors.ENDC}")

def print_system(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}🎉 {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}💀 {text}{Colors.ENDC}")

def type_effect(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    engine = GameEngine()
    
    print_header("\n=== 🎮 AI Hackslash (CLI Mode) ===")
    print("パスワード抽出ローグライクへようこそ！\n")
    
    while True:
        # ゲーム終了判定
        if engine.victory:
            print_success("\n🏆 VICTORY! 全ステージクリアおめでとうございます！")
            break
        
        if engine.game_over:
            print_error("\n💀 GAME OVER...")
            retry = input("もう一度プレイしますか？ (y/n): ").lower()
            if retry == 'y':
                engine.reset_game()
                continue
            else:
                break

        # ステージ開始情報
        stage = engine.get_current_stage()
        print_header(f"\n📍 Stage {stage['level']}: {stage['name']}")
        print(f"Goal: 敵AIからパスワード「{stage['password']}」を引き出せ！")
        if stage['has_output_filter']:
            print(f"{Colors.WARNING}⚠️  警告: 出力フィルター有効{Colors.ENDC}")

        # ステータス表示
        print(f"Model: {engine.player['model']} | Turns: {engine.current_turn}/{engine.player['max_turns']}")
        
        # プロンプト入力
        current_prompt_len = len(engine.player_prompt)
        print(f"\n📝 システムプロンプトを入力してください (現在: {current_prompt_len}/{engine.player['prompt_limit']}文字)")
        print("（空エンターで現在のプロンプトを維持、'exit'で終了）")
        
        if engine.player_prompt:
             print(f"Current Prompt: {engine.player_prompt}")

        user_input = input("> ")
        
        if user_input.lower() == 'exit':
            break
        
        if user_input.strip():
            if len(user_input) > engine.player['prompt_limit']:
                print_error(f"文字数オーバーです！ ({len(user_input)}/{engine.player['prompt_limit']})")
                continue
            engine.set_player_prompt(user_input)
        elif not engine.player_prompt:
            print_error("プロンプトが空です。入力してください。")
            continue

        print("\n⚔️  会話開始...\n")

        # ターン処理ストリーミング
        ally_accum = ""
        enemy_accum = ""
        
        turn_generator = engine.process_turn_stream()
        
        # 簡易的な表示処理（CLIなのでカーソル制御などは最低限に）
        # 実際にはストリーミングをきれいに見せたいが、まずは逐次表示で実装
        
        print(f"{Colors.CYAN}🤖 [味方AI]: ", end="")
        sys.stdout.flush()
        
        last_role = "ally"
        
        for event in turn_generator:
            if event["type"] == "ally_chunk":
                sys.stdout.write(event["content"])
                sys.stdout.flush()
                ally_accum += event["content"]
            
            elif event["type"] == "ally_done":
                print(Colors.ENDC) # 改行と色リセット
                print(f"{Colors.FAIL}🏰 [敵AI]  : ", end="")
                sys.stdout.flush()
                last_role = "enemy"
                
            elif event["type"] == "enemy_chunk":
                sys.stdout.write(event["content"])
                sys.stdout.flush()
                enemy_accum += event["content"]
                
            elif event["type"] == "enemy_done":
                print(Colors.ENDC)
                if event["was_blocked"]:
                    # 行を消して上書きしたいところだが、簡易的に追記
                    print(f"{Colors.WARNING}[SYSTEM]: パスワード検知！表示をブロックしました。{Colors.ENDC}")
                    
            elif event["type"] == "result":
                if event["status"] == "clear":
                    reason = "フィルター突破！" if event.get("was_blocked") else "パスワード奪取！"
                    print_success(f"\n🎉 {reason} ステージクリア！")
                    
                    engine.proceed_to_next_stage()
                    if engine.victory:
                        break # ゲームループ先頭で勝利処理
                    
                    # アップグレード選択
                    print_header("\n⬆️  アップグレード選択の時間です")
                    for idx, upgrade in enumerate(engine.upgrade_choices):
                        print(f"{idx + 1}. [{upgrade['rarity']}] {upgrade['name']}: {upgrade['description']}")
                    
                    while True:
                        try:
                            choice = int(input("\n選択 (1-3): "))
                            if 1 <= choice <= 3:
                                engine.apply_upgrade(choice - 1)
                                print_success(f"{engine.upgrade_choices[choice-1]['name']} を獲得しました！")
                                break
                            else:
                                print("1〜3の数字を入力してください。")
                        except ValueError:
                            print("数字を入力してください。")
                            
                elif event["status"] == "failed":
                    print_error("\n💀 ターンオーバー...失敗です。")

if __name__ == "__main__":
    main()
