# 书架管理类，用于书架上书籍的增删查改
# author: leempire

from .basic.fileManager import Path, readAndCreate, sanitizeFilename, stringSimilar
import os
from . import dataPath


class ShelfManager:
    """
    数据类型：
    book: dict类型，key: bookName, author, wordNumber, chapterNumber, src, progress
        其中src为filePath(import)/digit(from city)，progress为[chapter, word]

    属性：
    shelf: [book1, book2, ...]
    
    方法：
        公有方法：
        addFromCity(book) -> 提示语 添加来自书城的book
        addFromFile(booName, author='匿名') -> 提示语 从文件中添加book
        export(index=None) -> book / [book1, ...] 导出书籍，index可以为digit, keywords, index
        formatBook(book) -> 格式化为字符串，包含书名、作者等信息
        getBookByIndex(index) -> 根据index获取book，index可以为digit, keywords, index
        getBookPath(book) -> path 获取书籍地址
        getBookChapters(book) -> [chap1, ...] 获取书籍章节内容
        getShelf() -> [book1, ...] 获取书架信息
        remove(index) -> book 删除书籍，index可以为digit, keywords, index
        saveShelf() 保存书架，阅读时出现进度更新时调用
        search(keywords) -> [book1, ...] 关键字搜索
        update() -> 从书城中更新小说后，书籍的章节和字数发生变化，使用该方法自动更新章节和字数

        私有方法：
        _add(bookName, author, wordNumber, chapterNumber, src) -> book: 添加书籍
        _checkIndex(index) -> index 将各种类型的索引进行转换
    """

    def __init__(self, datapath=dataPath):
        # 正确指向 ./data/ 目录，无论程序在哪里启动
        datapath = Path(datapath)
        self.importPath = datapath / 'import'
        self.exportPath = datapath / 'export'
        self.storePath = datapath / 'store'
        # 书架
        self.shelfPath = datapath / 'shelf.json'
        self.shelf = readAndCreate(self.shelfPath, list())
        # 记录上一次显示的结果
        self.books = self.shelf
        # 初始化文件
        self.importPath.createDir()

    def _add(self, bookName, author, wordNumber, chapterNumber, src):
        """添加到书架，每条数据包括 书名、作者、字数、章节数、书籍链接地址"""
        book = {'bookName': bookName, 'author': author, 'wordNumber': wordNumber,
                'chapterNumber': chapterNumber, 'src': src, 'progress': [0, 0]}
        self.shelf.append(book)
        self.saveShelf()
        return book

    def _checkIndex(self, index):
        """若index为文字，自动完成搜索并返回匹配程度最高的结果；若为str，转换为int并-1"""
        if index is None:
            return None
        elif type(index) == int:
            return index
        elif not index.isdigit():  # 关键字搜索，返回最匹配的结果
            self.search(index)
            return 0
        elif type(index) == str:
            return int(index) - 1
        else:
            raise ValueError

    def addFromCity(self, book):
        """从city的搜索结果中添加书籍"""
        # 判断书籍是否已存在
        for b in self.shelf:
            if book['bookName'] == b['bookName'] and book['author'] == b['author']:
                return '添加失败，书籍已存在：' + self.formatBook(book)
        book = self._add(book['bookName'], book['author'], 0, 0, book['bookId'])
        return '已添加：' + self.formatBook(book)

    def addFromFile(self, bookName='all', author='匿名'):
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
        elif os.path.isfile(bookName):
            file = Path(bookName)
            bookName = file.filename
            text = file.read().strip()
            chapters = text.split('\n\n')
            book = self._add(bookName, author, len(text), len(chapters), file.path)
            self.getBookPath(book).write(chapters)  # 解析到store文件夹
            return '已添加：' + self.formatBook(book)
        else:
            # 判断书籍是否已存在
            for book in self.shelf:
                if book['bookName'] == bookName and book['author'] == author:
                    return '添加失败，书籍已存在：' + self.formatBook(book)
            # 书籍不存在，正常添加
            file = self.importPath / (bookName.replace('.txt', '') + '.txt')
            text = file.read().strip()
            chapters = text.split('\n\n')
            book = self._add(bookName, author, len(text), len(chapters), file.path)
            self.getBookPath(book).write(chapters)  # 解析到store文件夹
            return '已添加：' + self.formatBook(book)

    def export(self, index=None, exportPath=None):
        """导出到export文件夹，为0时全部导出"""
        index = self._checkIndex(index)
        exportPath = exportPath or self.exportPath
        exportPath = Path(exportPath)
        if index is None:
            books = self.shelf
        else:
            books = [self.books[index]]
        result = ''
        for book in books:
            novel = self.getBookPath(book)
            if novel.exists:
                novel = novel.read()
                novel = '\n'.join(novel)
                path = exportPath / (book['bookName'] + '.txt')
                path.write(novel)
                result += '已导出：{}\n'.format(self.formatBook(book))
            else:
                result += '导出失败：《{}》为空\n'.format(book['bookName'])
        result += f'请前往 {exportPath} 文件夹查看'
        return result

    def formatBook(self, book):
        """将book格式化为字符串"""
        return (f"《{book['bookName']}》\t作者：{book['author']}\t字数：{book['wordNumber']}\t"
                f"章节数：{book['chapterNumber']}")

    def getBookByIndex(self, index):
        index = self._checkIndex(index)
        book = self.books[index]
        return book

    def getBookPath(self, book):
        """获取book保存的位置"""
        return self.storePath / (sanitizeFilename(book['bookName']) + '.json')

    def getBookChapters(self, book):
        """获取book的所有章节，列表形式"""
        return readAndCreate(self.getBookPath(book), [])

    def getBookContent(self, book):
        chapters = self.getBookChapters(book)
        content = [chapter[:chapter.find('\n')] for chapter in chapters]
        return content

    def getShelf(self):
        """获取书架全部信息"""
        self.books = self.shelf
        return self.shelf

    def remove(self, index):
        """将self.books的index项移除"""
        index = self._checkIndex(index)
        target = self.books[index]
        for i, book in enumerate(self.shelf):
            if target == book:
                del self.shelf[i]
                self.getBookPath(book).remove()
                break
        self.saveShelf()
        return target

    def saveShelf(self):
        """保存"""
        self.shelfPath.write(self.shelf)

    def search(self, keywords):
        """在书架内关键字搜索"""
        results = [[book, stringSimilar(book['bookName'] + book['author'], keywords)] for book in self.shelf]
        results = sorted(results, key=lambda item: item[1], reverse=True)
        self.books = [item[0] for item in results]
        return self.books

    def update(self):
        """更新书籍信息"""
        for book in self.getShelf():
            if book['src'].isdigit():  # 书籍来源为city，可能发生了更新
                chapters = self.getBookChapters(book)
                book['chapterNumber'] = len(chapters)
                book['wordNumber'] = len(''.join(chapters).replace('\n', ''))
        self.shelfPath.write(self.shelf)
