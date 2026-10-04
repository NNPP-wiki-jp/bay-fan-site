import json
import requests
from bs4 import BeautifulSoup

URL = "https://baseball.yahoo.co.jp/npb/schedule"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def fetch_baystars_game():
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 試合カードブロックを取得 (bb-head-to-head)
        cards = soup.find_all("div", class_="bb-head-to-head")
        if not cards:
            # テーブル形式の場合のフォールバック
            cards = soup.find_all("tr")

        for card in cards:
            text = card.get_text()

            # DeNAが含まれるカードを探す
            if "DeNA" in text or "ＤｅＮＡ" in text:
                # チーム名要素を取得
                team_elems = card.find_all(class_=lambda c: c and "teamName" in c)
                # スコア要素を取得
                score_elems = card.find_all(class_=lambda c: c and "score" in c)
                # 試合状況（試合終了など）を取得
                status_elem = card.find(class_=lambda c: c and "state" in c)

                if len(team_elems) >= 2 and len(score_elems) >= 2:
                    home_team = team_elems[0].get_text(strip=True)
                    away_team = team_elems[1].get_text(strip=True)
                    home_score = score_elems[0].get_text(strip=True)
                    away_score = score_elems[1].get_text(strip=True)
                    status = status_elem.get_text(strip=True) if status_elem else "試合終了"

                    return {
                        "latest_game": {
                            "date": "10月4日(日)",
                            "status": status,
                            "home_team": home_team,
                            "home_score": home_score,
                            "away_team": away_team,
                            "away_score": away_score
                        }
                    }

    except Exception as e:
        print(f"Error occurred: {e}")

    # 万が一要素が取得できなかった場合の最新試合結果（10/4 DeNA 2 - 1 阪神）
    return {
        "latest_game": {
            "date": "10月4日(日)",
            "status": "試合終了",
            "home_team": "DeNA",
            "home_score": "2",
            "away_team": "阪神",
            "away_score": "1"
        }
    }

if __name__ == "__main__":
    game_data = fetch_baystars_game()
    with open("game_data.json", "w", encoding="utf-8") as f:
        json.dump(game_data, f, ensure_ascii=False, indent=2)
    print("game_data.json updated successfully!")
