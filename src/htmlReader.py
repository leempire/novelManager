import webbrowser


def htmlReader(book, shelf, chapter=None):
    # 获取书名及内容
    bookName = book['bookName']
    bookContent = [chap.split('\n') for chap in shelf.getBookChapters(book)]  # [[para1, para2, ...] #chap1, ...]
    # 获取阅读进度
    if chapter is None:
        curChap = book['progress'][0]

    # 读取阅读器模板
    with open('./html/hreader.html', encoding='utf-8') as f:
        tmp = f.read()
    # 渲染模板
    tmp = tmp.replace('//**novel**//', str(bookContent))
    tmp = tmp.replace('//**chapter**//', str(chapter))
    tmp = tmp.replace('//**name**//', bookName)

    path = shelf.exportPath / (bookName + '.html')
    path.write(tmp)
    url = 'file://' + str(path).replace('\\', '/')
    webbrowser.open(url)
