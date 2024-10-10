import re
import time
import keyboard
import pyautogui as ptg
import pynput.mouse as mouse

ptg.PAUSE = 0


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


class _Wait(_Event):
    def __init__(self, t):
        super().__init__()
        self.cate = 'wait'
        self.att = (t,)

    def add(self, t):
        self.att = (self.att[0] + t,)

    def __str__(self):
        return f'<{self.cate} {"%.3f" % self.att[0]}>'


class _Mouse:
    """记录鼠标事件的类"""

    class Move(_Event):
        def __init__(self, x, y):
            super().__init__()
            self.cate = 'mouse_move'
            self.att = (x, y)

    class Click(_Event):
        def __init__(self, x, y, button, pressed):
            super().__init__()
            self.cate = 'mouse_click'
            self.att = [x, y, button, pressed]

    class Scroll(_Event):
        def __init__(self, x, y, dx, dy):
            super().__init__()
            self.cate = 'mouse_scroll'
            self.att = [x, y, dx, dy]

    def __init__(self):
        mouse.Listener(on_move=self.move, on_click=self.click, on_scroll=self.scroll).start()
        self.event = []

    def move(self, x, y):
        self.event.append(self.Move(x, y))

    def click(self, x, y, button, pressed):
        button = str(button).split('.')[-1]
        self.event.append(self.Click(x, y, button, pressed))

    def scroll(self, x, y, dx, dy):
        self.event.append(self.Scroll(x, y, dx, dy))

    def get(self):
        event = self.event
        self.event = []
        return event


class _Key:
    """记录键盘事件的类"""

    class Keyboard(_Event):
        def __init__(self, name, state):
            super().__init__()
            self.cate = 'key'.format(name)
            self.att = (name, state)

    def __init__(self):
        keyboard.hook(self.do)
        self.event = []

    def do(self, key):
        self.event.append(self.Keyboard(key.name, key.event_type))

    def get(self):
        event = self.event
        self.event = []
        return event


class _Record:
    """记录键盘事件的类"""

    def __init__(self):
        self.mouse = _Mouse()
        self.key = _Key()
        self.pressed = []

    def get(self):
        mouse_ = self.mouse.get()
        key = self.key.get()
        for item in key:
            name, state = item.att
            if state == 'down' and name not in self.pressed:
                self.pressed.append(name)
            if state == 'up' and name in self.pressed:
                self.pressed.remove(name)
        return mouse_ + key

    def get_pressed(self):
        return self.pressed


def _do(order):
    """执行命令，传入为[type, att0, att1, ...]"""
    if order[0] == 'wait':
        # <wait 0.200>
        time.sleep(float(order[1]))
    if order[0] == 'mouse_move':
        # <mouse_move 2808 100>
        x, y = int(order[1]), int(order[2])
        ptg.moveTo((x, y))
    if order[0] == 'mouse_click':
        # <mouse_click 1539 1001 left True>
        x, y = int(order[1]), int(order[2])  # 坐标
        button = order[3]  # 按键
        if order[-1] == 'True':
            ptg.mouseDown((x, y), button=button)
        elif order[-1] == 'False':
            ptg.mouseUp((x, y), button=button)
    if order[0] == 'mouse_scroll':
        # <mouse_scroll 1584 1145 0 1>
        x, y = order[1:3]
        clicks = int(order[4]) * 100
        if order[3]:
            ptg.hscroll(clicks, x, y)
        else:
            ptg.vscroll(clicks, x, y)
    if order[0] == 'key':
        # <key s down>
        key = order[1]
        if order[-1] == 'down':
            ptg.keyDown(key)
        elif order[-1] == 'up':
            ptg.keyUp(key)


def act(msg):
    """执行操作"""
    if type(msg) == str:
        for i in re.findall('<(.*?)>', msg):
            order = i.split(' ')
            _do(order)
    elif type(msg) == list:
        for orders in msg:
            _do([str(j) for j in orders])


class Robot:
    def __init__(self, tick=20, mouse_move=1, mouse_click=1, mouse_scroll=1, key=1, wait=1):
        self.wait = 1 / tick
        self.event = _Record()
        self.record = []
        self.to_record = [mouse_move, mouse_click, mouse_scroll, key, wait]

    def run(self):
        while True:
            self.check_operation()
            time.sleep(self.wait)

    def add_wait(self):
        wait = _Wait(self.wait)
        if not self.record:
            self.record.append(wait)
        elif self.record[-1].cate == 'wait':
            self.record[-1]._add(self.wait)
        else:
            self.record.append(wait)

    def check_operation(self):
        """侦测操作"""
        for event in self.event.get():
            if event.cate == 'mouse_move':
                self.response_mouse_move(event, event.att)
                if self.to_record[0]:
                    self.record.append(event)
            if event.cate == 'mouse_click':
                pose, button, state = (event.att[0], event.att[1]), event.att[2], event.att[3]
                self.response_mouse_click(event, pose, button, state)
                if self.to_record[1]:
                    self.record.append(event)
            if event.cate == 'mouse_scroll':
                pose, horizon, vertical = (event.att[0], event.att[1]), event.att[2], event.att[3]
                self.response_mouse_scroll(event, pose, horizon, vertical)
                if self.to_record[2]:
                    self.record.append(event)
            if event.cate == 'key':
                key, state = event.att
                self.response_key(event, key, state)
                if self.to_record[3]:
                    self.record.append(event)
        if self.to_record[4]:
            self.add_wait()

    def set_to_record(self, mouse_move=1, mouse_click=1, mouse_scroll=1, key=1, wait=1):
        self.to_record = [mouse_move, mouse_click, mouse_scroll, key, wait]

    def reset_record(self):
        """重置record"""
        self.record = []

    def get_record(self):
        """获取record"""
        return self.record

    def get_pressed(self):
        """获取按下的键"""
        return self.event.get_pressed()

    def response_mouse_move(self, event, pose):
        """坐标"""
        pass

    def response_mouse_click(self, event, pose, button, state):
        """点击坐标，左右键，点击/释放"""
        pass

    def response_mouse_scroll(self, event, pose, horizon, vertical):
        """坐标，水平方向，竖直方向"""
        pass

    def response_key(self, event, key, state):
        """键，up/down"""
        pass


if __name__ == '__main__':
    Robot(20).run()
