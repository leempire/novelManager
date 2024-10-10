from typing import Literal
from datetime import date
from calendar import Calendar, month_name
from tkinter import Label, Button, Frame

from .limitentry import LimitEntry


class CalendarCtrl(Frame):
    """
    日历组件，继承自 tkinter.Frame，依赖 LimitEntry 组件。
    当有日期被点击时，生成 <<CalendarCtrlSelect>> 事件；当翻页时，生成 <<CalendarCtrlFlip>> 事件。
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self._now = date.today()

        # 初始化控件
        self.button_left = Button(self, text=" < ", font=("System", 10), command=lambda: self._flip("prev"))
        self.button_right = Button(self, text=" > ", font=("System", 10), command=lambda: self._flip("next"))
        self.limitentry_year = LimitEntry(self, width=4, font=("System", "10"))
        self.limitentry_year.configure_(limit_func=lambda text: int(text) >= 1)
        self.limitentry_month = LimitEntry(self, width=4, font=("System", "10"))
        self.limitentry_month.configure_(limit_func=lambda text: 1 <= int(text) <= 12)
        self.limitentry_day = LimitEntry(self, width=4, font=("System", "10"))
        self.limitentry_day.configure_(limit_func=lambda text, _=self: int(text) - 1 in list(Calendar().itermonthdays(_.now.year, _.now.month)))
        self.label_month = Label(self, font=("Helvetica", 16), anchor="center")
        self.buttons_date = [[Button(self, width=3) for _ in range(7)] for _ in range(6)]
        self.labels_week = [Label(self) for _ in range(7)]

        #  绑定事件
        self.limitentry_year.bind("<<LimitEntryMatch>>",
                                  lambda e: setattr(self, "now", date(int(self.limitentry_year.get()), self._now.month, 1)))
        self.limitentry_month.bind("<<LimitEntryMatch>>",
                                   lambda e: setattr(self, "now", date(self._now.year, int(self.limitentry_month.get()), 1)))
        self.limitentry_day.bind("<<LimitEntryMatch>>",
                                 lambda e: setattr(self, "now", date(self._now.year, self._now.month, int(self.limitentry_day.get()))))

        # 摆放控件
        self.button_left.grid(row=0, column=0)
        self.limitentry_year.grid(row=0, column=1)
        Label(self, text="/").grid(row=0, column=2)
        self.limitentry_month.grid(row=0, column=3)
        Label(self, text="/").grid(row=0, column=4)
        self.limitentry_day.grid(row=0, column=5)
        self.button_right.grid(row=0, column=6)
        self.label_month.grid(row=1, column=0, columnspan=7)
        for n, i in enumerate(["Mon", "Tue", "Wen", "Thu", "Fri", "Sat", "Sun"]):
            self.labels_week[n].configure(text=str(i))
            self.labels_week[n].grid(row=2, column=n)
        for r in range(6):
            for c in range(7):
                self.buttons_date[r][c].grid(row=3 + r, column=c, padx=2, pady=2)

        self._heavy_refresh()

    @property
    def now(self) -> date:  # 获取当前日期
        return self._now

    @now.setter
    def now(self, _date: date):  # 修改当前日期
        if (self._now.year, self._now.month) == (_date.year, _date.month):
            self._now = _date
            self._light_refresh()
        else:
            self._now = _date
            self._heavy_refresh()

    def configure_(self, top_font=None, middle_font=None, bottom_font=None):
        """
        :param top_font: 最上一栏控件的字体
        :param middle_font: 用于显示月份的文本框的字体
        :param bottom_font: 所有用于显示日期的按钮的字体
        """
        if top_font is not None:
            self.button_left.configure(font=top_font)
            self.button_right.configure(font=top_font)
            self.limitentry_year.configure(font=top_font)
            self.limitentry_month.configure(font=top_font)
            self.limitentry_day.configure(font=top_font)
        if middle_font is not None:
            self.label_month.configure(font=middle_font)
        if bottom_font is not None:
            for row in self.buttons_date:
                for button in row:
                    button.configure(font=bottom_font)
            for label in self.labels_week:
                label.configure(font=bottom_font)

    def cget_(self, key: Literal["top_font", "middle_font", "bottom_font"]):
        if key == "top_font":
            return self.button_left.cget("font")
        elif key == "middle_font":
            return self.label_month.cget("font")
        elif key == "bottom_font":
            return self.labels_week[0].cget("font")

    def _flip(self, direct: Literal["prev", "next"]):  # 翻页，生成 <<CalendarCtrlFlip>> 事件
        _month = self._now.month + {"prev": -1, "next": 1}[direct]
        if _month <= 0:
            if self.now.year >= 2:
                self.now = date(self.now.year-1, 12, 1)
        elif _month > 12:
            self.now = date(self.now.year+1, 1, 1)
        else:
            self.now = date(self.now.year, _month, 1)

        self.event_generate("<<CalendarCtrlFlip>>")

    def _heavy_refresh(self):  # 刷新控件整体
        self.limitentry_year.configure_(legal_text=f"{self._now.year}")
        self.limitentry_month.configure_(legal_text=f"{self._now.month}")
        self.limitentry_day.configure_(legal_text=f"{self._now.day}")

        self.label_month.configure(text=month_name[self._now.month])

        for row in self.buttons_date:
            for b in row:
                b.configure(text="", state="disabled", relief="flat", background="#F0F0F0")

        # itermonthdates 会迭代出不属于所需年月的日期，需要过滤掉。
        for d in filter(lambda _d: _d.month == self._now.month, Calendar(0).itermonthdates(self._now.year, self._now.month)):

            index = d.day + date(self._now.year, self._now.month, 1).weekday() - 1
            row, column = int(index / 7), index % 7
            self.buttons_date[row][column].configure(text=f" {d.day:0>2} ", state="normal", relief="raised",
                                                     command=lambda _=d: [
                                                         setattr(self, "_now", _),
                                                         self._light_refresh(),
                                                         self.event_generate("<<CalendarCtrlSelect>>")
                                                     ]
                                                     )
            if d == self._now:
                self.buttons_date[row][column].configure(background="green", foreground="white")
            else:
                self.buttons_date[row][column].configure(background="#F0F0F0", foreground="#000000")

    def _light_refresh(self):  # 刷新控件部分
        self.limitentry_day.configure_(legal_text=f"{self._now.day}")

        # itermonthdates 会迭代出不属于所需年月的日期，需要过滤掉。
        for d in filter(lambda _d: _d.month == self._now.month, Calendar(0).itermonthdates(self._now.year, self._now.month)):

            index = d.day + date(self._now.year, self._now.month, 1).weekday() - 1
            row, column = int(index / 7), index % 7

            if d == self._now:
                self.buttons_date[row][column].configure(background="green", foreground="white")
            else:
                self.buttons_date[row][column].configure(background="#F0F0F0", foreground="#000000")
