# 命令解析、指令注册
import os


class OrderAnalyser:
    autoCls = False

    def __init__(self):
        self.orders = {'help': [self.help, '']}

    def help(self, name='help', *args):
        """帮助文档"""
        if not name or name == 'help':  # 默认值，显示所有可用指令
            return 'help [orderName=help]\n 获取orderName的帮助\n 可用指令：{}'.format(', '.join(self.getAllOrders()))
        elif name in self.orders:
            item = self.orders[name]
            if isinstance(item[0], OrderAnalyser) and args:
                return item[0].help(*args)
            else:
                return item[1]
        else:
            return '{} 指令不存在\n 可用指令：{}'.format(name, ', '.join(self.getAllOrders()))

    def getAllOrders(self):
        """获取所有可用指令"""
        orders = []
        for k, v in self.orders.items():
            if isinstance(v[0], OrderAnalyser):
                for o in v[0].getAllOrders():  # 递归
                    if o == 'help':
                        continue
                    orders.append(k + ' ' + o)
            else:
                orders.append(k)
        return orders

    def register(self, name, hint=''):
        """将函数注册为指令"""
        if name in self.orders:
            raise IndexError

        def wrapper(func):
            self.orders[name] = [func, hint]

        return wrapper

    def __call__(self, order, isRoot=True):
        """处理order指令，isRoot为True时，为根指令，否则为子指令"""

        result = ''  # 最终的输出
        orders = order.split(' ')

        if isRoot and self.autoCls:  # 根指令，清空屏幕
            os.system('cls')
            result += '>> ' + order + '\n'

        if len(orders) == 0:  # 空输入
            return
        elif orders[0] not in self.orders:  # 指令不存在
            result += '{} 指令不存在\n 可用指令：{}'.format(orders[0], ', '.join(self.getAllOrders()))
        else:  # 指令存在
            try:
                func = self.orders[orders[0]][0]
                if isinstance(func, OrderAnalyser):  # 存在子指令
                        result += func(' '.join(orders[1:]), False)
                else:
                    result += func(*orders[1:])
            except Exception as e:
                result += '出错了:(\n请自行修复或联系开发者！\n{}'.format(e)

        result += '\n'
        if isRoot:
            # 分隔符
            try:
                result += '=' * os.get_terminal_size()[0]
            except OSError:
                result += '=' * 50
        return result.strip()


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
