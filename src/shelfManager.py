from .fileManager import Path, readAndCreate
import difflib


def sanitizeFilename(filename):
    """屏蔽文件名中不能出现的字符，将文件名合法化"""
    illegalChars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    illegalCharsRep = ['＜', '＞', '：', '＂', '／', '＼', '｜', '？', '＊']
    for i in range(len(illegalChars)):
        filename = filename.replace(illegalChars[i], illegalCharsRep[i])
    return filename


def stringSimilar(s1, s2):
    """字符串s1和s2的匹配程度，结果越大，匹配程度越高"""
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


class ShelfManager:
    def __init__(self, datapath='data'):
        self.datapath = Path(datapath)
        self.importPath = self.datapath / 'import'
        self.exportPath = self.datapath / 'export'
        self.storePath = self.datapath / 'store'
        # 书架
        self.shelfPath = self.datapath / 'shelf.json'
        self.shelf = readAndCreate(self.shelfPath, list())
        # 记录上一次显示的结果
        self.books = self.shelf
        # 初始化文件
        self.importPath.createDir()

    def formatBook(self, book):
        """将book格式化为字符串"""
        return (f"《{book['bookName']}》\t作者：{book['author']}\t字数：{book['wordNumber']}\t"
                f"章节数：{book['chapterNumber']}")

    def saveShelf(self):
        """保存"""
        self.shelfPath.write(self.shelf)

    def addFromFile(self, bookName, author='匿名'):
        """从import文件夹中，将bookName.txt导入到书架，并将文件解析到store文件夹中"""
        if bookName == 'all':
            result = ''
            for file in self.importPath.listdir():
                if file.type == '.txt':
                    try:
                        result += self.addFromFile(file.filename, author) + '\n'
                    except Exception as e:
                        result += '{}文件出错:(\n{}\n'.format(file, e)
            return result
        else:
            # 判断书籍是否已存在
            for book in self.shelf:
                if book['bookName'] == bookName and book['author'] == author:
                    return '添加失败，书籍已存在：' + self.formatBook(book)
            # 书籍不存在，正常添加
            file = self.importPath / (bookName.replace('.txt', '') + '.txt')
            text = file.read().strip()
            chapters = text.split('\n\n')
            book = self.add(bookName, author, len(text), len(chapters), file.path)
            self.getBookPath(book).write(chapters)  # 解析到store文件夹
            return '已添加：' + self.formatBook(book)

    def addFromCity(self, book):
        """从city的搜索结果中添加书籍"""
        book = self.add(book['bookName'], book['author'], 0, 0, book['bookId'])
        return '已添加：' + self.formatBook(book)

    def add(self, bookName, author, wordNumber, chapterNumber, src):
        """添加到书架，每条数据包括 书名、作者、字数、章节数、书籍链接地址"""
        book = {'bookName': bookName, 'author': author, 'wordNumber': wordNumber,
                'chapterNumber': chapterNumber, 'src': src, 'progress': [0, 0]}
        self.shelf.append(book)
        self.saveShelf()
        return book

    def remove(self, index):
        """将self.books的index项移除"""
        target = self.books[index]
        for i, book in enumerate(self.shelf):
            if target == book:
                del self.shelf[i]
                self.getBookPath(book).remove()
                break
        self.saveShelf()
        return target

    def export(self, index=None):
        """导出到export文件夹，为0时全部导出"""
        if index is None:
            for book in self.shelf:
                novel = self.getBookPath(book).read()
                novel = '\n'.join(novel)
                path = self.exportPath / (book['bookName'] + '.txt')
                path.write(novel)
            return self.shelf
        else:
            target = self.books[index]
            novel = self.getBookPath(target).read()
            novel = '\n'.join(novel)
            path = self.exportPath / (target['bookName'] + '.txt')
            path.write(novel)
            return target

    def search(self, keywords):
        """在书架内关键字搜索"""
        results = [[book, stringSimilar(book['bookName'] + book['author'], keywords)] for book in self.shelf]
        results = sorted(results, key=lambda item: item[1], reverse=True)
        self.books = [item[0] for item in results]
        return self.books

    def checkIndex(self, index):
        """若index为文字，自动完成搜索并返回匹配程度最高的结果；若为str，转换为int并-1"""
        if index is None:
            return None
        elif not index.isdigit():
            self.search(index)
            return 0
        elif type(index) == str:
            return int(index) - 1
        else:
            return index

    def getBookPath(self, book):
        """获取book保存的位置"""
        return self.storePath / (sanitizeFilename(book['bookName']) + '.json')

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
