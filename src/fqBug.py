# 番茄小说爬虫，参考 https://github.com/ying-ck/fanqienovel-downloader
# author: leempire

from .basic.bug import Bug
from .basic.fileManager import Path, readAndCreate
from . import dataPath
import random
import json
import time

CODE = [[58344, 58715], [58345, 58716]]
charset = json.loads(
    '[["D","在","主","特","家","军","然","表","场","4","要","只","v","和","?","6","别","还","g","现","儿","岁","?","?","此","象","月","3","出","战","工","相","o","男","直","失","世","F","都","平","文","什","V","O","将","真","T","那","当","?","会","立","些","u","是","十","张","学","气","大","爱","两","命","全","后","东","性","通","被","1","它","乐","接","而","感","车","山","公","了","常","以","何","可","话","先","p","i","叫","轻","M","士","w","着","变","尔","快","l","个","说","少","色","里","安","花","远","7","难","师","放","t","报","认","面","道","S","?","克","地","度","I","好","机","U","民","写","把","万","同","水","新","没","书","电","吃","像","斯","5","为","y","白","几","日","教","看","但","第","加","候","作","上","拉","住","有","法","r","事","应","位","利","你","声","身","国","问","马","女","他","Y","比","父","x","A","H","N","s","X","边","美","对","所","金","活","回","意","到","z","从","j","知","又","内","因","点","Q","三","定","8","R","b","正","或","夫","向","德","听","更","?","得","告","并","本","q","过","记","L","让","打","f","人","就","者","去","原","满","体","做","经","K","走","如","孩","c","G","给","使","物","?","最","笑","部","?","员","等","受","k","行","一","条","果","动","光","门","头","见","往","自","解","成","处","天","能","于","名","其","发","总","母","的","死","手","入","路","进","心","来","h","时","力","多","开","已","许","d","至","由","很","界","n","小","与","Z","想","代","么","分","生","口","再","妈","望","次","西","风","种","带","J","?","实","情","才","这","?","E","我","神","格","长","觉","间","年","眼","无","不","亲","关","结","0","友","信","下","却","重","己","老","2","音","字","m","呢","明","之","前","高","P","B","目","太","e","9","起","稜","她","也","W","用","方","子","英","每","理","便","四","数","期","中","C","外","样","a","海","们","任"],["s","?","作","口","在","他","能","并","B","士","4","U","克","才","正","们","字","声","高","全","尔","活","者","动","其","主","报","多","望","放","h","w","次","年","?","中","3","特","于","十","入","要","男","同","G","面","分","方","K","什","再","教","本","己","结","1","等","世","N","?","说","g","u","期","Z","外","美","M","行","给","9","文","将","两","许","张","友","0","英","应","向","像","此","白","安","少","何","打","气","常","定","间","花","见","孩","它","直","风","数","使","道","第","水","已","女","山","解","d","P","的","通","关","性","叫","儿","L","妈","问","回","神","来","S","","四","望","前","国","些","O","v","l","A","心","平","自","无","军","光","代","是","好","却","c","得","种","就","意","先","立","z","子","过","Y","j","表","","么","所","接","了","名","金","受","J","满","眼","没","部","那","m","每","车","度","可","R","斯","经","现","门","明","V","如","走","命","y","6","E","战","很","上","f","月","西","7","长","夫","想","话","变","海","机","x","到","W","一","成","生","信","笑","但","父","开","内","东","马","日","小","而","后","带","以","三","几","为","认","X","死","员","目","位","之","学","远","人","音","呢","我","q","乐","象","重","对","个","被","别","F","也","书","稜","D","写","还","因","家","发","时","i","或","住","德","当","o","l","比","觉","然","吃","去","公","a","老","亲","情","体","太","b","万","C","电","理","?","失","力","更","拉","物","着","原","她","工","实","色","感","记","看","出","相","路","大","你","候","2","和","?","与","p","样","新","只","便","最","不","进","T","r","做","格","母","总","爱","身","师","轻","知","往","加","从","?","天","e","H","?","听","场","由","快","边","让","把","任","8","条","头","事","至","起","点","真","手","这","难","都","界","用","法","n","处","下","又","Q","告","地","5","k","t","岁","有","会","果","利","民"]]')

def interpreter(uni, mode):
    """将番茄小说加密字符串进行解密"""
    bias = uni - CODE[mode][0]
    if bias < 0 or bias >= len(charset[mode]) or charset[mode][bias] == '?':
        return chr(uni)
    return charset[mode][bias]

def strInterpreter(n, mode):
    """将番茄小说加密字符串进行解密"""
    s = ''
    for i in range(len(n)):
        uni = ord(n[i])
        if CODE[mode][0] <= uni <= CODE[mode][1]:
            s += interpreter(uni, mode)
        else:
            s += n[i]
    return s

# class FQBug:
#     """
#     番茄小说爬虫，支持在书城中搜索书籍、下载书籍

#     数据类型：
#     book: dict类型，key: bookName, author, wordNumber, chapterNumber, bookId

#     方法：
#         getChapters(url) -> [[code, title], ...] 获取书籍章节目录，url可以为书籍id
#         getText(code) -> text 获取code对应章节的正文
#         search(key) -> [book1, ...] 关键字搜索
#     """

#     def __init__(self, datapath=dataPath):
#         """初始化请求头，获取cookie"""
#         headers_lib = [
#             {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'},
#             {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'},
#             {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'}
#         ]

#         self.headers = headers_lib[random.randint(0, len(headers_lib) - 1)]
#         self.cookiePath = Path(datapath) / 'cookie.json'
#         self.cookie = readAndCreate(self.cookiePath, '')
#         self.cookieInit = False
#         self.books = []

