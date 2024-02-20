from mastodon import Mastodon, StreamListener
import os
import threading
import json

# 連合タイムラインをListenするためのクラスを定義
class PublicStreamListener(StreamListener):

    # 引数に生成したMastodonのクライアントが必須
    def __init__(self, client):
        super(PublicStreamListener, self).__init__()
        self.client = client

    def handle_stream(self, response):
        try:
            super().handle_stream(response)
        except:
            pass

    def on_update(self, status):
        try:
            if len(status.mentions) > 3 and status.account.acct.find('@') > 0 and status.account.followers_count < 3:
                statusID = status.id
                account = status.account

                # スパムの通報(リモートサーバにも転送)を投げ、アカウントを停止させる
                print("spam!")
                report = self.client.report(account.id, status_ids=[statusID], forward=True, category='spam')
                self.client.admin_account_moderate(account.id, 'suspend', report_id=report.id)

        except Exception as e:
            print(e)
            pass

def start_listener(instance):
    client = Mastodon(api_base_url=instance['api_base_url'], access_token=instance['access_token'])
    listener = PublicStreamListener(client)
    client.stream_public(listener, remote=True)

# 設定ファイルからインスタンス情報を読み込む
with open('config.json', 'r') as file:
    instances = json.load(file)

# 各インスタンスに対してリスナーをスレッドで起動
for instance in instances:
    threading.Thread(target=start_listener, args=(instance,)).start()
