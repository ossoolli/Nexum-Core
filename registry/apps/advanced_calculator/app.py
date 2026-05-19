import os

def save_result(result):
    with open('/home/madarmutaz/Mutaz-dev/registry/apps/advanced_calculator/results.txt', 'a') as f:
        f.write(str(result) + '\n')

def calculator():
    print('--- Advanced Calculator ---')
    print('Enter expression (e.g., 2+2) or type exit to quit')
    while True:
        expr = input('> ')
        if expr.lower() == 'exit': break
        try:
            result = eval(expr)
            print(f'Result: {result}')
            save_result(f'{expr} = {result}')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    calculator()