#!/usr/bin/env python3
import os, re, logging
import requests
from bs4 import BeautifulSoup
import tweepy

# ログ（動いた記録）を残す設定
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# 投稿専用の設定を読み込む
auth = tweepy.OAuth1UserHandler(
    os.getenv('TW_CONSUMER_KEY'),
    os.getenv('TW_CONSUMER_SECRET'),
    os.getenv('TW_ACCESS_TOKEN'),
    os.getenv('TW_ACCESS_SECRET'),
)
client = tweepy.API(auth)

# すでに投稿したリンクをファイルに保存しておく
SEEN_FILE = 'posted_urls.txt'
if not os.path.exists(SEEN_FILE):
    open(SEEN_FILE, 'w').close()

def load_posted():
    return set(line.strip() for line in open(SEEN_FILE))

def save_posted(url):
    with open(SEEN_FILE, 'a') as f:
        f.write(url + '\n')

# X（旧Twitter）の検索結果ページを読み込む
def fetch_tweets():
    url = 'https://x.com/search?q=ttps%3A%2F%2Fgofile.io%2Fd&src=typed_query'
    headers = {'User-Agent':'Mozilla/5.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'lxml').select('article div[data-testid="tweetText"]')

def main():
    seen = load_posted()
    for elem in fetch_tweets():
        text = elem.get_text()
        match = re.search(r'(ttps://gofile\.io/d[^\s]+)', text)
        if not match: continue
        corrected = 'h' + match.group(1)
        if corrected in seen:
            logging.info(f'既投稿: {corrected}')
            continue
        # 投稿実行
        client.update_status(corrected)
        logging.info(f'投稿成功: {corrected}')
        save_posted(corrected)

if __name__ == '__main__':
    main()
