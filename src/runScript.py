class RunScript:
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, filepath, args):
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        for i in range(len(args)):
            content = content.replace(f'$var{i}', args[i])
            
        orders = self.analyse(content)
        for order in orders:
            self.handler(order)

    def analyse(self, content):
        lines = []
        tmp = ''
        for line in content.split('\n'):
            line = line.strip()
            if not line or line[:1] == '#':
                continue
            elif line[-1:] != '\\':  # 结束一行
                tmp += line
                if tmp:
                    print(tmp)
                    lines.append(tmp)
                    tmp = ''
            else:  # 跨行命令
                tmp += line[:-1].strip() + ' '
        return lines


if __name__ == '__main__':
    RunScript(lambda item: print(item)).analyse("""
show
insert a \\
                                        b

# ss
                                        
                                    asdg
""")
