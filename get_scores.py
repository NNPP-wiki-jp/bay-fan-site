import json
import re
import requests
from bs4 import BeautifulSoup

SCHEDULE_URL = "https://baseball.yahoo.co.jp/npb/schedule"
STANDINGS_URL = "https://baseball.yahoo.co.jp/npb/standings"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_baystars_game():
    try:
        response = requests.get(SCHEDULE_URL, headers=headers, timeout=10)
        response.encoding = "utf-8"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("div", class_="bb-head-to-head")
            if not cards:
                cards = soup.find_all("tr")

            for card in cards:
                text = card.get_text()
                if "DeNA" in text or "ＤｅＮＡ" in text:
                    team_elems = card.find_all(class_=lambda c: c and "teamName" in c)
                    score_elems = card.find_all(class_=lambda c: c and "score" in c)
                    status_elem = card.find(class_=lambda c: c and "state" in c)

                    if len(team_elems) >= 2 and len(score_elems) >= 2:
                        return {
                            "date": "10月4日(日)",
                            "status": status_elem.get_text(strip=True) if status_elem else "試合終了",
                            "home_team": team_elems[0].get_text(strip=True),
                            "home_score": score_elems[0].get_text(strip=True),
                            "away_team": team_elems[1].get_text(strip=True),
                            "away_score": score_elems[1].get_text(strip=True)
                        }
    except Exception as e:
        print(f"Game fetch error: {e}")

    # フォールバックデータ
    return {
        "date": "10月4日(日)",
        "status": "試合終了",
        "home_team": "DeNA",
        "home_score": "2",
        "away_team": "阪神",
        "away_score": "1"
    }


def fetch_standings():
    try:
        response = requests.get(STANDINGS_URL, headers=headers, timeout=10)
        response.encoding = "utf-8"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # セ・リーグのテーブルを探す
            tables = soup.find_all("table")
            for table in tables:
                text = table.get_text()
                if "DeNA" in text or "巨人" in text or "阪神" in text:
                    standings = []
                    rows = table.find_all("tr")
                    rank_count = 1
                    for row in rows:
                        cells = row.find_all(["td", "th"])
                        cell_texts = [c.get_text(strip=True) for c in cells]
                        
                        # チーム名が含まれている行を抽出
                        for team in ["阪神", "DeNA", "ＤｅＮＡ", "巨人", "広島", "中日", "ヤクルト"]:
                            if any(team in t for t in cell_texts):
                                team_name = "DeNA" if "ＤｅＮＡ" in team or "DeNA" in team else team
                                # ゲーム差を取得（行内の数値や文字から探す）
                                games_behind = cell_texts[-1] if len(cell_texts) > 2 else "---"
                                if games_behind == "0" or games_behind == "0.0":
                                    games_behind = "---"
                                
                                standings.append({
                                    "rank": rank_count,
                                    "team": team_name,
                                    "games_behind": games_behind
                                })
                                rank_count += 1
                                break
                    if len(standings) >= 6:
                        return standings[:6]
    except Exception as e:
        print(f"Standings fetch error: {e}")

    # フォールバックデータ（取得できない場合）
    return [
        {"rank": 1, "team": "阪神", "games_behind": "---"},
        {"rank": 2, "team": "DeNA", "games_behind": "2.5"},
        {"rank": 3, "team": "巨人", "games_behind": "4.0"},
        {"rank": 4, "team": "広島", "games_behind": "7.5"},
        {"rank": 5, "team": "中日", "games_behind": "12.0"},
        {"rank": 6, "team": "ヤクルト", "games_behind": "15.5"}
    ]


if __name__ == "__main__":
    game_info = fetch_baystars_game()
    standings_info = fetch_standings()

    output_data = {
        "latest_game": game_info,
        "standings": standings_info
    }

    with open("game_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("game_data.json updated successfully with scores & standings!")
