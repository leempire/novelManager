class OrderAnalyser:
    def __init__(self):
        self.orders = {'help': [self.help, '']}

    def help(self, name=''):
        """帮助文档"""
        if not name:
            return 'help [orderName=help]\n 获取orderName的帮助\n 可用指令：{}'.format(', '.join(self.orders.keys()))
        elif name in self.orders:
            return self.orders[name][1]
        else:
            return '{} 指令不存在\n 可用指令：{}'.format(name, ', '.join(self.orders.keys()))

    def register(self, name, hint=''):
        """将函数注册为指令"""
        if name in self.orders:
            raise IndexError

        def wrapper(func):
            self.orders[name] = [func, hint]

        return wrapper

    def __call__(self, order):
        orders = order.split(' ')
        if len(orders) == 0:
            return
        elif orders[0] not in self.orders:
            return '{} 指令不存在\n 可用指令：{}'.format(orders[0], ', '.join(self.orders.keys()))
        else:
            func = self.orders[orders[0]][0]
            if isinstance(func, OrderAnalyser):
                return func(' '.join(orders[1:]))
            else:
                return func(*orders[1:])


if __name__ == '__main__':
    o = OrderAnalyser()

    @o.register('f1', 'h1')
    def f1():
        return 'f1'

    @o.register('f2')
    def f2(p):
        return p

    assert o('f1') == 'f1'  # 无传参测试
    assert o('f2 123') == '123'  # 传参测试
    assert o('help f1') == 'h1'  # 帮助文档测试
