from typing import Callable, Optional, Literal
from tkinter import Entry, StringVar


class LimitEntry(Entry):
    """
    受限制的输入框组件，继承自 tkinter.Entry
    本控件内部绑定自身的 <Return> 事件。
    当回车键被点击时，如果检测通过，则生成 <<LimitEntryMatch>> 事件。
    （本控件依赖 StringVar 来检测内容变化，请勿随意改变 textvariable 属性）
    """
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self._limit_func: Callable[[str], bool] = lambda text: True
        self._var = StringVar()
        self._legal_text = ""  # 当前文本框所存储的合法字符串

        self.configure(textvariable=self._var)
        self._var.trace_add("write", self._on_trace_write)

        self.bind("<Return>", self._on_return)

    # 当框中文本相对上一次通过检测时有变化时，修改文本颜色
    def _on_trace_write(self, *args):
        text = self.get()
        if text != self._legal_text:
            self.config(foreground="red")
        else:
            self.config(foreground="black")

    # 单击回车时，检测框里的文本，如果未通过检测，则回滚文本。如果通过检测，则视参数生成一个 <<LimitEntryMatch>> 事件
    def _on_return(self, e):
        text = self.get()
        try:
            if self._limit_func(text):
                self._legal_text = text
                self.event_generate("<<LimitEntryMatch>>")
        except Exception:
            pass

        self.delete(0, "end")
        self.insert("end", self._legal_text)

    def configure_(self, limit_func: Callable[[str], bool] = None, legal_text: Optional[str] = None):
        """
        :param limit_func: 用于限制内容的函数，接受被检测的内容字符串。返回值为True时字符串检测成功，返回False或抛出异常时检测不成功，内容回滚。
        :param legal_text: 设置当前存储的合法文本。该文本必须能通过 limit_func 检测，否则设置无效。
        """
        if limit_func is not None:
            self._limit_func = limit_func
        if legal_text is not None:
            try:
                if self._limit_func(legal_text):
                    self._legal_text = legal_text
                    self.delete(0, "end")
                    self.insert(0, legal_text)
            except Exception:
                pass

    def cget_(self, key: Literal["limit_func", "legal_text"]):
        if key == "limit_func":
            return self._limit_func
        elif key == "legal_text":
            return self._legal_text
