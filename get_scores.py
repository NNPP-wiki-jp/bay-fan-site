import json
import re
import requests
from bs4 import BeautifulSoup

# Yahoo!プロ野球 試合日程ページ
URL = "https://baseball.yahoo.co.jp/npb/schedule"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_baystars_game():
    response = requests.get(URL, headers=headers)
    response.encoding = "utf-8"

    if response.status_code != 200:
        print("ページの取得に失敗しました")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 試合カードブロックを取得
    games = soup.find_all("tr", class_=re.compile("bb-scheduleTable__row"))

    for game in games:
        text = game.get_text()

        # DeNAが含まれる試合を探す
        if "DeNA" in text or "ＤｅＮＡ" in text:
            # チーム名とスコアの要素を取得
            teams = game.find_all("a", class_=re.compile("bb-head-to-head__teamName"))
            scores = game.find_all("span", class_=re.compile("bb-head-to-head__score"))
            status = game.find("span", class_=re.compile("bb-head-to-head__state"))

            if len(teams) >= 2 and len(scores) >= 2:
                team_left = teams[0].get_text(strip=True)
                team_right = teams[1].get_text(strip=True)
                score_left = scores[0].get_text(strip=True)
                score_right = scores[1].get_text(strip=True)

                # 勝敗・進行状況
                game_status = status.get_text(strip=True) if status else "試合終了"

                data = {
                    "latest_game": {
                        "date": "最新試合",
                        "status": game_status,
                        "home_team": team_left,
                        "home_score": score_left,
                        "away_team": team_right,
                        "away_score": score_right,
                    }
                }
                return data

    return None


if __name__ == "__main__":
    game_data = fetch_baystars_game()

    if game_data:
        # game_data.jsonに出力
        with open("game_data.json", "w", encoding="utf-8") as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
        print("game_data.json の更新完了！")
    else:
        print("DeNAの試合データが見つかりませんでした。")
