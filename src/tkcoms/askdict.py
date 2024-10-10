from typing import Union, Optional
from tkinter import Toplevel, Frame, Label, Entry, Button, StringVar
from tkinter.ttk import Combobox
from tkinter.scrolledtext import ScrolledText
from enum import Enum
import copy

from .listframe import ListFrame


class _IntEntry(Entry):

    def __init__(self, master, data: dict, key: str):
        super().__init__(master)

        self.data = data
        self.key = key

        self.var = StringVar()
        self.var.set(str(self.data[self.key]))
        self.configure(textvariable=self.var)
        self.var.trace_add("write", self.on_change)
        self.bind("<Return>", self.on_return)

    def on_change(self, *args):
        text = self.get()
        if text == str(self.data[self.key]):
            self.configure(fg="black")
        else:
            self.configure(fg="red")

    def on_return(self, e):
        text = self.var.get()
        try:
            self.data[self.key] = int(text)
        except ValueError:
            pass
        self.var.set(str(self.data[self.key]))


class _FloatEntry(Entry):

    def __init__(self, master, data: dict, key: str):
        super().__init__(master)

        self.data = data
        self.key = key

        self.var = StringVar()
        self.var.set(str(self.data[self.key]))
        self.configure(textvariable=self.var)
        self.var.trace_add("write", self.on_change)
        self.bind("<Return>", self.on_return)

    def on_change(self, *args):
        text = self.get()
        if text == str(self.data[self.key]):
            self.configure(fg="black")
        else:
            self.configure(fg="red")

    def on_return(self, e):
        text = self.var.get()
        try:
            self.data[self.key] = float(text)
        except ValueError:
            pass
        self.var.set(str(self.data[self.key]))


class _StrEntry(Entry):

    def __init__(self, master, data: dict, key: str):
        super().__init__(master)

        self.data = data
        self.key = key

        self.var = StringVar()
        self.var.set(str(self.data[self.key]))
        self.configure(textvariable=self.var)
        self.var.trace_add("write", self.on_change)

    def on_change(self, *args):
        text = self.var.get()
        self.data[self.key] = text


class _BoolCombobox(Combobox):

    def __init__(self, master, data: dict, key: str):
        super().__init__(master)

        self.data = data
        self.key = key

        self.set({True: "True", False: "False"}[self.data[self.key]])
        self.configure(state="readonly", values=("True", "False"))
        self.bind("<<ComboboxSelected>>", self.on_select)

    def on_select(self, e):
        text = self.get()
        if text == "True":
            self.data[self.key] = True
        elif text == "False":
            self.data[self.key] = False


class _EnumCombobox(Combobox):

    def __init__(self, master, data: dict, key: str):
        super().__init__(master)

        self.data = data
        self.key = key

        self.set(self.data[key].name)
        self.configure(state="readonly", values=[_.name for _ in list(type(self.data[key]))])
        self.bind("<<ComboboxSelected>>", self.on_select)

    def on_select(self, e):
        text = self.get()
        self.data[self.key] = getattr(type(self.data[self.key]), text)


class _StrScrolledText(ScrolledText):

    def __init__(self, master, data: dict, key: str):
        super().__init__(master)

        self.data = data
        self.key = key

        self.insert("end", self.data[key])
        line_n = self.data[key].count("\n") + 2
        self.configure(wrap="word", height=line_n if line_n <= 10 else 10)
        self.bind("<KeyRelease>", self.on_change)
        self.bind("<FocusOut>", self.on_change)

    def on_change(self, e):
        self.data[self.key] = self.get(1.0, "end-1c")


