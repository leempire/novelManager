from orderRegister import rootOrder

while True:
    resp = rootOrder(input())
    if resp:
        print('\n' + resp)
        print('\n' + '=' * 50)
