from typing import Union, Optional
from datetime import datetime, date, time
from calendar import Calendar
from tkinter import Toplevel, Button, Label, Spinbox, LabelFrame, IntVar
from tkinter.ttk import Combobox
from _tkinter import TclError


class AskDatetime:

    def __init__(self, data: Union[datetime, date, time], title: str, position: tuple[int, int], size: Optional[tuple[int, int]], if_grab: bool):
        self.data = data
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

        self.year, self.month, self.day, self.hour, self.minute, self.second = tuple(map(lambda _: _(), [IntVar]*6))

        self.labelframe_date = LabelFrame(self.root)
        self.spinbox_year = Spinbox(self.labelframe_date, from_=1, to=9999, textvariable=self.year, width=5)
        self.combobox_month = Combobox(self.labelframe_date, textvariable=self.month, state="readonly", height=12)
        self.combobox_day = Combobox(self.labelframe_date, textvariable=self.day, state="readonly", height=15)
        self.labelframe_time = LabelFrame(self.root)
        self.combobox_hour = Combobox(self.labelframe_time, textvariable=self.hour, state="readonly", height=12)
        self.spinbox_minute = Spinbox(self.labelframe_time, from_=0, to=59, textvariable=self.minute)
        self.spinbox_second = Spinbox(self.labelframe_time, from_=0, to=59, textvariable=self.second)
        self.button_submit = Button(self.root, text="Submit", command=self.submit)
        self.button_cancel = Button(self.root, text="Cancel", command=self.cancel)

    def bind(self):
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

        self.year.trace_add("write", lambda _1, _2, _3: self.refresh_day())
        self.month.trace_add("write", lambda _1, _2, _3: self.refresh_day())

    def load(self):
        if isinstance(self.data, (datetime, date)):
            self.year.set(self.data.year)
            self.month.set(self.data.month)
            self.day.set(self.data.day)
        if isinstance(self.data, (datetime, time)):
            self.hour.set(self.data.hour)
            self.minute.set(self.data.minute)
            self.second.set(self.data.second)

        if isinstance(self.data, datetime):
            pass
        elif isinstance(self.data, date):
            for widget in (self.combobox_hour, self.spinbox_minute, self.spinbox_second):
                widget.configure(state="disabled")
        elif isinstance(self.data, time):
            for widget in (self.spinbox_year, self.combobox_month, self.combobox_day):
                widget.configure(state="disabled")

        self.labelframe_date.configure(text="Date")
        self.labelframe_time.configure(text="Time")
        self.combobox_month.configure(values=tuple(range(1, 13)))
        self.combobox_hour.configure(values=tuple(range(0, 24)))

        self.labelframe_date.grid(row=0, column=0)
        Label(self.labelframe_date, text="Year:").grid(row=0, column=0, ipady=7)
        self.spinbox_year.grid(row=0, column=1)
        Label(self.labelframe_date, text="Month:").grid(row=1, column=0, ipady=7)
        self.combobox_month.grid(row=1, column=1)
        Label(self.labelframe_date, text="Day:").grid(row=2, column=0, ipady=7)
        self.combobox_day.grid(row=2, column=1)
        self.labelframe_time.grid(row=0, column=1)
        Label(self.labelframe_time, text="Hour:").grid(row=0, column=0, ipady=7)
        self.combobox_hour.grid(row=0, column=1)
        Label(self.labelframe_time, text="Minute(0~59):").grid(row=1, column=0, ipady=7)
        self.spinbox_minute.grid(row=1, column=1)
        Label(self.labelframe_time, text="Second(0~59):").grid(row=2, column=0, ipady=7)
        self.spinbox_second.grid(row=2, column=1)

        self.button_submit.grid(row=1, column=0)
        self.button_cancel.grid(row=1, column=1)

    def start(self):
        self.load()
        self.bind()

        self.refresh_day()

        self.root.focus_set()
        self.root.mainloop()
        return self.result

    def stop(self):
        self.root.quit()
        self.root.destroy()

    def submit(self):
        try:
            if isinstance(self.data, datetime):
                self.result = datetime(self.year.get(), self.month.get(), self.day.get(),
                                       self.hour.get(), self.minute.get(), self.second.get(), 0)
            elif isinstance(self.data, date):
                self.result = date(self.year.get(), self.month.get(), self.day.get())
            elif isinstance(self.data, time):
                self.result = time(self.hour.get(), self.minute.get(), self.second.get(), 0)

        except (ValueError, TclError):
            self.result = None

        self.stop()

    def cancel(self):
        self.result = None
        self.stop()

    def refresh_day(self):  # 根据 spinbox_year 和 combox_month 中的内容，刷新 combox_day 中的可选项
        if isinstance(self.data, time):  # 当 date 部分不起作用时，直接返回。
            return

        try:
            _year = self.year.get()
            _month = self.month.get()
            _day = self.day.get()
            legal_days = tuple(
                    map(lambda __d: __d.day,
                        filter(
                            lambda _d: _d.month == _month, Calendar(0).itermonthdates(_year, _month))
                        )
                )
            if _day not in legal_days:  # 如果当前 combobox_day 的内容不合法，则置为1
                self.day.set(1)
            self.combobox_day.configure(values=tuple(map(lambda _: str(_), legal_days)))  # 刷新 combobox_day 中的选项
        except TclError:
            self.day.set(1)
            self.combobox_day.configure(values=())


def askdatetime(data: Union[datetime, date, time], title: str, position: tuple[int, int], size: Optional[tuple[int, int]] = None,
                if_grab: bool = False) -> Union[datetime, date, time, None]:
    """
    弹出编辑日期或时间的窗口，返回编辑后的日期，时间或None。
    self.data 的数据类型和返回值（除了None）的数据类型相同。
    返回 None 代表用户没有 submit，或编辑的日期或时间数值不合法.
    :param data: 被编辑的日期或时间，可以是 datetime, date, time
    :param title: 窗口标题
    :param position: 窗口左上角相对全屏幕的位置
    :param size: 窗口大小，如省略则由系统自动设置
    :param if_grab: 本窗口是否阻断其他所有窗口
    :return: 编辑后的日期，时间或None
    """
    return AskDatetime(data, title, position, size, if_grab).start()


if __name__ == "__main__":
    print(askdatetime(datetime(2024, 7, 4, 11, 59, 30), "AskDatetime", (500, 250)))
