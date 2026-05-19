def example_algorithm(data):
    """
    خوارزمية بسيطة لترتيب البيانات
    """
    return sorted(data)

if __name__ == '__main__':
    data = [5, 2, 9, 1, 5, 6]
    print(f'Original: {data}')
    print(f'Sorted: {example_algorithm(data)}')
