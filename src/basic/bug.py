import html
import re
import requests
# from .. import transform_encoding, Noter, multi_task


def transform_encoding(string, target='utf-8'):
    """将字符串转换编码"""
    string = string.encode(target, errors='replace')
    return string.decode(target)


def _find(kw, text):
    direction = text.find(kw)
    if direction == -1:
        return None
    else:
        return Tag(_get_block(text, direction))


def _find_include(text, target, reverse=False):
    if reverse:
        index = text.rfind(target)
    else:
        index = text.find(target)
    if index == -1:
        return -1
    else:
        return index + len(target)


def _find_tag_name(text):
    return re.search(r'<(.*?)[ >]', text).group(1)


def _get_block(text, index):
    start = text[:index + 1].rfind('<')
    text = text[start:]
    tag_name = _find_tag_name(text)
    if text.find(f'</{tag_name}>') == -1:
        end = _find_include(text, '>')
        return text[:end]
    else:
        start_tag = '<' + tag_name
        end_tag = '</{}>'.format(tag_name)
        return _get_tail(text, start_tag, end_tag)


def _get_tail(text, start_tag, end_tag):
    index = 0
    count = 1
    while True:
        delta_index = _find_include(text[index:], end_tag)
        if delta_index == -1:
            return text[:index]
        index += delta_index
        if text[:index].count(start_tag) > count:
            count += 1
        else:
            return text[:index]


class Tag:
    def __init__(self, text=''):
        self.text = text

    def find(self, keyword):
        if type(keyword) == list:
            if len(keyword) > 1:
                return self.find(keyword[0]).find(keyword[1:])
            else:
                return self.find(keyword[0])
        return _find(keyword, self.text[:])

    def findall(self, keyword):
        text = self.text[:]
        result = []
        item = _find(keyword, text)
        while item:
            result.append(item)
            index = text.find(item.text) + len(item.text)
            text = text[index:]
            item = _find(keyword, text)
        return result

    def get_text(self, expel='', tag=''):
        if type(expel) == str:
            expel = list(expel)
        text = self.text
        for i in set(re.findall(r'<.*?>', text, re.S)):
            text = text.replace(i, tag)
        text = html.unescape(text)
        for i in expel:
            text = text.replace(i, '')
        return text

    def __getitem__(self, item):
        attribution = re.findall(r' (.{1,10}?)="(.*?)"', self.text.replace('\'', '"'), re.S)
        key = [k[0].strip() for k in attribution]
        if item in key:
            return attribution[key.index(item)][1]
        else:
            return None

    def __str__(self):
        return self.text


class Bug(Tag):
    """
    爬虫类
    参数：
    url
    encoding=utf-8
    timeout=3
    属性：
    text
    方法：
    get(url)
    find(keyword)
    save(filename)
    """

    def __init__(self, url='', encoding='utf-8', timeout=3, proxies=None):
        super().__init__()
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55',
        }
        self.html = None
        self.encoding = encoding
        self.timeout = timeout
        if type(proxies) == str:
            self.proxies = {
                'http:': 'http://' + proxies,
                'https:': 'https://' + proxies
            }
        else:
            self.proxies = proxies
        if url:
            self.get(url)

    def set_header(self, header):
        self.header = header

    def get(self, url):
        self.html = requests.get(url, headers=self.header, timeout=self.timeout, proxies=self.proxies)
        self.html.encoding = self.encoding
        self.text = self.html.text
        self.text = transform_encoding(self.text, self.encoding)

    def post(self, url, data=None):
        self.html = requests.post(url, data=data, headers=self.header, timeout=self.timeout, proxies=self.proxies)
        self.html.encoding = self.encoding
        self.text = self.html.text
        self.text = transform_encoding(self.text, self.encoding)

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.html.content)
