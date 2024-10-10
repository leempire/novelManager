from typing import Optional, Literal, Union, Any
from tkinter import Widget, Frame, Label
from tkinter.font import Font
from functools import reduce
import math


class StatusBar(Frame):
    """
    状态栏，继承自 tkinter.Frame
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self._widgets: list[Widget] = []  # 存储控件的列表
        self._widget_weight: dict[str, int] = {}  # 控件的名称对应其尺寸权重
        self._timeout_after = None
        self._default_msg: dict[str, Any] = {"text": "二色蓮花蝶", "foreground": "black", "font": ("微软雅黑", 9)}  # 默认消息

        self.label_msg = Label(self, **self._default_msg, background="#E0E0E0")

        self.configure(background="#555555")

        self.label_msg.grid(row=0, column=0, sticky="nsew", padx=1)
        self.grid_columnconfigure(0, weight=1)

    def configure_(self, default_text: Optional[str] = None, default_color: Optional[str] = None, default_font: Union[None, tuple, Font] = None):
        """
        :param default_text: 默认消息文本
        :param default_color: 默认消息颜色
        :param default_font: 默认消息字体
        """
        if default_text is not None:
            self._default_msg["text"] = default_text
        if default_color is not None:
            self._default_msg["foreground"] = default_color
        if default_font is not None:
            self._default_msg["font"] = default_font

    def cget_(self, key: Literal["default_text", "default_color", "default_font"]):
        if key == "default_text":
            return self._default_msg["text"]
        elif key == "default_color":
            return self._default_msg["foreground"]
        elif key == "default_font":
            return self._default_msg["font"]

    def add(self, widget: Widget, weight: int = 0):
        """
        添加一个组件，并设置其尺寸权重
        :param widget: 要添加的组件
        :param weight: 尺寸权重
        """
        widget.grid(row=0, column=len(self._widgets), sticky="nsew", padx=1)
        self.grid_columnconfigure(len(self._widgets), weight=weight)
        self._widgets.append(widget)
        self._widget_weight[str(widget)] = weight

        self._refresh_label_msg()

    # TODO 组件被移除后，会留下空隙
    def remove(self, widget: Widget):
        """
        移除一个组件
        :param widget: 要移除的组件
        """
        widget.grid_forget()

        self._widgets.remove(widget)
        del self._widget_weight[str(widget)]
        for i, w in enumerate(self._widgets):
            w.grid_configure(row=0, column=i, sticky="nsew", padx=1)
            self.grid_columnconfigure(i, weight=self._widget_weight[str(w)])

        self._refresh_label_msg()

    # TODO 组件被移除后，会留下空隙
    def clear(self):
        """
        清除所有组件
        """
        for w in filter(lambda _: str(_) != str(self.label_msg), self.grid_slaves(row=0)):
            w.grid_forget()

        self._widgets.clear()
        self._widget_weight.clear()

        self._refresh_label_msg()

    def show_message(self, text: str, timeout: int = 2000, color: Optional[str] = None, font: Union[None, tuple, Font] = None):
        """
        以特定的颜色显示消息，在指定时间后后变回默认
        :param text: 消息文本
        :param timeout: 消息滞留时间（ms）。为负数则永久滞留
        :param color: 消息文本颜色
        :param font: 消息文本字体
        """
        if self._timeout_after is not None:
            self.after_cancel(self._timeout_after)

        self.label_msg.configure(text=text, foreground=color, font=font)
        if timeout >= 0:
            self._timeout_after = self.after(timeout, lambda: self.label_msg.configure(**self._default_msg))

    def clear_message(self):
        """
        将消息变回默认
        """
        self.label_msg.configure(**self._default_msg)

    # 刷新 label_msg ，将其放置在最右边，尺寸权重设置为所有控件权重之和的三分之一。
    def _refresh_label_msg(self):
        self.label_msg.grid_configure(row=0, column=len(self._widgets), sticky="nsew", padx=1)
        self.grid_columnconfigure(len(self._widgets), weight=math.ceil((reduce(lambda _t, _s: _t + _s, self._widget_weight.values(), 0) + 1) / 3))


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    s = StatusBar(root)

    s.add(Label(s, text="1"), 1)
    l2 = Label(s, text="2")
    s.add(l2, 2)
    s.add(Label(s, text="3"), 3)

    # s.remove(l2)
    # s.clear()

    s.show_message("100", -1, font=("System", 10))
    s.pack(side="top", fill="both", expand=True)
    root.mainloop()
