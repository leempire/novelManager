# 文件管理，支持json格式文件的读写
import os
import json
import shutil
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


def readAndCreate(path, default=None):
    """读取path中的文件内容，若文件不存在，返回default"""
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists:
        return default
    else:
        return path.read()


class Path:
    def __init__(self, path):
        """初始化，输入文件相对/绝对路径"""
        self.path = os.path.abspath(str(path))

    @property
    def exists(self):
        """文件是否存在"""
        return os.path.exists(self.path)

    @property
    def type(self):
        """文件类型，目录文件返回'dir'，其他文件返回'.xx'"""
        if os.path.isdir(self.path):
            return 'dir'
        else:
            return os.path.splitext(self.path)[1]

    @property
    def dirname(self):
        """目录名"""
        return os.path.dirname(self.path)

    @property
    def filename(self):
        """获取不带后缀的文件名"""
        return os.path.basename(self.path).split('.')[0]

    def __eq__(self, other):
        if not isinstance(other, Path):
            other = Path(other)
        return other.path == self.path

    def __truediv__(self, other):
        """路径拼接"""
        return Path(os.path.join(self.path, other))

    def __str__(self):
        return self.path

    def listdir(self):
        """列举目录下的所有文件"""
        return [Path((self / i).path) for i in os.listdir(self.path)]

    def read(self, encoding='utf-8'):
        """读取文件，若为json文件，直接读取为对象"""
        if self.type == '.json':
            with open(self.path, encoding=encoding) as f:
                return json.load(f)
        else:
            with open(self.path, encoding=encoding) as f:
                return f.read()

    def write(self, obj, encoding='utf-8'):
        """写入文件，若为json文件，直接写入对象"""
        self.createDir(Path(self.dirname))  # 创建目录
        if self.type == '.json':
            with open(self.path, 'w', encoding=encoding) as f:
                json.dump(obj, f, indent=2, ensure_ascii=False)
        else:
            with open(self.path, 'w', encoding=encoding) as f:
                f.write(obj)

    def createDir(self, name=None):
        """创建name目录，name为None时创建self.path目录"""
        if name is None:
            self.createDir(self)
            return
        if not isinstance(name, Path):
            name = Path(self / name)
        root = str(name).replace('\\', '/')
        dirs = root.split('/')
        root = ''
        for d in dirs:
            root += d + '/'
            if not os.path.exists(root):
                os.mkdir(root)
        return name

    def remove(self):
        """删除文件或目录"""
        if not self.exists:
            return
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)


if __name__ == '__main__':
    # 测试json读写
    a = [1, 2, 3]
    Path('a.json').write(a)
    assert a == Path('a.json').read()
    assert Path('a.json').exists  # 测试exists
    assert Path('a.json').type == '.json'  # 测试type
    # 测试删除文件
    Path('a.json').remove()
    assert not Path('a.json').exists
    # 测试真除、自动创建目录并写入文件
    p = Path('tmp')
    file = p / 'a.txt'
    file.write('hello')
    assert Path('tmp/a.txt').exists
    # 测试删除目录
    Path('tmp').remove()
    assert not Path('tmp').exists

