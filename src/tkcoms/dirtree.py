from typing import Optional, Union, Literal
from tkinter import Frame, Scrollbar, Entry
from tkinter.ttk import Treeview, Style
from tkinter.font import Font
from pathlib import Path


class DirTree(Frame):
    """
    文件树组件，继承自 tkinter.Frame
    当双击鼠标左键 时，生成 <<DirTreeChoose>> 事件。
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.chosen_path: Optional[Path] = None  # 被选中的路径

        self._id_path = {}  # 树中元素的id对应路径的字典

        # 初始化控件
        self.frame_bottom = Frame(self)
        self.tree = Treeview(self.frame_bottom)
        self.scroll = Scrollbar(self.frame_bottom, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scroll.set, show="tree", style=f"{str(self.tree)}.Treeview")
        self.entry = Entry(self)

        # 绑定事件
        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<<TreeviewClose>>", self._on_close)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-Button-1>", lambda e: self.event_generate("<<DirTreeChoose>>"))

        # 摆放控件
        self.entry.pack(side="top", fill="x")
        self.frame_bottom.pack(side="top", fill="both", expand=True)
        self.tree.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="left", fill="y")

    def _on_open(self, e):
        parent = self.tree.focus()
        if not self._id_path[parent].is_dir():
            return

        self.tree.delete(*self.tree.get_children(parent))
        try:
            for p in self._id_path[parent].iterdir():
                id_ = self.tree.insert(parent, "end", text=p.name)
                self._id_path[id_] = p
        except PermissionError:
            pass

    def _on_close(self, e):
        parent = self.tree.focus()
        self.tree.delete(*self.tree.get_children(parent))
        self.tree.insert(parent, "end", text="none")

    def _on_select(self, e):
        self.chosen_path = self._id_path[self.tree.focus()]
        self.entry.delete(0, "end")
        self.entry.insert("end", self.chosen_path)

    def configure_(self, tree_font: Union[Font, tuple, None] = None, entry_font: Union[Font, tuple, None] = None):
        """
        :param tree_font: 设置文件夹树的字体
        :param entry_font: 设置显示路径的文本框的字体
        """
        if tree_font is not None:
            Style().configure(self.tree.cget("style"), font=tree_font)
        if entry_font is not None:
            self.entry.config(font=entry_font)

    def cget_(self, key: Literal["tree_font", "entry_font"]):
        if key == "tree_font":
            return Style().configure(self.tree.cget("style"), "font")
        elif key == "entry_font":
            self.entry.cget("font")

    def chdir(self, path: Union[Path, str]):
        """
        修改文件树的根目录
        """
        self.entry.delete(0, "end")
        self.entry.insert(0, str(Path(path)))
        self.chosen_path = Path(path)
        self.tree.delete(*self.tree.get_children(""))
        try:
            for p in Path(path).iterdir():
                if p.is_file():
                    id_ = self.tree.insert("", "end", text=p.name)
                    self._id_path[id_] = p

                elif p.is_dir():
                    id_ = self.tree.insert("", "end", text=p.name)
                    self._id_path[id_] = p
                    self.tree.insert(id_, "end", text="none")

        except PermissionError:
            pass
