# 注册指令，每个函数上面的 @... 的第二个参数为函数功能说明
# author: leempire

import os
import threading
from sys import exit
from src import dataPath
from src.basic.orderAnalyser import OrderAnalyser
from src.fqBug import FQBug
from src.reader import AutoReader, htmlReader
from src.setting import Setting
from src.shelfManager import ShelfManager
from src.runScript import RunScript

# 指令解析
rootOrder = OrderAnalyser()
rootOrder.register('exit', '安全退出程序')(exit)
rootOrder.register('quit', '安全退出程序')(exit)
# 修改设置
setting = Setting()
# 书架
shelfManager = ShelfManager()
# 命令行阅读器
reader = AutoReader(shelfManager.saveShelf)
threading.Thread(target=reader.run, daemon=True).start()
# 书城爬虫
fq = FQBug()
# 脚本执行器
runScript = RunScript(handler=rootOrder)


@rootOrder.register('add', 'add [index]\n 将书城搜索的结果序号对应的书籍添加到书城')
def add(index):
    if type(index) == str:
        index = int(index) - 1
    if not 0 <= index < len(fq.books):
        return '序号错误，请先使用city search搜索后，再添加相应书籍'
    book = fq.books[index]
    return shelfManager.addFromCity(book)


@rootOrder.register('content', 'content [index] [beg=1] [len=20]\n'
                               ' 查看书籍目录\n'
                               ' 目录范围为第`beg`章开始往后`len`章')
def content(index, beg='1', len_='20'):
    book = shelfManager.getBookByIndex(index)
    c = shelfManager.getBookContent(book)
    beg, len_ = int(beg), int(len_)
    c = '\n'.join(c[beg - 1:beg - 1 + len_])
    return c


@rootOrder.register('export', 'export [index=None]\n'
                              ' 使用 shelf search/show 后，将index项导出到 ./data/export/ 文件夹\n'
                              ' index取默认值时导出全部书籍\n'
                              ' 当index非数字时，使用搜索到匹配程度最高的结果作为目标')
def export(index=None):
    exportPath = setting['exportPath']
    result = shelfManager.export(index, exportPath=exportPath)
    return result


@rootOrder.register('hread', 'hread [index] [chapter=None]\n'
                             ' 使用shelf search/show 后，使用html阅读index项书籍\n'
                             ' html阅读器的阅读进度单独存储，不与novelManager的阅读进度共享\n'
                             ' 当novelManager阅读进度发生变化时，使用hread将自动同步到novelManager的进度\n'
                             ' 使用hread后将在 ./data/export/ 中产生html文件，下次阅读时可直接打开该文件\n'
                             ' 当index非数字时，使用搜索到匹配程度最高的结果作为目标')
def hRead(index, chapter=None):
    # 获取index对应的书籍
    book = shelfManager.getBookByIndex(index)
    # 获取书名及内容
    bookName = book['bookName']
    bookContent = [chap.split('\n') for chap in shelfManager.getBookChapters(book)]  # [[para1, para2, ...] #chap1, ...]
    # 获取阅读进度
    if chapter is None:
        chapter = book['progress'][0]
    else:  # 限制章节范围
        chapter = int(chapter) - 1
        chapter = min(len(bookContent) - 1, chapter)
        chapter = max(chapter, 0)
    path = shelfManager.exportPath / (bookName + '.html')
    result = htmlReader(bookName, bookContent, chapter, path, setting['hReadTemplate'])
    return result


@rootOrder.register('import', 'import [bookName=all] [author=匿名]\n'
                              ' 将要添加的书籍文件（bookName.txt）放入./data/import/目录下，执行命令后可导入到书架\n'
                              ' bookName=all时，将 ./data/import/ 目录下所有文件添加到书架')
def import_(bookName='all', author='匿名'):
    return shelfManager.addFromFile(bookName, author)


@rootOrder.register('open', 'open\n 打开数据文件夹')
def open_():
    os.startfile(str(dataPath))
    return '已打开数据文件夹'


