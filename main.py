from orderRegister import rootOrder

while True:
    resp = rootOrder(input('>> '))
    if resp:
        print(resp)
