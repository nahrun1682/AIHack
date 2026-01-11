# 実装計画: CLIモードとゲームエンジンの分離

## ゴール
現在 Streamlit (`app.py`) に密結合しているゲームロジックを分離し、CLI (`main.py`) からもゲームをプレイできるようにする。

## 現状の課題
- `app.py` に UI コードとゲームロジック（状態管理、ターン進行、勝利判定）が混在している。
- `st.session_state` に直接依存しているため、CLI などの他のインターフェースでロジックを再利用できない。
- `main.py` は未実装（Hello world のみ）。

## 変更内容

### 1. ゲームロジックの分離 (`game_engine.py`)
新しいモジュール `game_engine.py` を作成し、以下の責務を持たせる。
- **GameEngine クラス**:
    - ゲーム状態の保持（プレイヤー情報、現在のステージ、会話履歴など）
    - ゲーム進行メソッド（`start_game`, `process_turn`, `check_win_condition` 等）
    - LLM クライアントとの連携
- 既存の `game_state.py` も活用するが、UI 依存（`st.session_state` への依存）を排除する形でラップあるいは統合する。

#### [NEW] [game_engine.py](file:///wsl.localhost/Ubuntu/root/work/AIHackslash/game_engine.py)

### 2. CLI の実装 (`main.py`)
`GameEngine` を使用して、ターミナル上でゲームを進行させる。
- 入力: `input()` 関数を使用。
- 出力: `print()` およびリッチな表示（色分けなど）を使用。
- ループ: ユーザー入力を受け取り、エンジンに渡し、結果を表示するループ。

#### [MODIFY] [main.py](file:///wsl.localhost/Ubuntu/root/work/AIHackslash/main.py)

### 3. Streamlit アプリの改修 (`app.py`)
`app.py` のロジック部分を `GameEngine` を呼び出す形に書き換える。
- `st.session_state` に `GameEngine` のインスタンスを保持させる。
- UI 描画処理はそのまま維持し、データの取得元を `GameEngine` に変更する。

#### [MODIFY] [app.py](file:///wsl.localhost/Ubuntu/root/work/AIHackslash/app.py)

## 検証計画

### 自動テスト
- 現状、自動テストフレームワークは導入されていないようだが、ロジック分離により単体テストが可能になる。今回は手動検証を主とする。

### 手動検証
1.  **CLI モード**:
    - `python main.py` で起動。
    - チュートリアルステージがプレイ可能か。
    - パスワード入力でクリア判定されるか。
    - ゲームオーバー判定が機能するか。
2.  **Streamlit モード**:
    - `uv run streamlit run app.py` で起動。
    - 既存の機能が壊れていないか（退行テスト）。
    - 画面更新が正しく行われるか。