@rootOrder.register('read', 'read [index] [chapter=None]\n'
                            ' 使用shelf search/show 后，阅读index项书籍\n'
                            ' chapter取默认值时为当前阅读进度\n'
                            ' 当index非数字时，使用搜索到匹配程度最高的结果作为目标')
def read(index, chapter=None):
    book = shelfManager.getBookByIndex(index)
    novel = shelfManager.getBookChapters(book)
    progress = book['progress'] if chapter is None else [int(chapter) - 1, 0]  # 阅读进度
    try:
        reader.loadNovel(book, novel, *progress)
        reader.switch(True)
        return '已开启命令行阅读模式'
    except ValueError:
        return '该书籍为空，无法阅读'


@rootOrder.register('remove', 'remove [index]\n'
                              ' 使用 shelf search/show 后，在书架中删除index项\n'
                              ' 当index非数字时，使用搜索到匹配程度最高的结果作为目标')
def remove(index):
    book = shelfManager.getBookByIndex(index)
    if input('是否确认删除《{}》（Y/N）'.format(book['bookName'])).lower() == 'y':
        book = shelfManager.remove(index)
        return '已删除：{}'.format(shelfManager.formatBook(book))
    else:
        return '取消删除'


@rootOrder.register('run', 'run [filepath] [var1=None] ...\n 执行 filepath 脚本文件，并指定变量值')
def run(filepath, *args):
    return runScript(filepath, args)


@rootOrder.register('search', 'search [keywords] [scope=shelf]\n'
                              ' 在scope范围内搜索关键字keywords\n'
                              ' scope可选: city / shelf')
def search(keywords, scope='shelf'):
    if scope == 'city':
        books = fq.search(keywords)
    elif scope == 'shelf':
        books = shelfManager.search(keywords)
    else:
        return '参数错误：scope只能选city/shelf'
    result = ''
    for i, book in enumerate(books):
        result += '{}. {}\n'.format(i + 1, shelfManager.formatBook(book))
    return result


@rootOrder.register('set', 'set [key=None] [value=None]\n'
                           ' 修改默认设置，若不传入参数，返回当前设置，支持以下设置项\n'
                           ' readSpeed: float 命令行阅读器阅读速度（字/秒）\n'
                           ' autoCls: 0/1 是否开启命令行自动刷新\n'
                           ' hReadTemplate: html阅读器模板，输入 ./html/ 文件夹下的文件名\n'
                           ' color: main_GUI的配色方案，可选0~3，分别对应活力橙, 暗夜黑, 经典白, 靛紫青')
def set_(key=None, value=None):
    if key is None:
        txt = ''
        for k in setting:
            txt += ' {}: {}\n'.format(k, setting[k])
        return txt
    elif value is None:
        return '{}: {}\n'.format(key, setting[key])
    elif key in setting:
        p, n = setting.set(key, value)
        return '已将 {} 项从 {} 修改为 {}\n'.format(key, p, n)
    else:
        return '{} 项不存在\n'.format(key)


@rootOrder.register('show', 'show\n 显示书架所有书籍')
def show():
    # books: [book1, book2, ...]
    # book: {'bookName', 'author', 'wordNumber', 'chapterNumber', 'src', 'progress'}
    books = shelfManager.getShelf()
    result = ''
    if not books:
        return '您的书架空空如也'
    for i, book in enumerate(books):
        result += '{}. {}\n'.format(i + 1, shelfManager.formatBook(book))
    return result


@rootOrder.register('update', 'update\n'
                              ' 更新书架上所有从书城中添加的书籍\n'
                              ' 每更新5章会自动保存，可以随时中断程序')
def update():
    for book in shelfManager.getShelf():
        if book['src'].isdigit():  # 书籍来源为city，可更新
            chapters = fq.getChapters(book['src'])  # 章节id + 章节标题 的列表
            cc = shelfManager.getBookChapters(book)  # 本地的章节列表
            print('正在更新《{}》，发现{}个新章节'.format(book['bookName'], len(chapters) - len(cc)))
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
    return '已全部更新完毕'
