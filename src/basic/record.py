import time
from pynput import keyboard


class _Event:
    """事件类，cate为名称，att为具体属性"""
    cate = None
    att = None

    def __init__(self):
        pass

    def __str__(self):
        return f'<{self.cate} {" ".join(str(i) for i in self.att)}>'

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            return False

    def __iter__(self):
        return iter((self.cate, *self.att))


class _Key:
    """记录键盘事件的类"""

    class Keyboard(_Event):
        def __init__(self, name, state):
            super().__init__()
            self.cate = 'key'.format(name)
            self.att = (name, state)

    def __init__(self):
        keyboard.Listener(on_press=self.press, on_release=self.release).start()
        self.event = []

    def get_key_name(self, key):
        key = str(key)
        if key.startswith('Key'):
            key = key[key.find('.') + 1:]
        else:
            key = key[1:-1]
        return key

    def press(self, key):
        self.event.append(self.Keyboard(self.get_key_name(key), 'down'))

    def release(self, key):
        self.event.append(self.Keyboard(self.get_key_name(key), 'up'))

    def get(self):
        event = self.event
        self.event = []
        return event


class _Record:
    """记录键盘事件的类"""

    def __init__(self):
        self.key = _Key()
        self.pressed = []

    def get(self):
        key = self.key.get()
        for item in key:
            name, state = item.att
            if state == 'down' and name not in self.pressed:
                self.pressed.append(name)
            if state == 'up' and name in self.pressed:
                self.pressed.remove(name)
        return key

    def get_pressed(self):
        return self.pressed


class Robot:
    def __init__(self, tick=20):
        self.wait = 1 / tick
        self.event = _Record()
        self.record = []

    def run(self):
        while True:
            self.check_operation()
            time.sleep(self.wait)

    def check_operation(self):
        """侦测操作"""
        for event in self.event.get():
            if event.cate == 'key':
                key, state = event.att
                self.response_key(event, key, state)

    def reset_record(self):
        """重置record"""
        self.record = []

    def get_record(self):
        """获取record"""
        return self.record

    def get_pressed(self):
        """获取按下的键"""
        return self.event.get_pressed()

    def response_key(self, event, key, state):
        """键，up/down"""
        pass


if __name__ == '__main__':
    Robot(20).run()
