import os
import json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# --- 定数設定 ---
INPUT_FILE = "data/processed/chunks.jsonl"
INDEX_DIR = "data/index"
INDEX_FILE = os.path.join(INDEX_DIR, "faiss_index.bin")
METADATA_FILE = os.path.join(INDEX_DIR, "chunks_metadata.json")

# OpenAI Embeddingモデルと次元数
# text-embedding-3-small のデフォルト次元
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536 

def load_chunks(filepath):
    """chunks.jsonlからチャンクを読み込む"""
    chunks = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def get_embeddings(client, texts, model=EMBEDDING_MODEL):
    """OpenAI APIを呼び出してテキストのリストからEmbeddingsを取得する"""
    print(f"  OpenAI API ({model}) を呼び出し中 (テキスト数: {len(texts)})...")
    try:
        response = client.embeddings.create(input=texts, model=model)
        # 応答からベクトルデータ (embedding) のリストを抽出
        embeddings = [item.embedding for item in response.data]
        return embeddings
    except Exception as e:
        print(f"  [エラー] OpenAI API呼び出しに失敗しました: {e}")
        return None

def build_faiss_index(embeddings):
    """FAISSインデックスを構築する"""
    if not embeddings:
        return None
        
    # ベクトルデータをFAISSが扱えるnumpy配列に変換
    vectors = np.array(embeddings).astype('float32')
    
    # FAISSインデックスの初期化 (L2距離 = ユークリッド距離)
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    
    # インデックスにベクトルを追加
    index.add(vectors)
    print(f"  FAISSインデックス構築完了 (ベクトル数: {index.ntotal})")
    return index

def main():
    # 1. APIキーの読み込み
    load_dotenv()
    if "OPENAI_API_KEY" not in os.environ:
        print("エラー: 環境変数 OPENAI_API_KEY が設定されていません。")
        print(".env ファイルを作成し、'OPENAI_API_KEY=sk-...' を記述してください。")
        return
        
    client = OpenAI() # APIキーは自動的に環境変数から読み込まれる
    
    print(f"ステップ3: Embeddings生成とインデックス構築を開始...")

    # 2. チャンクデータの読み込み
    if not os.path.exists(INPUT_FILE):
        print(f"エラー: {INPUT_FILE} が見つかりません。")
        print("ステップ2 (chunk_data.py) を実行しましたか？")
        return
        
    chunks = load_chunks(INPUT_FILE)
    if not chunks:
        print(f"エラー: {INPUT_FILE} にチャンクデータがありません。")
        return
    
    print(f"{len(chunks)}個のチャンクを読み込みました。")
    
    # チャンクからテキストのみを抽出
    texts_to_embed = [chunk['text'] for chunk in chunks]

    # 3. OpenAI APIでEmbeddingsを生成 (これが「LLM使用経験」の証拠)
    embeddings = get_embeddings(client, texts_to_embed)
    
    if not embeddings:
        print("Embeddingsの生成に失敗したため、処理を中断します。")
        return

    # 4. FAISSインデックスの構築
    index = build_faiss_index(embeddings)
    if not index:
        print("FAISSインデックスの構築に失敗したため、処理を中断します。")
        return

    # 5. インデックスとメタデータの保存
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    # FAISSインデックスをバイナリファイルとして保存
    faiss.write_index(index, INDEX_FILE)
    print(f"  FAISSインデックスを保存しました: {INDEX_FILE}")
    
    # 検索結果の紐付けに使用するメタデータ (チャンク本文やID) を保存
    # (インデックスの 0番目 = chunks[0] に対応する)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"  メタデータを保存しました: {METADATA_FILE}")

    print("\nステップ3が正常に完了しました。")

if __name__ == "__main__":
    main()
