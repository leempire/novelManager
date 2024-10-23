# GUI模式的控制文件

from tkinter import *
from tkinter.font import Font

def askQuestion(title, message, button_texts):
    root = Tk()
    root.withdraw()
    top = Toplevel(root)
    top.title(title)
    Label(top, text=message).pack()
    result = None
    def set_result(text):
        nonlocal result
        result = text
        top.destroy()
        root.destroy()
    button1 = Button(top, text=button_texts[0], command=lambda: set_result(button_texts[0]))
    button1.pack(side=LEFT)
    button2 = Button(top, text=button_texts[1], command=lambda: set_result(button_texts[1]))
    button2.pack(side=RIGHT)
    top.wait_window()
    return result


class Window:
    """
    属性：
    labelWidth = (int, ...)
    lineNum = int
    buttonNum = int
    menu = (tuple | str, ...)
        tuple: (str, ...) 下拉菜单，第一个 str 为下拉名

    方法：
        公有方法：
        getEntry() -> str 获取输入框内容
        run() 打开GUI并进入主循环
        setList(content) 设置并更新列表信息
        setButtonText(content) 更新button的文字
        setPage(page) 设置当前页面，自动将page调整到合法范围内

        模板方法：点击相应的按钮触发
        menu_cmd()
        top_cmd()
        mid_cmd()
        bot_cmd()
    """

    title = 'novelManager'
    topButton = ('搜索',)
    labelWidth = (14, 10, 6, 6)  # list每列宽度
    labelAnchor = ('w', 'w', 'e', 'e')  # 对齐方式
    lineNum = 10  # 行数
    buttonNum = 3  # 按钮数量
    menu = ()
    color = 0  # 配色方案

    def __init__(self, color=None):
        self.focused = False
        self.entry_focused = False
        self._color(color or self.color)
        self.root = self._gui()
        self.curPage = 0
        self.curList = []

    def _color(self, n):
        fg = ['#fb5c00', '#bbbbbb', 'black', '#FF00FF']
        bg = ['#ffe7d7', '#3c3f41', 'whitesmoke', '#00CED1']
        self.bg_color = bg[n]
        self.fg_color = fg[n]

    def _entry_focus_set(self, t):
        self.entry_focused = t

    def _focus_set(self, t):
        self.focused = t

    def _gui(self):
        root = Tk()
        root.bind('<FocusIn>', lambda x: self._focus_set(True))
        root.bind('<FocusOut>', lambda x: self._focus_set(False))

        font = Font(family="楷体", size=14)
        root.tk_setPalette(background=self.bg_color, foreground=self.fg_color)
        root.title(self.title)
        self._pack_menu(root)
        body = Frame(root)

        # 搜索框
        top = Frame(body)
        self.entry = Entry(top)
        self.entry.pack(side=LEFT, padx=2)
        self.entry.bind('<Return>', lambda x: self.top_cmd(0))
        self.entry.bind('<FocusIn>', lambda x: self._entry_focus_set(True))
        self.entry.bind('<FocusOut>', lambda x: self._entry_focus_set(False))
        for i, text in enumerate(self.topButton):
            Button(top, text=text, command=lambda n=i: self.top_cmd(n), font=font).pack(side=LEFT, padx=2)
        top.pack(pady=5)
        # 歌曲列表
        mid = Frame(body)
        self.list = []
        self.buttons = []
        for i in range(self.lineNum):
            line = Frame(mid)

            self.list.append([])
            for j, width in enumerate(self.labelWidth):
                t = StringVar()
                label = Label(line, anchor=self.labelAnchor[j], width=width, textvariable=t,
                              relief='ridge', borderwidth=1, font=font)
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
        self.page = StringVar(value='0 / 0')
        Label(bot, textvariable=self.page, font=font).pack(side=LEFT, padx=5)
        Button(bot, text='下一页', command=lambda: self.bot_cmd(1), font=font).pack(side=LEFT)
        bot.pack(pady=5)

        body.pack()
        return root

    def _pack_menu(self, root):
        # 菜单
        menu_root = Menu(root)
        menu_root.option_add('*font', ('楷体', 12))
        for i, item in enumerate(self.menu):
            if type(item) == str:  # 直接点击的菜单
                menu_root.add_command(label=item, command=lambda n=i: self.menu_cmd(n))
            elif type(item) == tuple:  # 下拉菜单
                menu = Menu(menu_root, tearoff=0)
                for j, hint in enumerate(item[1:]):
                    menu.add_command(label=hint, command=lambda n=(i, j): self.menu_cmd(*n))
                menu_root.add_cascade(label=item[0], menu=menu)
        root.config(menu=menu_root)

    def _updateLabel(self):
        """根据self.list和self.curPage进行渲染"""
        for i in range(self.lineNum):
            index = i + self.curPage * self.lineNum
            if index < len(self.curList):
                for j in range(len(self.labelWidth)):
                    self.list[i][j].set(self.curList[index][j])
            else:
                for j in range(len(self.labelWidth)):
                    self.list[i][j].set('')

    def _updatePage(self):
        """根据self.curList的长度，以及self.curPage，自动更新page信息"""
        form = '{:<2}/{:>2}'
        if not self.curList:
            self.curPage = cur = total = 0
        else:
            total = (len(self.curList) - 1) // self.lineNum
            self.curPage = max(0, self.curPage)
            self.curPage = min(self.curPage, total)
            cur = self.curPage + 1
            total += 1
        self.page.set(form.format(cur, total))

    def getEntry(self):
        """获取输入框信息"""
        return self.entry.get()

    def run(self):
        self.root.mainloop()

    def setButtonText(self, content):
        """更新button的文字"""
        for row in self.buttons:
            for i in range(len(row)):
                row[i].set(content[i])

    def setList(self, content):
        """更新label的信息"""
        self.curList = content
        self._updateLabel()
        self._updatePage()

    def setPage(self, page):
        self.curPage = page
        self._updateLabel()
        self._updatePage()

    def menu_cmd(self, *args, **kwargs):
        ...

    def top_cmd(self, *args, **kwargs):
        ...

    def mid_cmd(self, *args, **kwargs):
        ...

    def bot_cmd(self, d):
        """翻页命令"""
        if d == 0:  # 上一页
            self.curPage -= 1
            self._updatePage()
            self._updateLabel()
        elif d == 1:
            self.curPage += 1
            self._updatePage()
            self._updateLabel()


if __name__ == '__main__':
    Window(0).run()
