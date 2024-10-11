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

        self.statusbar_shelf_1 = StatusBar(self.frame_shelf)
        self.button_show_shelf = Button(self.statusbar_shelf_1, text="Show")
        self.button_add_shelf = Button(self.statusbar_shelf_1, text="Add")
        self.button_remove_shelf = Button(self.statusbar_shelf_1, text="Remove")
        self.button_export_shelf = Button(self.statusbar_shelf_1, text="Export")
        self.button_update_city = Button(self.statusbar_shelf_1, text="Update")
        self.statusbar_shelf_2 = StatusBar(self.frame_shelf)
        self.button_search_shelf = Button(self.statusbar_shelf_2, text="Search")
        self.entry_search_shelf = Entry(self.statusbar_shelf_2)

        self.frame_city = Frame(self.notebook)

        self.frame_top_city = Frame(self.frame_city)
        self.table_city = Table(self.frame_top_city)
        self.scrollbar_x_city = Scrollbar(self.frame_top_city)
        self.scrollbar_y_city = Scrollbar(self.frame_top_city)

        self.statusbar_city = StatusBar(self.frame_city)
        self.button_update_city = Button(self.statusbar_shelf_1, text="Update")
        self.button_add_city = Button(self.statusbar_city, text="Add")
        self.button_search_city = Button(self.statusbar_city, text="Search")
        self.entry_search_city = Entry(self.statusbar_city)

    def bind(self):

        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def load(self):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        self.root.tk.call('tk', 'scaling', ScaleFactor / 75)

        self.table_shelf.configure_(font=("TkDefaultFont", 10))
        self.table_city.configure_(font=("TkDefaultFont", 10))

        self.button_show_shelf.configure(command=self.show_shelf)
        self.button_add_shelf.configure(command=self.add_shelf)
        self.button_search_shelf.configure(command=self.search_shelf)
        self.button_remove_shelf.configure(command=self.remove_shelf)
        self.button_export_shelf.configure(command=self.export_shelf)
        self.button_update_city.configure(command=self.update_city)
        self.statusbar_shelf_1.add(self.button_show_shelf)
        self.statusbar_shelf_1.add(self.button_add_shelf)
        self.statusbar_shelf_1.add(self.button_remove_shelf)
        self.statusbar_shelf_1.add(self.button_export_shelf)
        self.statusbar_shelf_1.add(self.button_update_city)
        self.statusbar_shelf_2.add(self.button_search_shelf)
        self.statusbar_shelf_2.add(self.entry_search_shelf)
        self.statusbar_shelf_2.show_message("", -1)
        self.scrollbar_y_shelf.configure(command=self.table_shelf.yview)
        self.scrollbar_x_shelf.configure(command=self.table_shelf.xview, orient="horizontal")

        self.button_add_city.configure(command=self.add_city)
        self.button_search_city.configure(command=self.search_city)
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
        self.statusbar_shelf_1.pack(side="bottom", fill="x")
        self.statusbar_shelf_2.pack(side="bottom", fill="x")

        self.notebook.add(self.frame_city, text="city")
        self.frame_top_city.pack(side="top", fill="both", expand=True)
        self.scrollbar_y_city.pack(side="right", fill="y")
        self.scrollbar_x_city.pack(side="bottom", fill="x")
        self.table_city.pack(side="top", expand=True, fill="both")
        self.statusbar_city.pack(side="bottom", fill="x")

    def start(self):
        self.bind()
        self.load()

        for i in range(4):
            self.table_shelf.add_col()
            self.table_city.add_col()

        self.show_shelf()


        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def show_shelf(self):
        books = shelfManager.getShelf()

        for i in range(self.table_shelf.table_size[0]):
            self.table_shelf.del_row(1)
        self.table_shelf.add_row(items=['bookName', 'author', 'wordNumber', 'chapterNumber'])
        for i, book in enumerate(books):
            self.table_shelf.add_row(items=[book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])

    def search_shelf(self):
        r = self.entry_search_shelf.get()

        if r != "":
            keywords = r.split(" ")
            books = shelfManager.search(' '.join(keywords))

            for i in range(self.table_shelf.table_size[0]):
                self.table_shelf.del_row(1)
            self.table_shelf.add_row(items=['bookName', 'author', 'wordNumber', 'chapterNumber'])
            for i, book in enumerate(books):
                self.table_shelf.add_row(items=[book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])
        else:
            self.statusbar_shelf_1.show_message("尚未填入搜索关键词", 3000, color="blue")

    def add_shelf(self):
        data = {"BookName": "all", "Author": ""}
        r = askdict(data, "Search", 2, (self.root.winfo_x(), self.root.winfo_y()))

        if r is not None:
            shelfManager.addFromFile(r["BookName"], r["Author"])

            self.show_shelf()

    def remove_shelf(self):
        index = self.table_shelf.position[0] - 1

        if index >= 1:
            book = shelfManager.remove(str(index))

            result = '已删除：{}'.format(shelfManager.formatBook(book))

            self.statusbar_shelf_1.show_message(result, 3000, "blue")

            self.show_shelf()

    def export_shelf(self):
        index = self.table_shelf.position[0] - 1

        book = shelfManager.export(str(index))
        result = '已导出：{}\n请前往 ./data/export/ 文件夹查看'.format(shelfManager.formatBook(book))

        self.statusbar_shelf_1.show_message(result, 3000, "blue")

    def search_city(self):
        keywords = self.entry_search_city.get()
        # books: [book1, book2, ...]
        # book: {'bookName', 'author', 'wordNumber', 'chapterNumber'}

        for i in range(self.table_city.table_size[0]):
            self.table_city.del_row(1)
        self.table_city.add_row(items=['bookName', 'author', 'wordNumber', 'chapterNumber'])

        books = fq.search(keywords)
        if books is None:
            return
        for i, book in enumerate(books):
            self.table_city.add_row(items=[ book['bookName'], book["author"], book["wordNumber"], book["chapterNumber"]])

    def add_city(self):
        index = self.table_city.position[0]-2
        if not 0 <= index < len(fq.books):
            self.statusbar_city.show_message('序号错误，请先使用search搜索后，再添加相应书籍', 3000, "blue")
        book = fq.books[index]

        shelfManager.addFromCity(book)
        self.show_shelf()

    def update_city(self):

        def _():
            index = self.table_shelf.position[0] - 1

            for i, book in enumerate(shelfManager.getShelf()):
                if index >= 1 and index != i+1:
                    continue

                if book['src'].isdigit():  # 书籍来源为city，可更新
                    chapters = fq.getChapters(book['src'])  # 章节id + 章节标题 的列表
                    cc = shelfManager.getBookChapters(book)  # 本地的章节列表
                    for i, chapter in enumerate(chapters[len(cc):]):  # 从最新章节开始更新
                        text = chapter[1] + fq.getText(chapter[0])
                        cc.append(text)
                        self.statusbar_shelf_1.show_message('已更新：《{}》 {}\t字数：{}'.format(book['bookName'], chapter[1], len(text)))
                        # 保存
                        if i % 5 == 0:
                            shelfManager.getBookPath(book).write(cc)
                            shelfManager.update()
                    shelfManager.getBookPath(book).write(cc)  # 保存
                    shelfManager.update()
            self.statusbar_shelf_1.show_message('已全部更新完毕')
            self.show_shelf()

        threading.Thread(target=_, daemon=True).start()


App().start()
