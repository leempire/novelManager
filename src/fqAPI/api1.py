from . import APIBase
import requests
import time
import json


class API1(APIBase):
    def __init__(self):
        self.api = [
            "https://api.cenguigui.cn/api/tomato/content.php?item_id={}",
            "https://lsjk.zyii.xyz:3666/content?item_id={}",
            "http://api.jingluo.love/content?item_id={}",
            "http://apifq.jingluo.love/content?item_id={}",
            "http://rehaofan.jingluo.love/content?item_id={}"
            ]
        self.pin = 0

    def getText(self, chapter_id):
        # time.sleep(0.5)
        for _ in range(5):
            try:
                html = requests.get(self.api[0].format(chapter_id)).text
                data = json.loads(html)
                text = data['data']['content']
                while '\n\n' in text:
                    text = text.replace('\n\n', '\n')
                if len(text) < 100:
                    raise ValueError
                return text
            except Exception:
                print('当前节点失败，切换下载节点')
                self.pin += 1
                if self.pin == len(self.api):
                    self.pin = 0
        raise ValueError('下载失败')
