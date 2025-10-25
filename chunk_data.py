import os
import glob
import json

# 入力ディレクトリ (ステップ1で保存した場所)
INPUT_DIR = "data/raw"
# 出力ディレクトリ (チャンクの保存場所)
OUTPUT_DIR = "data/processed"
# 出力ファイル名
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chunks.jsonl")

# チャンク化の設定 (固定値)
CHUNK_SIZE = 500      # 1チャンクの文字数 (目安)
CHUNK_OVERLAP = 100   # チャンク間で重複させる文字数

def chunk_text(text, source_file):
    """テキストを指定されたサイズとオーバーラップで分割する"""
    chunks = []
    
    # テキストの先頭から末尾まで、(SIZE - OVERLAP) ずつスライドしながら処理
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        
        # テキストの i 文字目から (i + CHUNK_SIZE) 文字目までを切り出す
        chunk_content = text[i : i + CHUNK_SIZE]
        
        # 切り出したチャンクが短すぎる場合 (最後のチャンクなど) はスキップしない
        if not chunk_content.strip():
            continue
            
        # チャンク情報を辞書として格納
        chunk_data = {
            "text": chunk_content,
            "source": source_file  # どのファイル由来か
        }
        chunks.append(chunk_data)
        
        # テキストの終端に達したらループを抜ける
        if i + CHUNK_SIZE >= len(text):
            break
            
    return chunks

def main():
    # 出力ディレクトリがなければ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # data/raw/ にある .txt ファイルをすべて取得
    input_files = glob.glob(os.path.join(INPUT_DIR, "*.txt"))
    
    if not input_files:
        print(f"エラー: {INPUT_DIR} に .txt ファイルが見つかりません。")
        print("ステップ1 (01_fetch_data.py) を実行しましたか？")
        return

    all_chunks = []
    
    print(f"{len(input_files)}個のファイルからチャンクを作成します...")
    
    for filepath in input_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            # ファイル名だけを取得 (例: "トヨタ自動車.txt")
            filename = os.path.basename(filepath)
            
            # テキストをチャンク化
            file_chunks = chunk_text(text, filename)
            all_chunks.extend(file_chunks)
            
            print(f"  [成功] {filename} -> {len(file_chunks)} チャンク作成")
            
        except Exception as e:
            print(f"  [エラー] {filepath} の処理に失敗: {e}")

    # すべてのチャンクを .jsonl 形式で保存
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(all_chunks):
                # チャンクごとにユニークなIDを付与
                chunk["id"] = f"chunk_{i:04d}"
                # JSON Lines (jsonl) 形式で書き込む (1行1JSON)
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                
        print(f"\nチャンク化完了。合計 {len(all_chunks)} チャンクを {OUTPUT_FILE} に保存しました。")
        
    except IOError as e:
        print(f"エラー: {OUTPUT_FILE} への書き込みに失敗しました: {e}")

if __name__ == "__main__":
    main()
