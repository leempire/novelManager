# 小说阅读器，提供暂停、调速、切换章节功能
import time
import threading
from .record import Robot


class Reader:
    def __init__(self, shelf, speed=10, fps=30):
        self.shelf = shelf
        self.book = None
        self.novel = []  # 小说 [chap1, ...]
        # 阅读进度
        self.curChapter = 0
        self.curWord = 0

        self.reading = False  # 正在阅读
        self.speed = speed  # 阅读速度每秒多少字
        self.fps = fps  # 帧率
        self.pin = 0
        threading.Thread(target=self.thread, daemon=True).start()

    def loadNovel(self, book, curChapter=0, curWord=0):
        """将小说正文加载到缓冲区"""
        self.book = book
        self.novel = self.shelf.getBookChapters(book)
        self.setProgress(curChapter, curWord)
        self.curWord = 0
        if not self.novel:
            raise ValueError

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

    def nextChapter(self):
        self.setProgress(self.curChapter + 1, 0)
        print()

    def lastChapter(self):
        self.setProgress(self.curChapter - 1, 0)
        print()

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

    def speedUp(self):
        """加速"""
        self.speed = round(self.speed * 1.2, 1)

    def speedDown(self):
        """减速"""
        self.speed = round(self.speed / 1.2, 1)

    def forward(self):
        """快进5秒"""
        self.pin += self.speed * 5

    def saveProgress(self):
        """保存进度"""
        self.book['progress'] = [self.curChapter, self.curWord]
        self.shelf.saveShelf()

    def thread(self):
        self.pin = 0
        t0 = time.time()
        while True:
            # 限制帧率
            t = time.time()  # 上一次循环的结束时间
            dt = t - t0  # 上一次循环的总时间
            delta = 1 / self.fps - dt
            if delta > 0:
                time.sleep(delta)  # 限制帧率
                dt = 1 / self.fps
            t0 = time.time()  # 这一次循环的开始时间
            # dt为间隔时间

            # 暂停中
            if not self.reading:
                continue

            # 刷新新的字符
            self.pin += self.speed * dt
            print(self.novel[self.curChapter][int(self.curWord):int(self.pin)], end='', flush=True)
            self.curWord = self.pin
            # 保存进度
            self.saveProgress()

            # 本章读完后，将进度切换到下一章，并暂停阅读
            if self.curWord > len(self.novel[self.curChapter]):
                self.setProgress(self.curChapter + 1, 0)
                self.pin = 0
                self.setReading(False)
                print('\n本章已结束，按空格键继续阅读下一章\n')


class AutoReader(Robot):
    def __init__(self, shelf):
        self.reader = Reader(shelf)
        self.shelf = shelf
        self.on = False
        # 只检测键盘操作
        super().__init__(tick=20, mouse_move=0, mouse_click=0, mouse_scroll=0, key=1, wait=0)

    def getProgress(self):
        """获取当前阅读进度"""
        return [self.reader.curChapter, self.reader.curWord]

    def loadNovel(self, book, curChapter=0, curWord=0):
        """载入小说"""
        self.reader.loadNovel(book, curChapter, curWord)

    def setProgress(self, curChapter=None, curWord=None):
        self.reader.setProgress(curChapter, curWord)

    def switch(self, on=None):
        """切换是否开启"""
        if on is None:
            self.on = not self.on
        else:
            self.on = on
        self.reader.setReading(self.on)

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
                    print('\n已退出阅读模式')
                    print('=' * 50)


if __name__ == '__main__':
    r = Reader()
    r.loadNovel(['这是第一章\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890',
                 '这是第二章\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n'
                 '还是第二章这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890\n'
                 '还是第二章这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890\n'
                 '还是第二章这是一个测试1234567890\n这是一个测试1234567890这是一个测试1234567890\n这是一个测试1234567890',])
    # 开始阅读
    r.setReading()
    time.sleep(8)
    # 测试章节结束后是否暂停
    assert not r.reading
    # 开始阅读
    r.setReading()
    # 是否自动跳转到下一章
    assert r.curChapter == 1
    # 测试加减速
    def testSpeed():
        p0 = r.curWord
        time.sleep(3)
        p1 = r.curWord
        return r.speed, (p1 - p0) / 3

    a = testSpeed()
    r.speedUp()
    b = testSpeed()
    r.speedDown()
    r.speedDown()
    c = testSpeed()
    r.setReading(False)
    print()
    print('预计速度：{}\t实际速度：{}'.format(*a))
    print('预计速度：{}\t实际速度：{}'.format(*b))
    print('预计速度：{}\t实际速度：{}'.format(*c))
