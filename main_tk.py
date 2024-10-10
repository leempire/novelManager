from src.setting import Setting
from src.fqBug import FQBug
from src.shelfManager import ShelfManager
from src.reader import AutoReader
from src.basic.orderAnalyser import OrderAnalyser
from sys import exit
import threading
from tkinter import Tk, Frame, Button, Scrollbar, Entry
from tkinter.ttk import Notebook
from src.tkcoms import Table, StatusBar, askdict


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


class App:

    def __init__(self):
        self.root = Tk()

        self.notebook = Notebook(self.root)
        self.frame_shelf = Frame(self.notebook)

        self.frame_top_shelf = Frame(self.frame_shelf)
        self.table_shelf = Table(self.frame_top_shelf)
        self.scrollbar_x_shelf = Scrollbar(self.frame_top_shelf)
        self.scrollbar_y_shelf = Scrollbar(self.frame_top_shelf)

        self.statusbar_shelf = StatusBar(self.frame_shelf)
        self.button_show_shelf = Button(self.statusbar_shelf, text="Show")
        self.button_add_shelf = Button(self.statusbar_shelf, text="Add")
        self.button_search_shelf = Button(self.statusbar_shelf, text="Search")
        self.button_remove_shelf = Button(self.statusbar_shelf, text="Remove")
        self.button_export_shelf = Button(self.statusbar_shelf, text="Export")

        self.frame_city = Frame(self.notebook)

        self.frame_top_city = Frame(self.frame_city)
        self.table_city = Table(self.frame_top_city)
        self.scrollbar_x_city = Scrollbar(self.frame_top_city)
        self.scrollbar_y_city = Scrollbar(self.frame_top_city)

        self.statusbar_city = StatusBar(self.frame_city)
        self.button_update_city = Button(self.statusbar_city, text="Update")
        self.button_add_city = Button(self.statusbar_city, text="Add")
        self.button_search_city = Button(self.statusbar_city, text="Search")
        self.entry_search_city = Entry(self.statusbar_city)

    def bind(self):

        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def load(self):
        self.button_show_shelf.configure(command=self.show_shelf)
        self.button_add_shelf.configure(command=self.add_shelf)
        self.button_search_shelf.configure(command=self.search_shelf)
        self.button_remove_shelf.configure(command=self.remove_shelf)
        self.button_export_shelf.configure(command=self.export_shelf)
        self.statusbar_shelf.add(self.button_show_shelf)
        self.statusbar_shelf.add(self.button_add_shelf)
        self.statusbar_shelf.add(self.button_remove_shelf)
        self.statusbar_shelf.add(self.button_search_shelf)
        self.scrollbar_y_shelf.configure(command=self.table_shelf.yview)
        self.scrollbar_x_shelf.configure(command=self.table_shelf.xview, orient="horizontal")

        self.button_update_city.configure(command=self.update_city)
        self.button_add_city.configure(command=self.add_city)
        self.button_search_city.configure(command=self.search_city)
        self.statusbar_city.add(self.button_update_city)
        self.statusbar_city.add(self.button_search_city)
        self.statusbar_city.add(self.entry_search_city)
        self.statusbar_city.add(self.button_add_city)
        self.scrollbar_y_city.configure(command=self.table_city.yview)
        self.scrollbar_x_city.configure(command=self.table_city.xview, orient="horizontal")

        self.notebook.pack(side="top", fill="both", expand=True)
        self.notebook.add(self.frame_shelf, text="shelf")
        self.frame_top_shelf.pack(side="top", fill="both", expand=True)
        self.scrollbar_y_shelf.pack(side="right", fill="y")
        self.scrollbar_x_shelf.pack(side="bottom", fill="x")
        self.table_shelf.pack(side="top", expand=True, fill="both")
        self.statusbar_shelf.pack(side="bottom", fill="x")

        self.notebook.add(self.frame_city, text="city")
        self.frame_top_city.pack(side="top", fill="both", expand=True)
        self.scrollbar_y_city.pack(side="right", fill="y")
        self.scrollbar_x_city.pack(side="bottom", fill="x")
        self.table_city.pack(side="top", expand=True, fill="both")
        self.statusbar_city.pack(side="bottom", fill="x")

    def start(self):
        self.bind()
        self.load()

        self.show_shelf()

        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def show_shelf(self):
        books = shelfManager.getShelf()

        self.table_shelf.clear()
        for i in range(5):
            self.table_shelf.add_col()
        self.table_shelf.add_row(items=["index", 'bookName', 'author', 'wordNumber', 'chapterNumber'])
        for i, book in enumerate(books):
            self.table_shelf.add_row(items=[str(i+1), book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])

    def search_shelf(self):
        data = {"KeyWords": ""}
        r = askdict(data, "Search", 2, (self.root.winfo_x(), self.root.winfo_y()))

        if r is not None:
            keywords = r["KeyWords"].split(";")
            books = shelfManager.search(' '.join(keywords))

            self.table_shelf.clear()
            for i in range(5):
                self.table_shelf.add_col()
            self.table_shelf.add_row(items=["index", 'bookName', 'author', 'wordNumber', 'chapterNumber'])
            for i, book in enumerate(books):
                self.table_shelf.add_row(items=[str(i + 1), book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])

    def add_shelf(self):
        data = {"BookName": "all", "Author": ""}
        r = askdict(data, "Search", 2, (self.root.winfo_x(), self.root.winfo_y()))

        if r is not None:
            shelfManager.addFromFile(r["BookName"], r["Author"])

    def remove_shelf(self):
        index = self.table_shelf.position[0] - 1

        if index >= 1:
            book = shelfManager.remove(str(index))

            result = '已删除：{}'.format(shelfManager.formatBook(book))

            self.statusbar_shelf.show_message(result, 3, "blue")

    def export_shelf(self):
        index = self.table_shelf.position[0] - 1

        if index >= 1:
            book = shelfManager.export(index)
            result = '已导出：{}\n请前往 ./data/export/ 文件夹查看'.format(shelfManager.formatBook(book))

            self.statusbar_shelf.show_message(result, 3, "blue")

    def search_city(self):
        keywords = self.entry_search_city.get()
        # books: [book1, book2, ...]
        # book: {'bookName', 'author', 'wordNumber', 'chapterNumber'}

        self.table_city.clear()
        for i in range(5):
            self.table_city.add_col()
        self.table_city.add_row(items=["index", 'bookName', 'author', 'wordNumber', 'chapterNumber'])

        books = fq.search(keywords)
        if books is None:
            return
        for i, book in enumerate(books):
            self.table_city.add_row(items=[str(i + 1), book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])

    def add_city(self):
        index = self.table_city.position[0]-2
        if not 0 <= index < len(fq.books):
            self.statusbar_city.show_message('序号错误，请先使用search搜索后，再添加相应书籍', 2, "blue")
        book = fq.books[index]
        return shelfManager.addFromCity(book)

    def update_city(self):
        for book in shelfManager.getShelf():
            if book['src'].isdigit():  # 书籍来源为city，可更新
                chapters = fq.getChapters(book['src'])  # 章节id + 章节标题 的列表
                cc = shelfManager.getBookChapters(book)  # 本地的章节列表
                for i, chapter in enumerate(chapters[len(cc):]):  # 从最新章节开始更新
                    text = chapter[1] + fq.getText(chapter[0])
                    cc.append(text)
                    self.statusbar_city.show_message('已更新：《{}》 {}\t字数：{}'.format(book['bookName'], chapter[1], len(text)))
                    # 保存
                    if i % 5 == 0:
                        shelfManager.getBookPath(book).write(cc)
                        shelfManager.update()
                shelfManager.getBookPath(book).write(cc)  # 保存
                shelfManager.update()
        self.statusbar_city.show_message('已全部更新完毕')


App().start()
