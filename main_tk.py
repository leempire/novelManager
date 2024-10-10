from src.setting import Setting
from src.fqBug import FQBug
from src.shelfManager import ShelfManager
from src.reader import AutoReader
from src.basic.orderAnalyser import OrderAnalyser
from sys import exit
import threading
from tkinter import Tk, Frame, Button, Scrollbar
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

        self.statusbar = StatusBar(self.frame_shelf)
        self.button_show = Button(self.statusbar, text="Update")
        self.button_add = Button(self.statusbar, text="add")
        self.button_search = Button(self.statusbar, text="Search")
        self.button_remove = Button(self.statusbar, text="Remove")

        self.frame_city = Frame(self.notebook)

        self.frame_top_city = Frame()
        self.table_city = Table(self.frame_top_city)
        self.scrollbar_x_city = Scrollbar(self.frame_top_city)
        self.scrollbar_y_city = Scrollbar(self.frame_top_city)


    def bind(self):

        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def load(self):
        self.button_show.configure(command=self.show)
        self.button_add.configure(command=self.add)
        self.button_search.configure(command=self.search)
        self.button_remove.configure(command=self.remove)
        self.statusbar.show_message("", -1)
        self.statusbar.add(self.button_show)
        self.statusbar.add(self.button_add)
        self.statusbar.add(self.button_remove)
        self.statusbar.add(self.button_search)
        self.scrollbar_y_shelf.configure(command=self.table_shelf.yview)
        self.scrollbar_x_shelf.configure(command=self.table_shelf.xview, orient="horizontal")

        self.notebook.pack(side="top", fill="both", expand=True)
        self.notebook.add(self.frame_shelf, text="shelf")
        self.frame_top_shelf.pack(side="top", fill="both", expand=True)
        self.scrollbar_y_shelf.pack(side="right", fill="y")
        self.scrollbar_x_shelf.pack(side="bottom", fill="x")
        self.table_shelf.pack(side="top", expand=True, fill="both")

        self.statusbar.pack(side="bottom", fill="x")

    def start(self):
        self.bind()
        self.load()

        self.show()

        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def show(self):
        books = shelfManager.getShelf()

        self.table_shelf.clear()
        for i in range(5):
            self.table_shelf.add_col()
        self.table_shelf.add_row(items=["index", 'bookName', 'author', 'wordNumber', 'chapterNumber'])
        for i, book in enumerate(books):
            self.table_shelf.add_row(items=[str(i+1), book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])

    def search(self):
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

    def add(self):
        data = {"BookName": "all", "Author": ""}
        r = askdict(data, "Search", 2, (self.root.winfo_x(), self.root.winfo_y()))

        if r is not None:
            shelfManager.addFromFile(r["BookName"], r["Author"])

    def remove(self):
        index = self.table_shelf.position[0] - 1

        if index >= 1:
            book = shelfManager.remove(str(index))

            return '已删除：{}'.format(shelfManager.formatBook(book))


App().start()
