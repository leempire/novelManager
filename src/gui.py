from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.font import Font


class Window:
    """

    """

    labelWidth = (14, 10, 6, 6)
    buttonNum = 3

    def __init__(self, color):
        self.focused = False
        self.entry_focused = False
        self._color(color)
        self.root = self._gui()

    def _color(self, n):
        fg = ['#fb5c00', '#bbbbbb', 'black', '#FF00FF']
        bg = ['#ffe7d7', '#3c3f41', 'whitesmoke', '#00CED1']
        self.bg_color = bg[n]
        self.fg_color = fg[n]

    def _gui(self):
        root = Tk()
        root.bind('<FocusIn>', lambda x: self.focus_set(True))
        root.bind('<FocusOut>', lambda x: self.focus_set(False))

        font = Font(family="楷体", size=14)
        root.tk_setPalette(background=self.bg_color, foreground=self.fg_color)
        root.title('iChat播放器')
        self._pack_menu(root)
        body = Frame(root)

        # 搜索框
        top = Frame(body)
        self.entry = Entry(top)
        self.entry.pack(side=LEFT, padx=2)
        self.entry.bind('<Return>', lambda x: self.top_cmd(0))
        self.entry.bind('<FocusIn>', lambda x: self.entry_focus_set(True))
        self.entry.bind('<FocusOut>', lambda x: self.entry_focus_set(False))
        Button(top, text='搜索', command=lambda: self.top_cmd(0), font=font).pack(side=LEFT, padx=2)
        # Button(top, text='添加', command=lambda: self.top_cmd(1), font=font).pack(side=LEFT, padx=2)
        top.pack(pady=5)
        # 歌曲列表
        mid = Frame(body)
        self.list = []
        self.buttons = []
        for i in range(11):
            line = Frame(mid)

            self.list.append([])
            for width in self.labelWidth:
                t = StringVar()
                label = Label(line, anchor='w', width=width, textvariable=t, relief='solid', borderwidth=1, font=font)
                label.pack(side=LEFT, padx=2)
                self.list[-1].append(t)

            self.buttons.append([])
            for j in range(self.buttonNum):
                t = StringVar()
                button = Button(line, textvariable=t, command=lambda n=(j, i): self.mid_cmd(*n), font=font, width=4)
                button.pack(side=LEFT, padx=2)
                self.buttons[-1].append(t)
            line.pack(pady=2)
        mid.pack(pady=5)
        # 翻页
        bot = Frame(body)
        Button(bot, text='上一页', command=lambda: self.bot_cmd(0), font=font).pack(side=LEFT)
        self.page = StringVar(value='1 / 1')
        Label(bot, textvariable=self.page, font=font).pack(side=LEFT, padx=5)
        Button(bot, text='下一页', command=lambda: self.bot_cmd(1), font=font).pack(side=LEFT)
        bot.pack(pady=5)

        body.pack()
        return root

    def _pack_menu(self, root):
        # 菜单
        menu_root = Menu(root)
        menu_root.option_add('*font', ('楷体', 12))
        # 第一栏 模式选择
        menu_0 = Menu(menu_root, tearoff=0)
        menu_0.add_command(label='书架', command=lambda: self.menu_cmd((0, 0)))
        menu_0.add_command(label='书城', command=lambda: self.menu_cmd((0, 1)))
        menu_root.add_cascade(label='模式', menu=menu_0)
        # # 第二栏 歌单选择
        # menu_1 = Menu(menu_root, tearoff=0)
        # for i in range(5):
        #     menu_1.add_command(label=f'歌单{i + 1}', command=lambda n=i: self.menu_cmd((1, n)))
        # menu_root.add_cascade(label='歌单', menu=menu_1)
        # # 第三栏 配色
        # menu_2 = Menu(menu_root, tearoff=0)
        # menu_2.add_command(label='活力橙', command=lambda: self.menu_cmd((2, 0)))
        # menu_2.add_command(label='暗夜黑', command=lambda: self.menu_cmd((2, 1)))
        # menu_2.add_command(label='经典白', command=lambda: self.menu_cmd((2, 2)))
        # menu_2.add_command(label='靛紫青', command=lambda: self.menu_cmd((2, 3)))
        # menu_root.add_cascade(label='配色', menu=menu_2)
        # # 第四栏 榜单
        # menu_3 = Menu(menu_root, tearoff=0)
        # menu_3.add_command(label='热歌榜', command=lambda: self.menu_cmd((3, 0)))
        # menu_3.add_command(label='原创榜', command=lambda: self.menu_cmd((3, 1)))
        # menu_3.add_command(label='新歌榜', command=lambda: self.menu_cmd((3, 2)))
        # menu_3.add_command(label='飙升榜', command=lambda: self.menu_cmd((3, 3)))
        # menu_root.add_cascade(label='榜单', menu=menu_3)
        # # 第五栏 一起听歌
        # menu_4 = Menu(menu_root, tearoff=0)
        # menu_4.add_command(label='加入', command=lambda: self.menu_cmd((4, 0)))
        # menu_4.add_command(label='退出', command=lambda: self.menu_cmd((4, 1)))
        # menu_4.add_command(label='主持', command=lambda: self.menu_cmd((4, 2)))
        # menu_root.add_cascade(label='云听歌', menu=menu_4)
        # # 第六栏 其他操作
        # menu_5 = Menu(menu_root, tearoff=0)
        # menu_5.add_command(label='全部添加', command=lambda: self.menu_cmd((5, 0)))
        # menu_5.add_command(label='全部删除', command=lambda: self.menu_cmd((5, 1)))
        # menu_5.add_command(label='操作指南', command=lambda: self.menu_cmd((5, 2)))
        # menu_5.add_command(label='导出当前', command=lambda: self.menu_cmd((5, 3)))
        # menu_5.add_command(label='快捷方式', command=lambda: self.menu_cmd((5, 4)))
        # menu_5.add_command(label='省流模式', command=lambda: self.menu_cmd((5, 5)))
        # menu_root.add_cascade(label='其他', menu=menu_5)

        root.config(menu=menu_root)

    def run(self):
        self.root.mainloop()

    def focus_set(self, t):
        self.focused = t

    def entry_focus_set(self, t):
        self.entry_focused = t

    def get_focused(self):
        return self.focused

    def get_entry_focused(self):
        return self.entry_focused

    def get_entry(self):
        return self.entry.get()

    def set_head(self, content):
        for i in range(len(self.labelWidth)):
            self.list[0][i].set(content[i])

    def set_list(self, content, index=-1):
        if index == -1:
            for i in range(10):
                if i < len(content):
                    self.set_list(content[i], i)
                else:
                    self.set_list([''] * len(self.labelWidth), i)
        else:
            for i in range(len(self.labelWidth)):
                self.list[index + 1][i].set(content[i])

    def set_button(self, content):
        for row in self.buttons[1:]:
            for i in range(len(row)):
                row[i].set(content[i])

    def set_page(self, now, total):
        if not now:
            now = 1
        if not total:
            total = 1
        self.page.set(f'{str(now).ljust(2, " ")}/{str(total).rjust(2, " ")}')

    def menu_cmd(self, d):
        ...

    def top_cmd(self, d):
        ...

    def mid_cmd(self, action, index):
        ...

    def bot_cmd(self, d):
        ...
        ...


if __name__ == '__main__':
    Window(0).run()
