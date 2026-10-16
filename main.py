import os
import sys
import feedparser
import requests

# GitHub Secrets または環境変数から取得
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# 対象のYouTubeチャンネルID
CHANNEL_ID = "ここにチャンネルIDを入れる"  # 例: UC_x5XG1OV2P6uYZ5t9VLSUM
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
NOTIFIED_FILE = "notified_ids.txt"


def load_notified_ids():
    if not os.path.exists(NOTIFIED_FILE):
        return set()
    with open(NOTIFIED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_notified_ids(ids):
    with open(NOTIFIED_FILE, "w", encoding="utf-8") as f:
        for vid in sorted(ids):
            f.write(f"{vid}\n")


def send_slack(text):
    if not SLACK_WEBHOOK_URL:
        print("エラー: SLACK_WEBHOOK_URL が設定されていません。")
        sys.exit(1)
    res = requests.post(SLACK_WEBHOOK_URL, json={"text": text})
    res.raise_for_status()


def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("エントリーが見つかりませんでした。")
        return

    notified_ids = load_notified_ids()
    new_notified = set(notified_ids)
    has_update = False

    # 古い順に処理するため逆順でループ
    for entry in reversed(feed.entries):
        # entry.yt_videoid で動画固有のIDが取得可能
        video_id = getattr(entry, "yt_videoid", entry.link.split("v=")[-1])

        if video_id not in notified_ids:
            title = entry.title
            link = entry.link
            
            message = (
                f":bell: *新しい配信枠・動画が追加されました！*\n"
                f"*タイトル*: {title}\n"
                f"*URL*: {link}"
            )
            print(f"通知送信: {title}")
            send_slack(message)

            new_notified.add(video_id)
            has_update = True

    if has_update:
        save_notified_ids(new_notified)
        print("既読リストを更新しました。")
    else:
        print("新規の配信枠はありませんでした。")


if __name__ == "__main__":
    main()
