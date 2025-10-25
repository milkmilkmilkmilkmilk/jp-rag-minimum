import requests
import os
import time

# データを保存するディレクトリ
SAVE_DIR = "data/raw"

# Wikipedia APIのエンドポイント
API_URL = "https://ja.wikipedia.org/w/api.php"

# 取得対象とする企業ページのタイトル (Wikipedia日本語版の正式なページ名)
COMPANIES = [
    "トヨタ自動車",
    "ソニーグループ",
    "任天堂",
    "キーエンス",
    "ファーストリテイリング"
]

def fetch_wikipedia_content(title):
    """Wikipedia APIから指定されたページのプレーンテキストを取得する"""
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,  # プレーンテキストで取得
        "redirects": 1,     # リダイレクトを解決
    }
    
    # HTTPリクエストヘッダーにUser-Agentを追加
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    try:
        # headers=headers を引数に追加
        response = requests.get(API_URL, params=params, headers=headers)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        data = response.json()
        
        # ページIDを取得 (APIの応答はネストが深い)
        page_id = next(iter(data["query"]["pages"]))
        
        if page_id == "-1":
            print(f"  [エラー] ページが見つかりません: {title}")
            return None
            
        content = data["query"]["pages"][page_id]["extract"]
        return content
        
    except requests.exceptions.RequestException as e:
        print(f"  [エラー] APIリクエスト失敗: {title} ({e})")
        return None

def main():
    # 保存ディレクトリがなければ作成
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    print(f"Wikipediaから企業データの取得を開始します (対象: {len(COMPANIES)}社)")
    
    for company in COMPANIES:
        print(f"処理中: {company}")
        content = fetch_wikipedia_content(company)
        
        if content:
            # ファイル名をサニタイズ (簡易版)
            filename = company.replace(" ", "_").replace("/", "_") + ".txt"
            save_path = os.path.join(SAVE_DIR, filename)
            
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  [成功] 保存しました: {save_path}")
            except IOError as e:
                print(f"  [エラー] ファイル保存失敗: {save_path} ({e})")
        
        # APIへの連続リクエストを避けるため、1秒待機
        time.sleep(1)

    print("データ取得が完了しました。")

if __name__ == "__main__":
    main()
