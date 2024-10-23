# 命令行模式
from orderRegister import rootOrder

while True:
    resp = rootOrder(input('>> '))
    if resp:
        print(resp)
