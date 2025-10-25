# 簡易RAGシステム (OpenAI API 利用デモ)

## 1. プロジェクト概要

このリポジトリは、インターンシップ応募要件である「LLM使用経験（OpenAI APIなど）」を満たすことを証明するために作成した、最小構成のRAG（Retrieval-Augmented Generation）システムです。

Pythonを使用し、OpenAI API（Embeddings, Chat Completions）を直接呼び出して、日本語Wikipediaのデータを基にした質疑応答を実現しています。

## 2. 使用技術

*   **Python 3**
*   **OpenAI API**
    *   Embeddingsモデル: `text-embedding-3-small`
    *   LLMモデル: `gpt-4o-mini`
*   **FAISS** (`faiss-cpu`): ベクトル検索ライブラリ
*   **依存ライブラリ**: `requests`, `python-dotenv`, `numpy`

## 3. セットアップ方法

### 3-1. リポジトリのクローン

```bash
git clone [https://github.com/](https://github.com/)[milkmilkmilkmilkmilk]/jp-rag-minimum.git
cd jp-rag-minimum
```

### 3-2. 依存ライブラリのインストール
```bash
pip3 install -r requirements.txt
```

### 3-3. OpenAI_APIキーの設定
プロジェクトのルートに .env ファイルを作成し、ご自身のOpenAI APIキーを記述してください。
```bash
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
(この .env ファイルは .gitignore によりリポジトリには含まれないようにします)

4. 実行手順
以下のスクリプトを順番に実行してください。

ステップ1: データ取得
Wikipediaから企業データをフェッチし、data/raw/ に保存します。
```bash
python3 01_fetch_data.py
```
ステップ2: データチャンク化
取得したテキストを検索可能なチャンクに分割し、data/processed/chunks.jsonl に保存します。
```bash
python3 chunk_data.py
```

ステップ3: Embeddings生成とインデックス構築
OpenAI API (text-embedding-3-small) を呼び出し、全チャンクをベクトル化します。 FAISSインデックス (faiss_index.bin) を構築し、data/index/ に保存します。
```bash
python3 build_index.py
```
5. 実行（RAGによる質疑応答）
ask.py スクリプトに質問文を渡して実行します。 内部で以下の処理が実行されます。
1.質問文を text-embedding-3-small APIでベクトル化。
2.FAISSインデックスを検索 (Retrieve)。
3.検索結果のチャンクをコンテキストとして gpt-4o-mini APIに渡し、回答を生成 (Generate)。
```bash
python3 ask.py "あなたの質問文"
```
6. 実行例

実行例 1
コマンド:
```bash
python3 ask.py "トヨタ自動車の主な事業は何ですか？"
```

出力結果:

```bash
--- 質問 --- 
トヨタ自動車の主な事業は何ですか?

1. 質問をベクトル化中 (モデル: text-embedding-3-small)...
2. FAISSインデックスを検索中 (Top 3)...

--- 検索された根拠 (上位3件) ---
[1] (出典: トヨタ自動車.txt)
    事業部として事業開始、2003年に営業部門を先行してトヨタ自動車より分社・独立、2010年10月に住宅事業 部門の事業企画や技術開発、生産部門をトヨタ自動車より全面移管し統合。不動産、住宅事業に携わる。...    
[2] (出典: トヨタ自動車.txt)
    きたいヤンマーと、技術・生産部品などの幅広い部分での提携を発表。2017年（平成29年）にはレクサスブ ランドのプレジャーボートを公開、2019年（平成31年）に「LY650」として販売を開始した。取り...
[3] (出典: トヨタ自動車.txt)
    - 1991年設立の完全子会社。レクサスのセダンとSUVを生産。
トヨタ自動車北海道 - 1990年設立の完全子会社。トランスミッションやハイブリッドなどの駆動系部品を生産。
トヨタ紡織 - 1950...

3. LLMに回答を生成依頼中 (モデル: gpt-4o-mini)...

--- LLMによる回答 ---
資料からは分かりません。
```

実行例 2
コマンド:
```bash
python3 ask.py "キーエンスの創業者は誰ですか？"
```

出力結果: 
```bash
--- 質問 --- 
キーエンスの創業者は誰ですか？

1. 質問をベクトル化中 (モデル: text-embedding-3-small)...
2. FAISSインデックスを検索中 (Top 3)...

--- 検索された根拠 (上位3件) ---
[1] (出典: キーエンス.txt)
    株式会社キーエンス（英: KEYENCE CORPORATION）は、大阪府大阪市東淀川区東中島に本社を置く、自動制御機器（PLCと周辺機器）、計測機器、情報機器、光学顕微鏡・電子顕微鏡などの開発およ...
[2] (出典: キーエンス.txt)
    位になるなど日本を代表する優良企業であり、『カンブリア宮殿』などのテレビ番組でも取り上げられた。 
2009年（平成21年）4月3日に、ジャストシステムとの資本・業務提携を行うと発表した。第三者割当て増...    
[3] (出典: キーエンス.txt)
    自動認識事業部
マーキング事業部
画像システム事業部


=== 国内営業所 ===
東日本エリア:
盛岡、仙台、郡山、宇都宮、高崎、熊谷、浦和、水戸、柏、幕張、神田、東京、立川、八王子、横浜、海老名...

3. LLMに回答を生成依頼中 (モデル: gpt-4o-mini)...

--- LLMによる回答 ---
キーエンスの創業者は滝崎武光です。
```



