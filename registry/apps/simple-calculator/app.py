def calculator():
    print("--- حاسبة بسيطة ---")
    try:
        num1 = float(input("أدخل الرقم الأول: "))
        op = input("أدخل العملية (+, -, *, /): ")
        num2 = float(input("أدخل الرقم الثاني: "))

        if op == '+': result = num1 + num2
        elif op == '-': result = num1 - num2
        elif op == '*': result = num1 * num2
        elif op == '/': result = num1 / num2 if num2 != 0 else "خطأ: القسمة على صفر"
        else: result = "عملية غير صالحة"

        print(f"النتيجة: {result}")
    except ValueError:
        print("خطأ: يرجى إدخال أرقام صحيحة.")

if __name__ == '__main__':
    calculator()