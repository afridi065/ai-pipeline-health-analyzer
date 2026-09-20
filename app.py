from flask import Flask, render_template, requests

app = Flask(__name__)

history = []

@app.route('/', methods=['GET', 'POST'])
def calculator():
    result = None
    error = None
    operation = 'add'
    num1_val = ''
    num2_val = ''

    if request.method == 'POST':
        operation = request.form.get('operation', 'add')
        num1_val = request.form.get('num1', '')
        num2_val = request.form.get('num2', '')

        try:
            if not num1_val:
                raise ValueError("Please enter the first number")
            num1 = float(num1_val)

            if operation == 'sqrt':
                if num1 < 0:
                    error = "Cannot take square root of a negative number"
                else:
                    result = num1 ** 0.5
            else:
                if not num2_val:
                    raise ValueError("Please enter the second number")
                num2 = float(num2_val)

                if operation == 'add':
                    result = num1 + num2
                elif operation == 'subtract':
                    result = num1 - num2
                elif operation == 'multiply':
                    result = num1 * num2
                elif operation == 'divide':
                    if num2 == 0:
                        error = "Cannot divide by zero"
                    else:
                        result = num1 / num2
                elif operation == 'power':
                    result = num1 ** num2
                elif operation == 'percentage':
                    result = (num1 / 100) * num2
                else:
                    error = "Unknown operation"

        except ValueError as e:
            error = str(e) if str(e) else "Please enter valid numbers"

        if result is not None and not error:
            op_display = num2_val if operation != 'sqrt' else ''
            entry = f"{num1_val} {operation} {op_display} = {result}"
            history.insert(0, entry)
            del history[10:]

    return render_template('index.html', result=result, error=error, operation=operation,
                            num1=num1_val, num2=num2_val, history=history)

@app.route('/clear-history', methods=['POST'])
def clear_history():
    history.clear()
    return calculator()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
