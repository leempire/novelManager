from . import Path
import difflib


def stringSimilar(s1, s2):
    """字符串s1和s2的匹配程度"""
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def readAndCreate(path, default=None):
    """读取path中的文件内容，若文件不存在，返回default"""
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists:
        return default
    else:
        return path.read()


class ShelfManager:
    def __init__(self, datapath='data'):
        self.datapath = Path(datapath)
        self.importPath = self.datapath / 'import'
        self.storePath = self.datapath / 'store'
        # 书架
        self.shelfPath = self.datapath / 'shelf.json'
        self.shelf = readAndCreate(self.shelfPath, list())
        # 记录上一次显示的结果
        self.books = []
        # 初始化文件
        self.importPath.createDir()

    def formatBook(self, book):
        """将book格式化为字符串"""
        return (f"《{book['bookName']}》\t作者：{book['author']}\t字数：{book['wordNumber']}\t"
                f"章节数：{book['chapterNumber']}")

    def addFromFile(self, bookName, author='匿名'):
        """从import文件夹中，将bookName.txt导入到书架，并将文件解析到store文件夹中"""
        file = self.importPath / (bookName + '.txt')
        text = file.read().strip()
        chapters = text.split('\n\n')
        book = self.add(bookName, author, len(text), len(chapters), file.path)
        self.getBookPath(book).write(chapters)  # 解析到store文件夹
        return '已添加：' + self.formatBook(book)

    def addFromCity(self, book):
        """从city的搜索结果中添加书籍"""
        # book = self.add(book['bookName'], book['author'], book['wordNumber'], book['chapterNumber'], book['bookId'])
        book = self.add(book['bookName'], book['author'], 0, 0, book['bookId'])
        return '已添加：' + self.formatBook(book)

    def add(self, bookName, author, wordNumber, chapterNumber, src):
        """添加到书架，每条数据包括 书名、作者、字数、章节数、书籍链接地址"""
        book = {'bookName': bookName, 'author': author, 'wordNumber': wordNumber,
                           'chapterNumber': chapterNumber, 'src': src}
        self.shelf.append(book)
        self.shelfPath.write(self.shelf)
        return book

    def remove(self, index):
        index = int(index) - 1
        target = self.books[index]
        for i, book in enumerate(self.shelf):
            if target == book:
                del self.shelf[i]
                self.getBookPath(book).remove()
                break
        self.shelfPath.write(self.shelf)
        return target

    def search(self, keywords):
        """在书架内关键字搜索"""
        results = [[book, stringSimilar(book['bookName'] + book['author'], keywords)] for book in self.shelf]
        results = sorted(results, key=lambda item: item[1], reverse=True)
        self.books = [item[0] for item in results]
        return self.books

    def getBookPath(self, book):
        """获取book保存的位置"""
        return self.storePath / (book['bookName'] + '.json')

    def getBookChapters(self, book):
        """获取book的所有章节，列表形式"""
        return readAndCreate(self.getBookPath(book), [])

    def update(self):
        """更新书籍信息"""
        for book in self.getShelf():
            if book['src'].isdigit():  # 书籍来源为city，可能发生了更新
                chapters = self.getBookChapters(book)
                book['chapterNumber'] = len(chapters)
                book['wordNumber'] = len(''.join(chapters).replace('\n', ''))
        self.shelfPath.write(self.shelf)

    def getShelf(self):
        """获取书架全部信息"""
        self.books = self.shelf
        return self.shelf
