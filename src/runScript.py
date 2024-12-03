class RunScript:
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, filepath, args):
        if not filepath.endswith('.st'):
            filepath += '.st'
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        for i in range(len(args)):
            content = content.replace(f'$var{i + 1}', args[i])
            
        orders = self._analyse(content)
        result = ''
        for order in orders:
            tmp = self.handler(order)
            if tmp[:2] != '>>':
                result += f'>> {order}\n'
            result += tmp
        result = result[:result.rfind('\n=')]
        return result

    def _analyse(self, content):
        lines = []
        tmp = ''
        for line in content.split('\n'):
            line = line.strip()
            if not line or line[:1] == '#':
                continue
            elif line[-1:] != '\\':  # 结束一行
                tmp += line
                if tmp:
                    lines.append(tmp)
                    tmp = ''
            else:  # 跨行命令
                tmp += line[:-1].strip() + ' '
        return lines
