from .basic.fileManager import Path, readAndCreate
from .basic.orderAnalyser import OrderAnalyser
from .reader import Reader


class Setting:
    """
    设置
    可设置属性：
        阅读速度
        自动清空命令行
        html阅读器模板
    """
    def __init__(self):
        self.settingPath = Path('data/setting.json')
        self.defaultSetting = {
            'readSpeed': 10.0,
            'autoCls': 0,
            'hReadTemplate': 'hreader',
        }
        self.setting = readAndCreate(self.settingPath, dict())
        # 若键值缺失，使用默认值
        for k in self.defaultSetting:
            if k not in self.setting:
                self.setting[k] = self.defaultSetting[k]
        self.settingPath.write(self.setting)

        self.loadSetting()

    def loadSetting(self):
        Reader.speed = self.setting['readSpeed']
        OrderAnalyser.autoCls = self.setting['autoCls']

    def set(self, key, value):
        prev = self.setting[key]
        value = type(prev)(value)
        self.setting[key] = value
        self.settingPath.write(self.setting)
        self.loadSetting()
        return prev, value

    def __getitem__(self, item):
        return self.setting[item]

    def __contains__(self, item):
        return item in self.setting
