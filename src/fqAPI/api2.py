from . import APIBase
from ..basic.bug import Bug
import time
import json


class API2(APIBase):
    def __init__(self):
        self.api = [
            "https://api.xcvts.cn/api/xiaoshuo/fanqie?content={}",
            "https://api.cenguigui.cn/api/tomato/content.php?item_id={}",
        ]
        self.pin = 0

    def getText(self, chapter_id):
        time.sleep(0.5)
        for _ in range(5):
            try:
                bug = Bug()
                url = self.api[self.pin].format(chapter_id)
                bug.get(url)
                bug.text = json.loads(bug.text)['data']['content']

                text = bug.text.replace(' ', '\n')

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
