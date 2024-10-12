from .basic.fileManager import Path, readAndCreate
from .basic.orderAnalyser import OrderAnalyser
from .gui import Window
from .reader import Reader
from . import dataPath


class Setting:
    """
    设置
    可设置属性：
        阅读速度
        自动清空命令行
        html阅读器模板
        GUI配色
    """
    def __init__(self, datapath=dataPath):
        self.settingPath = Path(datapath) / 'setting.json'
        self.defaultSetting = {
            'readSpeed': 10.0,
            'autoCls': 0,
            'hReadTemplate': 'hreader',
            'color': 0,
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
        Window.color = self.setting['color']

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
