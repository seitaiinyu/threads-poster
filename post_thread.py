#!/usr/bin/env python3
"""
Threads ツリー投稿スクリプト
------------------------------------------------
公式 Threads Graph API を使い、複数投稿を1つのツリー（スレッド）として連結投稿します。

使い方:
  1. 環境変数を設定
       export THREADS_USER_ID="あなたのThreadsユーザーID"
       export THREADS_ACCESS_TOKEN="長期アクセストークン"
  2. posts.json に投稿テキスト（配列）を用意（同フォルダにサンプルあり）
  3. 実行
       python3 post_thread.py posts.json
       # 確認だけしたい場合（投稿しない）:
       python3 post_thread.py posts.json --dry-run
"""

import os
import sys
import json
import time
import urllib.parse
import urllib.request

API_BASE = "https://graph.threads.net/v1.0"


def _post(path, params):
    url = f"{API_BASE}/{path}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def create_container(user_id, token, text, reply_to_id=None):
    """テキスト投稿コンテナを作成し、コンテナIDを返す"""
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": token,
    }
    if reply_to_id:
        params["reply_to_id"] = reply_to_id
    res = _post(f"{user_id}/threads", params)
    return res["id"]


def publish_container(user_id, token, creation_id):
    """コンテナを公開し、投稿IDを返す"""
    res = _post(f"{user_id}/threads_publish", {
        "creation_id": creation_id,
        "access_token": token,
    })
    return res["id"]


def post_thread(user_id, token, posts, dry_run=False):
    prev_id = None
    for i, text in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] {'(dry-run) ' if dry_run else ''}投稿:\n{text}\n{'-'*40}")
        if dry_run:
            continue
        creation_id = create_container(user_id, token, text, reply_to_id=prev_id)
        # API推奨: publish前に少し待つ
        time.sleep(2)
        post_id = publish_container(user_id, token, creation_id)
        print(f"  -> 投稿完了 ID: {post_id}")
        prev_id = post_id
        time.sleep(2)
    print("\n✅ すべて完了しました。")


def main():
    if len(sys.argv) < 2:
        print("使い方: python3 post_thread.py posts.json [--dry-run]")
        sys.exit(1)

    posts_file = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    user_id = os.environ.get("THREADS_USER_ID")
    token = os.environ.get("THREADS_ACCESS_TOKEN")

    if not dry_run and (not user_id or not token):
        print("環境変数 THREADS_USER_ID と THREADS_ACCESS_TOKEN を設定してください。")
        sys.exit(1)

    with open(posts_file, encoding="utf-8") as f:
        posts = json.load(f)

    if not isinstance(posts, list) or not posts:
        print("posts.json は投稿テキストの配列である必要があります。")
        sys.exit(1)

    post_thread(user_id, token, posts, dry_run=dry_run)


if __name__ == "__main__":
    main()
