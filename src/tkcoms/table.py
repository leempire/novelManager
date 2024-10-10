from typing import Callable, Union, Literal, Any, Optional
from tkinter.ttk import Treeview, Style
from tkinter.font import Font


class Table(Treeview):
    """
    表格组件，继承自 tkinter.ttk.Treeview
    本控件内部绑定 <Button-1> <Up> <Down> <Left> <Right> 事件。
    当左键单击单元格或表头 或 按下键盘方向键切换选中的单元格或表头 时，生成 <<TableSelect>> 事件。
    """
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._position: tuple[int, int] = (-1, -1)  # 当前被选中的位置

        self.configure(show="tree headings", selectmode="none", style=f"{str(self)}.Treeview")
        self.column("#0", width=80, minwidth=60, stretch=False, anchor="w")
        self.heading("#0", anchor="center")

        self.tag_configure("odd", background="#E7E7E7")  # 设置奇数行标签
        self.tag_configure("even", background="#FFFFFF")  # 设置偶数行标签

        self._history = []  # 操作记录
        self._history_cur = 0  # 操作记录指针

        self._heading_args = {"anchor": "center"}  # 用于设置除第零列以外所有列 heading 函数的参数
        self._column_args = {"minwidth": 60, "anchor": "w", "stretch": False}  # 用于设置除第零列以外所有列 column 函数的参数

        self.bind("<Button-1>", self._on_button_left)
        self.bind("<Up>", self._on_direct)
        self.bind("<Down>", self._on_direct)
        self.bind("<Left>", self._on_direct)
        self.bind("<Right>", self._on_direct)

    # 点击鼠标左键，选中单元格或者表头
    def _on_button_left(self, e):
        x, y = e.x, e.y
        index_row = self.identify_row(y)
        index_col = self.identify_column(x)
        kind = self.identify_region(x, y)
        if kind == "cell":  # 点击了单元格
            pos = (self.get_children().index(index_row) + 1, int(index_col[1:]))
        elif kind == "heading":  # 如果点击了表头
            pos = (0, int(index_col[1:]))
        elif kind == "tree":  # 如果点击了第零列
            pos = (self.get_children().index(index_row) + 1, 0)
        else:  # 如果点击了列分割符或什么也没点击到
            pos = (-1, -1)

        self.position = pos  # 选中点击的位置
        self.event_generate("<<TableSelect>>")  # 生成事件

    # 按下键盘上的方向键，移动当前选中的单元格或表头
    def _on_direct(self, e):
        next_pos = (self.position[0]+{"Left": 0, "Right": 0, "Up": -1, "Down": 1}[e.keysym],
                    self.position[1]+{"Left": -1, "Right": 1, "Up": 0, "Down": 0}[e.keysym])

        if 0 <= next_pos[0] <= self.table_size[0] and 0 <= next_pos[1] <= self.table_size[1]:
            self.position = next_pos
            self.event_generate("<<TableSelect>>")

    @property
    def position(self) -> tuple[int, int]:
        """返回选中位置的索引"""
        return self._position

    @position.setter
    def position(self, pos: tuple[int, int]):
        """选中索引对应的位置"""

        self.selection_remove(self.get_children(""))
        for i in self.cget("column"):
            self.heading(i, text=str(i))

        if 1 <= pos[0] <= self.table_size[0] and 1 <= pos[1] <= self.table_size[1]:  # 两个索引都大于等于1 表示选中了单元格
            self.selection_add(self.get_children("")[pos[0] - 1])
            self.heading(pos[1], text=f"##{pos[1]}##", **self._heading_args)
        elif pos[0] == 0 and pos[1] > 0:  # 行索引等于0 表示选中了表头
            self.heading(pos[1], text=f"##{pos[1]}##", **self._heading_args)
        elif pos[0] > 0 and pos[1] == 0:  # 列索引等于0 表示选中了第零列
            self.selection_add(self.get_children("")[pos[0] - 1])
        elif pos[0] == 0 and pos[1] == 0:  # 两个索引都等0 表示选中了左上角的格子
            pass
        else:  # 其他情况，索引不属于表格
            pos = (-1, -1)

        self._position = pos

    @property
    def table_size(self) -> tuple[int, int]:
        """获取表格的大小"""
        return len(self.get_children("")), len(self.cget("column"))

    def configure_(self, yscrollcommand: Callable = None, xscrollcommand: Callable = None,
                   rowheight: float = None, font: Union[Font, tuple] = None, zero_text: Optional[str] = None,
                   minwidth: int = None, anchor: Literal['w', 'center', 'e'] = None, stretch: bool = None,
                   head_anchor: Literal['w', 'center', 'e'] = None):
        """
        :param yscrollcommand: 纵向滚动的回调函数，用于绑定滚动条
        :param xscrollcommand: 横向滚动的回调函数，用于绑定滚动条
        :param rowheight: 每一行的行高
        :param font: 字体
        :param zero_text: 第0行第0列单元格的文本
        :param minwidth: 每一列的最小宽度
        :param anchor: 所有单元格文字的对齐方式
        :param stretch: 是否让每一列的宽度可以调整
        :param head_anchor: 所有表头文字的对齐方式
        """
        flag = False
        if yscrollcommand is not None:
            self.configure(yscrollcommand=yscrollcommand)
        if xscrollcommand is not None:
            self.configure(xscrollcommand=xscrollcommand)
        if rowheight is not None:
            Style().configure(self.cget("style"), rowheight=rowheight)
        if font is not None:
            Style().configure(self.cget("style"), font=font)
            Style().configure(f"{self.cget("style")}.Heading", font=font)
        if zero_text is not None:
            self.heading("#0", text=zero_text)
        if minwidth is not None:
            self._column_args["minwidth"] = minwidth
            flag = True
        if anchor is not None:
            self._column_args["anchor"] = anchor
            flag = True
        if stretch is not None:
            self._column_args["stretch"] = stretch
            flag = True
        if head_anchor is not None:
            flag = True
            self._heading_args["anchor"] = head_anchor

        if flag:
            for i in range(1, self.table_size[1]):
                self.heading(str(i), **self._heading_args)
                self.column(str(i), **self._column_args)

    def cget_(self, key: Literal["rowheight", "font", "zero_text", "minwidth", "anchor", "stretch", "head_anchor"]):
        if key == "rowheight":
            return Style().configure(self.cget("style"), "rowheight")
        elif key == "font":
            return Style().configure(self.cget("style"), "font")
        elif key == "zero_text":
            return self.heading("#0", "text")
        elif key == "minwidth":
            return self._column_args["minwidth"]
        elif key == "anchor":
            return self._column_args["anchor"]
        elif key == "stretch":
            return self._column_args["stretch"]
        elif key == "head_anchor":
            return self._heading_args["anchor"]

    def row(self, r: int, items: Union[None, list, tuple] = None, record: bool = True):
        size = self.table_size
        if r < 1 or r > size[0]:  # 检查索引越界
            raise ValueError

        if items is None:  # 如果不设置items参数，则返回索引所在行
            t_items = list(self.item(self.get_children("")[r - 1], "values"))

            if len(t_items) >= self.table_size[1]:
                return t_items[:self.table_size[1]]
            else:
                return t_items + ["" for _ in range(size[1] - len(t_items))]
        else:  # 如果设置了items参数，则根据items设置索引所在行
            if record:  # 操作记录
                self._history = self._history[:self._history_cur]
                self._history.append(["row_set", r, items, self.row(r)])
                self._history_cur += 1

            items = list(items)
            if len(items) > size[1]:
                items = items[:size[1]]
            self.item(self.get_children("")[r - 1], values=items)

    def col(self, c: int, items: Union[None, list, tuple] = None, record: bool = True):
        size = self.table_size
        if c < 1 or c > size[1]:  # 检查索引越界
            raise ValueError

        if items is None:  # 如果不设置items参数，则返回索引所在列
            t_items = []
            for i in range(1, size[0] + 1):
                t_items.append(self.row(i)[c - 1])
            return t_items
        else:  # 如果设置了items参数，则根据items设置索引所在列
            if record:  # 操作记录
                self._history = self._history[:self._history_cur]
                self._history.append(["col_set", c, items, self.col(c)])
                self._history_cur += 1

            items = list(items)
            if len(items) < size[0]:
                items += ["" for _ in range(size[0] - len(items))]
            for i in range(1, 1 + size[0]):
                t = self.row(i)
                t[c - 1] = items[i - 1]
                self.row(i, t, record=False)

    def cell(self, r: int, c: int, item: Union[None, Any] = None, record: bool = True):
        size = self.table_size
        if r < 1 or r > size[0] or c < 1 or c > size[1]:  # 检查索引越界
            raise ValueError

        if item is None:  # 如果不设置item参数，则返回索引所在单元的元素
            return self.row(r)[c - 1]
        else:  # 如果设置了item参数，则根据item设置索引所在单元
            if record:  # 操作记录
                self._history = self._history[:self._history_cur]
                self._history.append(["cell_set", c, r, item, self.row(r)[c - 1]])
                self._history_cur += 1

            t = self.row(r)
            t[c - 1] = str(item)
            self.row(r, t, record=False)

    def add_row(self, r: Optional[int] = None, items: Union[None, list, tuple] = None, record: bool = True):  # 根据索引增加一行，默认增加到最后一行
        size = self.table_size

        if r is None:
            r = size[0]

        if (r < 0) or (r > size[0]):  # 检查越界
            raise ValueError

        if record:  # 操作记录
            self._history = self._history[:self._history_cur]
            self._history.append(["row_add", r, items])
            self._history_cur += 1

        if r % 2:
            index = self.insert("", r, text=str(r + 1), tags="odd")
        else:
            index = self.insert("", r, text=str(r + 1), tags="even")
        for j, i in enumerate(self.get_children("")[r + 1:]):
            if (j + r + 2) % 2:
                self.item(i, text=str(j + r + 2), tags="even")
            else:
                self.item(i, text=str(j + r + 2), tags="odd")
        if items is None:
            self.item(index, values=["" for _ in range(size[1])])
        else:
            self.item(index, values=items[:size[1] + 1])

    def add_col(self, c: Optional[int] = None, items: Union[None, list, tuple] = None, record: bool = True):  # 根据索引增加一列，默认增加到最后一列
        size = self.table_size

        if c is None:
            c = size[1]

        if (c < 0) or (c > size[1]):
            raise ValueError

        if record:  # 操作记录
            self._history = self._history[:self._history_cur]
            self._history.append(["col_add", c, items])
            self._history_cur += 1

        self.config(columns=list(self.cget("columns")) + [str(size[1] + 1)])
        for i in range(size[1] + 1):
            self.heading(str(i + 1), text=str(i + 1), **self._heading_args)
            self.column(str(i + 1), **self._column_args)
        if items is not None:
            if len(items) < size[0]:
                items = list(items) + ["" for _ in range(size[0] - len(items))]
            for i in range(size[0]):
                t_items = self.row(i + 1)
                t_items.insert(c, items[i - 1])
                self.row(i + 1, t_items, record=False)
        else:
            for i in range(size[0]):
                t_items = self.row(i + 1)
                t_items.insert(c, "")
                self.row(i + 1, t_items, record=False)

    def del_row(self, r: int, record=True):  # 删除某一行
        size = self.table_size
        if r < 1 or r > size[0] or size[0] == 0:  # 检查索引越界，检查是否有行可供删除
            raise ValueError

        if record:  # 操作记录
            self._history = self._history[:self._history_cur]
            self._history.append(["row_del", r, self.row(r)])
            self._history_cur += 1

        if r == self.position[0]:  # 删除的是当前选中的行
            self.position = -1, self.position[1]

        self.delete(self.get_children("")[r - 1])
        for j, i in enumerate(self.get_children("")[r - 1:]):
            if (j + r) % 2:
                self.item(i, text=str(j + r), tags="even")
            else:
                self.item(i, text=str(j + r), tags="odd")

    def del_col(self, c: int, record=True):  # 删除某一列
        size = self.table_size
        if c < 1 or c > size[1] or size[1] == 0:  # 检查索引越界，检查是否有列可删除
            raise ValueError

        if record:  # 操作记录
            self._history = self._history[:self._history_cur]
            self._history.append(["col_del", c, self.col(c)])
            self._history_cur += 1

        if c == self.position[1]:  # 删除的是当前选中的列
            self.position = self.position[0], -1

        for i in range(size[0]):
            t_items = self.row(i + 1)
            t_items.pop(c - 1)
            self.row(i + 1, t_items, record=False)
        self.config(columns=list(self["columns"])[:-1])
        for i in range(size[1] - 1):
            self.heading(str(i + 1), text=str(i + 1), **self._heading_args)
            self.column(str(i + 1), **self._column_args)

    def clear(self):  # 清空表格
        self.delete(*self.get_children(""))
        self.config(columns=[])

    def undo(self):  # 撤销上一个操作
        if self._history_cur <= 0:  # 检查操作指针是否已经移动到栈底
            return True

        do = self._history[self._history_cur - 1]  # 移动指针
        self._history_cur -= 1

        if do[0] == "row_set":
            self.row(do[1], do[3], record=False)
        elif do[0] == "col_set":
            self.col(do[1], do[3], record=False)
        elif do[0] == "cell_set":
            self.cell(do[1], do[2], do[4], record=False)
        elif do[0] == "row_add":
            self.del_row(do[1] + 1, record=False)
        elif do[0] == "col_add":
            self.del_col(do[1] + 1, record=False)
        elif do[0] == "row_del":
            self.add_row(do[1] - 1, do[2], record=False)
        elif do[0] == "col_del":
            self.add_col(do[1] - 1, do[2], record=False)

        return False

    def redo(self):  # 重做操作
        if self._history_cur >= len(self._history):  # 检查操作指针是否移动到栈顶
            return True

        do = self._history[self._history_cur]  # 移动指针
        self._history_cur += 1

        if do[0] == "row_set":
            self.row(do[1], do[2], record=False)
        elif do[0] == "col_set":
            self.col(do[1], do[2], record=False)
        elif do[0] == "cell_set":
            self.cell(do[1], do[2], do[3], record=False)
        elif do[0] == "row_add":
            self.add_row(do[1], do[2], record=False)
        elif do[0] == "col_add":
            self.add_col(do[1], do[2], record=False)
        elif do[0] == "row_del":
            self.del_row(do[1], record=False)
        elif do[0] == "col_del":
            self.del_col(do[1], record=False)

        return False

    def reset(self):  # 清空操作记录
        self._history = []
        self._history_cur = 0

    def modified(self):  # 获取表格是否被变更过
        if self._history:
            if self._history_cur == 0:
                return False
            else:
                return True
        else:
            return False
