from typing import Sequence, Literal
import math
from tkinter import Frame, Scrollbar, Widget


class ListFrame(Frame):
    """
    以列表形式显示 tkinter组件的框架，继承自 tkinter.Frame
    """
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.widgets: list[Widget] = []  # 按顺序存储的所有子组件的列表
        self._shown_widget: list[Widget] = []  # 存储正在显示的组件的列表
        self._cursor: int = 0  # 当前显示的第一个组件（最上面或者最左边组件）的索引

        self._length: int = 8  # 最多一次性显示的组件数目
        self._horizontal: bool = False  # 框架列表是否水平显示

        self._scrollbar = Scrollbar(self, command=self._on_scroll, jump=True, repeatdelay=100, repeatinterval=100)  # 滚动条
        self._scrollbar.pack(side="right", fill="y")

        self._refresh()

    def _on_scroll(self, *args):
        match args:
            case ["moveto", _1]:
                self.roll_to(float(_1))

            case ["scroll", _1, "units"]:
                self.roll(int(_1))

            case ["scroll", _1, "pages"]:
                self.roll(math.ceil(self._length / 2) if int(_1) > 0 else -math.ceil(self._length / 2))

    def configure_(self, length: int = None, horizontal: bool = None, scroll_width: float = None):
        """
        :param length: 最多一次显示的组件数目
        :param horizontal: 列表框架是否水平显示
        :param scroll_width: 滚动条的宽度
        """
        if isinstance(length, int):
            if isinstance(length, int):
                self._length = length
        if isinstance(horizontal, bool):
            if isinstance(horizontal, bool):
                self._horizontal = horizontal
                self._scrollbar.pack_forget()
                if horizontal:
                    self._scrollbar.configure(orient="horizontal")
                    self._scrollbar.pack(side="bottom", fill="x")
                else:
                    self._scrollbar.configure(orient="vertical")
                    self._scrollbar.pack(side="right", fill="y")
        if isinstance(scroll_width, (float, int)):
            self._scrollbar.configure(width=scroll_width)

        self._refresh()

    def cget_(self, key: Literal["length", "horizontal", "scroll_width"]):
        if key == "length":
            return self._length
        elif key == "horizontal":
            return self._horizontal
        elif key == "scroll_width":
            return self._scrollbar.cget("width")

    def _refresh(self):  # 刷新
        if len(self.widgets) <= self._length:  # 如果总组件数少于最大显示数量，则全部显示
            target = self.widgets[:]
        else:
            if self._cursor > len(self.widgets) - self._length:  # 如果已经滚动到底部
                self._cursor = len(self.widgets) - self._length
            elif self._cursor < 0:  # 如果已经滚动到顶部
                self._cursor = 0
            target = self.widgets[self._cursor:self._cursor + self._length]

        for i in self._shown_widget:
            i.pack_forget()

        for j in target:
            if self._horizontal:
                j.pack(side="left", fill="y")
            else:
                j.pack(side="top", fill="x")

        self._shown_widget = target

        if self.widgets:
            self._scrollbar.set(self._cursor / len(self.widgets),
                                (self._cursor + len(self._shown_widget)) / len(self.widgets)
                                )

    def roll(self, n: int):  # 让框架列表根据给定数值滚动，正为向下，右滚动，负为向上，左滚动
        if len(self.widgets) <= self._length:  # 如果总组件数少于最大显示数量，则不做改变
            n = 0
        else:
            if self._cursor + n + self._length > len(self.widgets):  # 如果已经滚动到底部
                n = len(self.widgets) - self._length - self._cursor
            elif self._cursor + n < 0:  # 如果已经滚动到顶部
                n = -self._cursor
        if n > 0:
            for j in range(n):
                t_widget = self.widgets[self._cursor + len(self._shown_widget)]
                self._shown_widget.pop(0).pack_forget()
                if self._horizontal:
                    t_widget.pack(side="left", fill="y")
                else:
                    t_widget.pack(side="top", fill="x")
                self._shown_widget.append(t_widget)
                self._cursor += 1
        elif n < 0:
            for j in range(-n):
                t_widget = self.widgets[self._cursor - 1]
                self._shown_widget.pop(-1).pack_forget()
                if self._horizontal:
                    t_widget.pack(side="left", fill="y", before=self._shown_widget[0] if len(self._shown_widget) else None)
                else:
                    t_widget.pack(side="top", fill="x", before=self._shown_widget[0] if len(self._shown_widget) else None)
                self._shown_widget.insert(0, t_widget)
                self._cursor -= 1

        if self.widgets:
            self._scrollbar.set(self._cursor / (len(self.widgets)),
                                (self._cursor + len(self._shown_widget)) / (len(self.widgets))
                                )

    def roll_to(self, ratio: float):  # 让框架滚动到某个比例所指定位置
        temp = math.ceil(len(self.widgets) * ratio)
        if abs(temp - self._cursor) < self._length:
            self.roll(temp - self._cursor)
        else:
            self._cursor = temp
            self._refresh()

    def append(self, widget: Widget):
        self.widgets.append(widget)
        self._refresh()

    def insert(self, index: int, widget: Widget):
        self.widgets.insert(index, widget)
        self._refresh()

    def extend(self, widgets: Sequence[Widget]):
        self.widgets.extend(widgets)
        self._refresh()

    def pop(self, index: int = -1) -> Widget:
        widget = self.widgets.pop(index)
        self._refresh()
        return widget

    def remove(self, widget: Widget):
        self.widgets.remove(widget)
        self._refresh()

    def clear(self):
        self.widgets.clear()
        self._refresh()
