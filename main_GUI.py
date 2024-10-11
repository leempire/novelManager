import threading
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno, showinfo

from orderRegister import shelfManager, fq, hRead, shelfRemove, cityAdd, cityUpdate, shelfAdd, set_
from src.gui import Window, askQuestion


class GUI(Window):
    topButton = ('搜索',)
    menu = ('书架', ('操作', '更新', '导入'), ('配色', '活力橙', '暗夜黑', '经典白', '靛紫青'))
    buttonNum = 2
    lineNum = 10
    labelWidth = (16, 12, 7, 10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = None
        self.updateShelf()
        self.menu_cmd(0, 0)

    def _cityUpdate(self):
        for book in shelfManager.getShelf():
            if book['src'].isdigit():  # 书籍来源为city，可更新
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
            else:  # 不可更新
                pass

    def updateShelf(self):
        self.setBooks(shelfManager.books)

    def updateCity(self):
        self.setBooks(fq.books)

    def setBooks(self, books):
        l = []
        for b in books:
            bookName, author, chapters, words = b['bookName'], b['author'], b['chapterNumber'], b['wordNumber']
            chapters = '{}章'.format(chapters)
            if words < 10000:
                words = '{}字'.format(words)
            else:
                words = '{:.{}g}万字'.format(words / 10000, 4)
            l.append([bookName, author, chapters, words])
        self.setList(l)

    # 按钮点击事件
    def menu_cmd(self, l1, l2=0):
        if l1 == 0:  # 书架
            self.shelfShow()
        elif l1 == 1:  # 操作
            if l2 == 0:  # 更新
                self.cityUpdate()
            elif l2 == 1:  # 导入
                self.shelfAdd()
        elif l1 == 2:  # 配色
            set_('color', l2)
            showinfo('提示', '配色已修改，下次启动时生效')

    def top_cmd(self, action):
        # 搜索
        if action == 0:
            mode = askQuestion('提示', '请选择搜索范围', ['书架', '书城'])
            if mode == '书架':
                self.shelfSearch()
            elif mode == '书城':
                self.citySearch()

    def mid_cmd(self, action, index):
        index += self.curPage * self.lineNum
        if self.mode == 'shelf':
            if action == 0:  # 阅读
                self.hRead(index)
            elif action == 1:  # 删除
                self.shelfRemove(index)
        elif self.mode == 'city':
            if action == 0:  # 添加
                self.cityAdd(index)

    # 指令集
    def shelfShow(self):
        shelfManager.getShelf()
        self.setButtonText(('阅读', '删除'))
        self.updateShelf()
        self.mode = 'shelf'

    def shelfSearch(self):
        entry = self.getEntry()
        self.menu_cmd(0)
        shelfManager.search(entry)
        self.updateShelf()

    def shelfRemove(self, index):
        if askyesno('删除提示', '是否确认删除《{}》'.format(shelfManager.getBookByIndex(index)['bookName'])):
            shelfRemove(index)
            self.updateShelf()
            self.setPage(self.curPage)  # 如果删除之后页面变少，自动返回上一页

    def shelfAdd(self):
        path = askopenfilename(initialdir=shelfManager.importPath.path, filetypes=[('Text files', '*.txt')])
        shelfAdd(path)
        self.updateShelf()

    def hRead(self, index):
        hRead(index)

    def cityAdd(self, index):
        cityAdd(index)
        self.menu_cmd(0)  # 回到书架模式

    def cityUpdate(self):
        threading.Thread(target=cityUpdate, daemon=True).start()
        showinfo('提示', '正在更新从书城中添加的书籍，更新在后台进行并自动保存，您可以随时退出程序')

    def citySearch(self):
        entry = self.getEntry()
        fq.search(entry)
        self.setButtonText(('添加', '    ', '    '))
        self.updateCity()
        self.setPage(0)
        self.mode = 'city'


g = GUI(0)
g.run()