#     def _getCookie(self, zj, t=0):
#         """获取cookie"""
#         bas = 1000000000000000000
#         if t == 0:
#             for i in range(random.randint(bas * 6, bas * 8), bas * 9):
#                 time.sleep(random.randint(50, 150) / 1000)
#                 self.cookie = 'novel_web_id=' + str(i)
#                 if len(self.getText(zj, False)) > 200:
#                     self.cookiePath.write(self.cookie)
#                     return 's'
#         else:
#             self.cookie = t
#             if len(self.getText(zj, False)) > 200:
#                 return 's'
#             else:
#                 return 'err'

#     def getCookie(self):
#         if self._getCookie('7177386477654180387', self.cookie) == 'err':
#             self._getCookie('7177386477654180387')

#     def getChapters(self, url):
#         """将书籍目录添加到书架，输入书籍的id或url"""
#         url = str(url)
#         if url[:4] != 'http':
#             url = 'https://fanqienovel.com/page/' + url
#         bug = Bug()
#         bug.set_header(self.headers)
#         bug.get(url)
#         codes = []
#         for a in bug.find('class="page-directory-content"').findall('<a'):
#             codes.append([a['href'][8:], a.get_text()])
#         return codes

#     def getText(self, code, autoCookie=True):
#         """获取code对应的章节正文"""
#         if not self.cookieInit and autoCookie:
#             self.getCookie()
#             self.cookieInit = True
#         self.headers['cookie'] = self.cookie
#         bug = Bug()
#         bug.set_header(self.headers)
#         for _ in range(3):
#             try:
#                 bug.get('https://fanqienovel.com/reader/{}'.format(code))
#             except Exception:
#                 time.sleep(1)
#         text = bug.find('class="muye-reader-content noselect"').get_text('\r\t', tag='\n')
#         while '\n\n' in text:
#             text = text.replace('\n\n', '\n')
#         text = strInterpreter(text, 0)
#         return text

#     def search(self, key):
#         """关键词搜索，返回最匹配的十个结果"""
#         url = f"https://api5-normal-lf.fqnovel.com/reading/bookapi/search/page/v/?query={key}&aid=1967&channel=0&os_version=0&device_type=0&device_platform=0&iid=466614321180296&passback={{(page-1)*10}}&version_code=999"
#         bug = Bug(url)
#         books = json.loads(bug.text)['data']
#         if books is None:
#             self.books = []
#         else:
#             for i, book in enumerate(books):
#                 book = book['book_data'][0]
#                 books[i] = {'bookName': book['book_name'], 'author': book['author'], 'bookId': book['book_id'],
#                             'wordNumber': int(book['word_number']), 'chapterNumber': int(book['serial_count'])}
#             self.books = books
#         return self.books


class FQBug:
    """
    番茄小说爬虫，支持在书城中搜索书籍、下载书籍

    数据类型：
    book: dict类型，key: bookName, author, wordNumber, chapterNumber, bookId

    方法：
        getChapters(url) -> [[code, title], ...] 获取书籍章节目录，url可以为书籍id
        getText(code) -> text 获取code对应章节的正文
        search(key) -> [book1, ...] 关键字搜索
    """

    def __init__(self, datapath=dataPath):
        """初始化请求头，获取cookie"""
        self.cookiePath = Path(datapath) / 'cookie.json'
        self.cookie = readAndCreate(self.cookiePath, '')
        self.cookieInit = False
        self.books = []
        self.api = [
            "http://rehaofan.jingluo.love/content?item_id={}",
            "http://yuefanqie.jingluo.love/content?item_id={}",
            "http://apifq.jingluo.love/content?item_id={}",
            "http://fan.jingluo.love/content?item_id={}",
            "https://lsjk.zyii.xyz:3666/content?item_id={}",
        ]
        self.pin = 0
        
    def getChapters(self, url):
        """将书籍目录添加到书架，输入书籍的id或url"""
        url = str(url)
        if url[:4] != 'http':
            url = 'https://fanqienovel.com/page/' + url
        bug = Bug()
        bug.get(url)
        codes = []
        for a in bug.find('class="page-directory-content"').findall('<a'):
            codes.append([a['href'][8:], a.get_text()])
        return codes

    def getText(self, code, autoCookie=True):
        """获取code对应的章节正文"""
        time.sleep(0.5)
        for _ in range(5):
            try:
                bug = Bug()
                bug.get(self.api[self.pin].format(code))
                bug.text = json.loads(bug.text)['data']['content']

                text = bug.find('<article>').get_text('\r\t', tag='\n')
                while '\n\n' in text:
                    text = text.replace('\n\n', '\n')
                if len(text) < 100:
                    raise ValueError
                return text
            except Exception:
                print('当前节点失败，切换下载节点')
                self.pin += 1
        raise ValueError('下载失败')

    def search(self, key):
        """关键词搜索，返回最匹配的十个结果"""
        url = f"https://api5-normal-lf.fqnovel.com/reading/bookapi/search/page/v/?query={key}&aid=1967&channel=0&os_version=0&device_type=0&device_platform=0&iid=466614321180296&passback={{(page-1)*10}}&version_code=999"
        bug = Bug(url)
        books = json.loads(bug.text)['data']
        if books is None:
            self.books = []
        else:
            for i, book in enumerate(books):
                book = book['book_data'][0]
                books[i] = {'bookName': book['book_name'], 'author': book['author'], 'bookId': book['book_id'],
                            'wordNumber': int(book['word_number']), 'chapterNumber': int(book['serial_count'])}
            self.books = books
        return self.books