class AskDict:

    def __init__(self, data: dict[str, Union[int, float, str, bool, Enum]], title: str, length: int, position: tuple[int, int],
                 size: Optional[tuple[int, int]], if_grab: bool):
        super().__init__()

        self.data = copy.deepcopy(data)
        self.result = None

        self.root = Toplevel()
        self.root.title(title)

        if if_grab:
            self.root.grab_set()
        else:
            self.root.grab_release()

        if size is not None:
            self.root.geometry("{}x{}+{}+{}".format(size[0], size[1], position[0], position[1]))
        else:
            self.root.geometry("+{}+{}".format(position[0], position[1]))

        self.listframe = ListFrame(self.root)
        self.listframe.configure_(length=length)
        self.init_listframe()  # 初始化要显示在 listframe 里的控件
        self.frame_bottom = Frame(self.root)
        self.button_submit = Button(self.frame_bottom, text="Submit", command=self.submit)
        self.button_cancel = Button(self.frame_bottom, text="Cancel", command=self.cancel)

    def init_listframe(self):
        for key in self.data:
            # 初始化框架
            frame = Frame(self.listframe)
            #  初始化用于显示键和变量类型的 Label
            label = Label(frame, text=f"Key: {key} | Type: {type(self.data[key]).__name__}", anchor="w")
            #  根据不同变量类型初始化输入控件
            if isinstance(self.data[key], bool):  # 当变量类型为 bool 时
                input_widget = _BoolCombobox(frame, self.data, key)
            elif isinstance(self.data[key], int):  # 当变量类型为 int 时
                input_widget = _IntEntry(frame, self.data, key)
            elif isinstance(self.data[key], float):  # 当变量类型为 float 时
                input_widget = _FloatEntry(frame, self.data, key)
            elif isinstance(self.data[key], str):  # 当变量类型为 str 时
                if "\n" not in self.data[key]:  # 单行字符串
                    input_widget = _StrEntry(frame, self.data, key)
                else:  # 多行字符串
                    input_widget = _StrScrolledText(frame, self.data, key)
            elif isinstance(self.data[key], Enum):  # 当变量类型为 Enum 时
                input_widget = _EnumCombobox(frame, self.data, key)
            else:
                raise TypeError

            # 把标签和输入控件放入框架
            label.pack(side="top", fill="x", expand=True)
            input_widget.pack(side="bottom", fill="x", expand=True)

            # 把框架放入 ListFrame
            self.listframe.append(frame)

    def bind(self):
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def load(self):
        self.listframe.pack(side="top", fill="both", expand=True)
        self.frame_bottom.pack(side="bottom", fill="x")
        self.frame_bottom.grid_columnconfigure(0, weight=1)
        self.frame_bottom.grid_columnconfigure(1, weight=1)
        self.button_submit.grid(row=0, column=0)
        self.button_cancel.grid(row=0, column=1)

    def start(self):
        self.bind()
        self.load()

        self.root.focus_set()
        self.root.mainloop()
        return self.result

    def stop(self):
        self.root.quit()
        self.root.destroy()

    def submit(self):
        self.result = self.data
        self.stop()

    def cancel(self):
        self.result = None
        self.stop()


def askdict(data: dict[str, Union[int, float, str, bool, Enum]], title: str, length: int, position: tuple[int, int],
            size: Optional[tuple[int, int]] = None, if_grab: bool = False) -> Optional[dict]:
    """
    弹出编辑字典的窗口，返回编辑后的字典或 None。依赖 ListFrame 组件。
    字典的键必须实现 __str__() 魔术方法，字典的值必须为 str,int,float,bool,Enum 五种数据类型。
    :param data: 原字典
    :param title: 窗口标题
    :param length: 列表显示的条目数量
    :param position: 窗口左上角位置
    :param size: 窗口大小，默认为 None，即由系统自动设置
    :param if_grab: 本窗口是否阻断其他所有窗口
    :return: 编辑后的字典或 None
    """
    return AskDict(data, title, length, position, size, if_grab).start()


if __name__ == "__main__":
    print(askdict({"1": 12, "2": True, "3": "Hello World", "4": "Hello,World\n"}, "AskDict", 3, (500, 250)))
