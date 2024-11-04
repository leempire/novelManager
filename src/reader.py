# 小说阅读器，提供暂停、调速、切换章节功能
# author: leempire

import os
import threading
import time
import webbrowser
import sys
from .basic import windows
from .basic.fileManager import Path
from . import dataPath
from .basic.record import Robot


def htmlReader(bookName, bookContent, chapter, exportPath, template='hreader'):
    """生成html阅读器"""
    # 读取阅读器模板
    template = template.replace('.html', '') + '.html'
    template = Path(Path(dataPath).dirname) / 'html' / template
    if not os.path.exists(str(template)):
        return '模板文件 {} 缺失，请检查文件是否存在，或使用 set hReadTemplate xx 修改模板文件'.format(template)
    tmp = template.read()
    # 渲染模板
    tmp = tmp.replace('//**novel**//', str(bookContent))
    tmp = tmp.replace('//**chapter**//', str(chapter))
    tmp = tmp.replace('//**name**//', bookName)

    exportPath.write(tmp)
    url = 'file://' + str(exportPath).replace('\\', '/')
    webbrowser.open(url)
    return '已打开网页阅读器'


class Reader:
    """
    属性：
    book: dict类型，key: bookName, author, wordNumber, chapterNumber, src, progress
        正在阅读的书籍
        其中src为filePath(import)/digit(from city)，progress为[chapter, word]
    novel: [chap1, ...]

    方法：
        公有方法：
        forward() 快进5秒
        lastChapter() 回到上一章
        loadNovel(book, novel, curChapter=0, curWord=0) 将小说内容加载到缓冲区
        nextChapter() 下一章
        setProgress() 修改进度
        setReading(reading=None) -> reading 切换暂停/开始
        setSpeed(speed) 设置阅读速度
        speedDown() 减速
        speedUp() 加速

        私有方法：
        _saveProgress() 保存进度
        _thread() 阅读进程
    """

    speed = 10  # 阅读速度每秒多少字
    fps = 30  # 帧率

    def __init__(self):
        self.book = None
        self.novel = []  # 小说 [chap1, ...]
        # 阅读进度
        self.curChapter = 0
        self.curWord = 0

        self.reading = False  # 正在阅读
        self.pin = 0
        threading.Thread(target=self._thread, daemon=True).start()

    def _saveProgress(self):
        """保存进度"""
        self.book['progress'] = [self.curChapter, self.curWord]

    def _thread(self):
        self.pin = 0
        t0 = time.time()
        while True:
            # 限制帧率
            t = time.time()  # t0为上次循环开始时间，t为这次循环开始时间
            dt = t - t0  # 上一次循环的总时间
            t0 = t
            time.sleep(1 / self.fps)  # 限制帧率
            # dt为间隔时间

            # 暂停中
            if not self.reading:
                continue

            # 刷新新的字符
            self.pin += self.speed * dt
            print(self.novel[self.curChapter][int(self.curWord):int(self.pin)], end='', flush=True)
            self.curWord = self.pin
            # 保存进度
            self._saveProgress()

            # 本章读完后，将进度切换到下一章，并暂停阅读
            if self.curWord > len(self.novel[self.curChapter]):
                self.setProgress(self.curChapter + 1, 0)
                self.pin = 0
                self.setReading(False)
                print('\n本章已结束，按空格键继续阅读下一章\n')

    def forward(self):
        """快进5秒"""
        self.pin += self.speed * 5

    def lastChapter(self):
        self.setProgress(self.curChapter - 1, 0)
        print('\n')

    def loadNovel(self, book, novel, curChapter=0, curWord=0):
        """将小说正文加载到缓冲区"""
        self.book = book
        self.novel = novel
        self.setProgress(curChapter, curWord)
        self.curWord = 0
        if not self.novel:
            raise ValueError

    def nextChapter(self):
        self.setProgress(self.curChapter + 1, 0)
        print('\n')

    def setProgress(self, curChapter=None, curWord=None):
        if curChapter is not None:
            # 判断章节是否合法
            curChapter = max(0, curChapter)
            curChapter = min(curChapter, len(self.novel) - 1)
            self.curChapter = curChapter
        if curWord is not None:
            # 自动修正合法范围
            curWord = max(0, curWord)
            curWord = min(curWord, len(self.novel[curChapter]))
            self.pin = self.curWord = curWord

    def setReading(self, reading=None):
        """暂停(False) / 播放(True)，默认值时更改当前阅读状态"""
        if reading is None:
            self.reading = not self.reading
        else:
            self.reading = reading
        return self.reading

    def setSpeed(self, speed):
        """设置阅读速度"""
        self.speed = speed

    def speedDown(self):
        """减速"""
        self.speed = round(self.speed / 1.2, 1)

    def speedUp(self):
        """加速"""
        self.speed = round(self.speed * 1.2, 1)


class AutoReader(Robot):
    """
    接收参数：
        saveFun: 保存进度，一般传入saveShelf

    方法：
        getProgress() -> [chapter, word] 获取当前进度
        loadNovel(book, novel, curChapter=0, curWord=0) 载入小说
        setProgress() 设置当前进度
        switch(on=None) 切换当前状态暂停/开始
    """

    def __init__(self, saveFun):
        self.saveFUn = saveFun
        self.reader = Reader()
        self.on = False
        # 只检测键盘操作
        super().__init__(tick=20)

    def getProgress(self):
        """获取当前阅读进度"""
        return [self.reader.curChapter, self.reader.curWord]

    def loadNovel(self, book, novel, curChapter=0, curWord=0):
        """载入小说"""
        self.reader.loadNovel(book, novel, curChapter, curWord)

    def response_key(self, event, key, state):
        if self.on:
            if state == 'down':
                if key == '-':
                    self.reader.speedDown()
                elif key == '=':
                    self.reader.speedUp()
                elif key == 'space':
                    self.reader.setReading()
                elif key == 'right':
                    self.reader.nextChapter()
                elif key == 'left':
                    self.reader.lastChapter()
                elif key == 'down':
                    self.reader.forward()
                elif key == 'esc':  # 退出阅读模式
                    self.switch(False)
                    self.saveFUn()
                    print('\n已退出阅读模式，进度已保存')
                    print('=' * 50)

    def setProgress(self, curChapter=None, curWord=None):
        self.reader.setProgress(curChapter, curWord)

    def switch(self, on=None):
        """切换是否开启"""
        if on is None:
            self.on = not self.on
        else:
            self.on = on
        self.reader.setReading(self.on)

# if __name__ == '__main__':
#     r = Reader()
#     r.loadNovel(['这是第一章\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890',
#                  '这是第二章\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n'
#                  '还是第二章这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890\n'
#                  '还是第二章这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890\n'
#                  '还是第二章这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890',])
#     # 开始阅读
#     r.setReading()
#     time.sleep(8)
#     # 测试章节结束后是否暂停
#     assert not r.reading
#     # 开始阅读
#     r.setReading()
#     # 是否自动跳转到下一章
#     assert r.curChapter == 1
#     # 测试加减速
#     def testSpeed():
#         p0 = r.curWord
#         time.sleep(3)
#         p1 = r.curWord
#         return r.speed, (p1 - p0) / 3
#
#     a = testSpeed()
#     r.speedUp()
#     b = testSpeed()
#     r.speedDown()
#     r.speedDown()
#     c = testSpeed()
#     r.setReading(False)
#     print()
#     print('预计速度：{}\t实际速度：{}'.format(*a))
#     print('预计速度：{}\t实际速度：{}'.format(*b))
#     print('预计速度：{}\t实际速度：{}'.format(*c))
