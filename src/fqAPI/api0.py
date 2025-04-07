from . import APIBase
from ..basic.bug import Bug
import time
import json


class API0(APIBase):
    def __init__(self):
        self.api = [
            "http://rehaofan.jingluo.love/content?item_id={}",
            "http://yuefanqie.jingluo.love/content?item_id={}",
            "http://apifq.jingluo.love/content?item_id={}",
            "http://fan.jingluo.love/content?item_id={}",
            "https://lsjk.zyii.xyz:3666/content?item_id={}",
        ]
        self.pin = 0

    def getText(self, chapter_id):
        time.sleep(0.5)
        for _ in range(5):
            try:
                bug = Bug()
                url = self.api[self.pin].format(chapter_id)
                print(url)
                bug.get(url)
                bug.text = json.loads(bug.text)['data']['content']

                text = bug.find('<article>').get_text('\r\t', tag='\n')
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
