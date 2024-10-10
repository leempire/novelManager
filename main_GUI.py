import threading
from sys import exit

from src.basic.orderAnalyser import OrderAnalyser
from src.fqBug import FQBug
from src.gui import Window
from src.reader import AutoReader
from src.setting import Setting
from src.shelfManager import ShelfManager

# 指令解析
rootOrder = OrderAnalyser()
rootOrder.register('exit', '退出')(exit)

# 修改设置
setting = Setting()

# 书架
shelfOrder = OrderAnalyser()
rootOrder.register('shelf', 'shelf ...\n 书架指令集')(shelfOrder)
shelfManager = ShelfManager()
reader = AutoReader(shelfManager)
threading.Thread(target=reader.run, daemon=True).start()

# 书城
cityOrder = OrderAnalyser()
rootOrder.register('city', 'city ...\n 书城指令集')(cityOrder)
fq = FQBug()


class GUI(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = None
        self.updateShelf()
        self.menu_cmd((0, 0))
        self.set_head(('书名', '作者', '章节数', '字数'))

    def updateShelf(self):
        self.setBooks(shelfManager.books)

    def updateCity(self):
        self.setBooks(fq.books)

    def setBooks(self, books):
        l = []
        for b in books:
            l.append([b['bookName'], b['author'], b['chapterNumber'], b['wordNumber']])
        super().set_list(l)

    def top_cmd(self, d):
        # 搜索
        if d == 0:
            entry = self.get_entry()
            if self.mode == 'shelf':
                shelfManager.search(entry)
                self.updateShelf()
            elif self.mode == 'city':
                fq.search(entry)
                self.updateCity()
        # # 添加
        # elif d == 1:
        #     pass

    def menu_cmd(self, d):
        if d[0] == 0:
            if d[1] == 0:  # 书架
                self.set_button(('更新', '导出', '删除'))
                self.updateShelf()
                self.mode = 'shelf'
            elif d[1] == 1:  # 书城
                self.set_button(('添加', '    ', '    '))
                self.updateCity()
                self.mode = 'city'

    def mid_cmd(self, action, index):
        index -= 1
        if index == -1:
            return
        # 更新
        if action == 0:
            book = shelfManager.getBookByIndex(index)
            if book['src'].isdigit():  # 书籍来源为city，可更新
                def thread():
                    chapters = fq.getChapters(book['src'])  # 章节id + 章节标题 的列表
                    cc = shelfManager.getBookChapters(book)  # 本地的章节列表
                    for i, chapter in enumerate(chapters[len(cc):]):  # 从最新章节开始更新
                        text = chapter[1] + fq.getText(chapter[0])
                        cc.append(text)
                        print('已更新：《{}》 {}\t字数：{}'.format(book['bookName'], chapter[1], len(text)))
                        # 保存
                        if i % 5 == 0:
                            shelfManager.getBookPath(book).write(cc)
                            shelfManager.update()
                    shelfManager.getBookPath(book).write(cc)  # 保存
                    shelfManager.update()
                    self.updateShelf()

                # 开启单一线程下载
                threading.Thread(target=thread, daemon=True).start()
            else:  # 不可更新
                pass
        # 导出
        elif action == 1:
            shelfManager.export(index)
        # 删除
        elif action == 2:
            shelfManager.remove(index)
            self.updateShelf()


g = GUI(0)
g.run()
