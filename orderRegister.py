from src import *
from sys import exit


rootOrder = OrderAnalyser()
rootOrder.register('exit', '退出')(exit)

# 书架
shelfOrder = OrderAnalyser()
rootOrder.register('shelf', 'shelf ...\n 书架指令集')(shelfOrder)
shelfManager = ShelfManager()


@shelfOrder.register('show', 'shelf show\n 显示书架所有书籍')
def shelfShow():
    books = shelfManager.getShelf()
    result = ''
    if not books:
        return '您的书架空空如也'
    for i, book in enumerate(books):
        result += '{}. {}\n'.format(i + 1, shelfManager.formatBook(book))
    return result


@shelfOrder.register('add', 'shelf add [bookName] [author=匿名]\n'
                            ' 将要添加的书籍文件（bookName.txt）放入./data/import/目录下，执行命令后可添加到书架')
def shelfAdd(bookName, author='匿名'):
    return shelfManager.addFromFile(bookName, author)


@shelfOrder.register('search', 'shelf search [keywords]\n 在书架内关键字搜索')
def shelfSearch(keywords):
    books = shelfManager.search(keywords)
    result = ''
    for i, book in enumerate(books):
        result += '{}. {}\n'.format(i + 1, shelfManager.formatBook(book))
    return result


@shelfOrder.register('remove', 'shelf remove [index]\n 使用shelf search/show后，在书架中删除index项')
def shelfRemove(index):
    book = shelfManager.remove(index)
    return '已删除：{}'.format(shelfManager.formatBook(book))


# 书城
cityOrder = OrderAnalyser()
rootOrder.register('city', 'city ...\n 书城指令集')(cityOrder)
fq = FQBug()


@cityOrder.register('search', 'city search [keywords]\n 在书城中关键字搜索')
def citySearch(*keywords):
    keywords = ' '.join(keywords)
    books = fq.search(keywords)
    result = ''
    for i, book in enumerate(books):
        result += '{}. {}\n'.format(i + 1, shelfManager.formatBook(book))
    return result


@cityOrder.register('add', 'city add [index]\n 将书城搜索的结果序号对应的书籍添加到书城')
def cityAdd(index):
    index = int(index) - 1
    if not 0 <= index < len(fq.books):
        return '序号错误，请先使用city search搜索后，再添加相应书籍'
    book = fq.books[index]
    return shelfManager.addFromCity(book)


@cityOrder.register('update', 'city update\n 更新书架中的所有书籍）')
def cityUpdate():
    for book in shelfManager.getShelf():
        if book['src'].isdigit():  # 书籍来源为city，可更新
            chapters = fq.getChapters(book['src'])  # 章节id + 章节标题 的列表
            cc = shelfManager.getBookChapters(book)  # 本地的章节列表
            for i, chapter in enumerate(chapters[len(cc):]):  # 从最新章节开始更新
                text = chapter[1] + fq.getText(chapter[0])
                cc.append(text)
                print('已更新：《{}》 {}'.format(book['bookName'], chapter[1]))
                # 保存
                if i % 5 == 0:
                    shelfManager.getBookPath(book).write(cc)
                    shelfManager.update()
            shelfManager.getBookPath(book).write(cc)  # 保存
            shelfManager.update()
    return '已全部更新完毕'


while True:
    resp = rootOrder(input())
    if resp:
        print(resp)
        print('\n' + '=' * 50)
