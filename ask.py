import os
import sys
import json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# --- 定数設定 ---
INDEX_DIR = "data/index"
INDEX_FILE = os.path.join(INDEX_DIR, "faiss_index.bin")
METADATA_FILE = os.path.join(INDEX_DIR, "chunks_metadata.json")

# 検索する上位K件
TOP_K = 3

# OpenAIモデル
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

def load_index_and_metadata():
    """FAISSインデックスとメタデータを読み込む"""
    try:
        index = faiss.read_index(INDEX_FILE)
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # メタデータを {id: chunk} の辞書に変換 (検索をしやすくするため)
        metadata_dict = {chunk['id']: chunk for chunk in metadata}
        
        return index, metadata_dict
    except Exception as e:
        print(f"エラー: インデックスまたはメタデータの読み込みに失敗しました: {e}")
        return None, None

def retrieve_chunks(client, index, metadata, query_text):
    """質問文をベクトル化し、FAISSで関連チャンクを検索する (Retrieve)"""
    print(f"\n1. 質問をベクトル化中 (モデル: {EMBEDDING_MODEL})...")
    try:
        # 1. 質問文をベクトル化
        response = client.embeddings.create(input=[query_text], model=EMBEDDING_MODEL)
        query_vector = response.data[0].embedding
        query_vector_np = np.array([query_vector]).astype('float32')

        # 2. FAISSで検索 (k=TOP_K)
        print(f"2. FAISSインデックスを検索中 (Top {TOP_K})...")
        # D: 距離の配列, I: インデックスのID配列
        distances, indices = index.search(query_vector_np, TOP_K)
        
        retrieved_chunks = []
        for i, idx in enumerate(indices[0]):
            # FAISSのインデックスID (0, 1, 2...) から、
            # メタデータのチャンクID (chunk_0000, chunk_0001...) を引く
            chunk_id = f"chunk_{idx:04d}"
            
            if chunk_id in metadata:
                chunk = metadata[chunk_id]
                retrieved_chunks.append({
                    "text": chunk['text'],
                    "source": chunk['source'],
                    "distance": float(distances[0][i])
                })
        
        return retrieved_chunks
        
    except Exception as e:
        print(f"  [エラー] 検索処理に失敗: {e}")
        return []

def generate_answer(client, query_text, context_chunks):
    """検索したチャンクをコンテキストとしてLLMに回答を生成させる (Generate)"""
    
    # プロンプトの構築
    context_str = "\n---\n".join([chunk['text'] for chunk in context_chunks])
    
    system_prompt = "あなたは、提供された資料のみに基づいて質問に回答するAIアシスタントです。資料に記載されていないことは「資料からは分かりません」と回答してください。"
    
    user_prompt = f"""
以下の資料を厳密に参照して、質問に回答してください。

---[資料ここから]---
{context_str}
---[資料ここまで]---

質問: {query_text}
回答:
"""
    
    print(f"\n3. LLMに回答を生成依頼中 (モデル: {LLM_MODEL})...")
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0 # 創造性をおさえる
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"  [エラー] LLM呼び出しに失敗: {e}")
        return None

def main():
    # 1. APIキーの読み込み
    load_dotenv()
    if "OPENAI_API_KEY" not in os.environ:
        print("エラー: 環境変数 OPENAI_API_KEY が設定されていません。")
        return
    
    client = OpenAI()

    # 2. 質問文の取得
    if len(sys.argv) < 2:
        print("エラー: 質問文をコマンドライン引数として入力してください。")
        print("例: python3 ask.py \"トヨタ自動車の主な事業は何ですか？\"")
        return
    
    query_text = " ".join(sys.argv[1:])
    print(f"--- 質問 --- \n{query_text}")

    # 3. インデックスとメタデータの読み込み
    index, metadata = load_index_and_metadata()
    if index is None:
        return

    # 4. 検索 (Retrieve)
    retrieved_chunks = retrieve_chunks(client, index, metadata, query_text)
    
    if not retrieved_chunks:
        print("検索結果が0件でした。")
        return

    print("\n--- 検索された根拠 (上位3件) ---")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"[{i+1}] (出典: {chunk['source']})")
        # テキストが長いので冒頭100文字だけ表示
        print(f"    {chunk['text'][:100]}...")

    # 5. 回答生成 (Generate)
    answer = generate_answer(client, query_text, retrieved_chunks)

    if answer:
        print("\n--- LLMによる回答 ---")
        print(answer)

if __name__ == "__main__":
    main()
