from flask import Flask, render_template, request, jsonify
import tempfile
import subprocess

app = Flask(__name__)

# Dictionary of explanations for common errors
error_dict = {
    "NameError": "Variable not defined.",
    "TypeError": "Wrong type used in operation.",
    "SyntaxError": "Check syntax: missing colons, brackets, or indentation.",
    "IndexError": "Index out of range.",
    "KeyError": "Dictionary key not found."
}

# Function to save code and run/compile it
def run_code(language, code):
    # Decide file extension and command
    if language == "python":
        ext = ".py"
        cmd = ["python"]
    elif language == "java":
        ext = ".java"
        cmd = ["javac"]
    elif language == "cpp":
        ext = ".cpp"
        cmd = ["g++"]
    elif language == "javascript":
        ext = ".js"
        cmd = ["node"]
    else:
        return "Language not supported"

    # Save user code to temp file
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
        temp_file.write(code.encode())
        temp_file_path = temp_file.name

    try:
        if language in ["java", "cpp"]:
            # Compile for Java/C++
            result = subprocess.run(cmd + [temp_file_path],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return result.stderr
            return "Compiled successfully! (You can run manually)"
        else:
            # Run Python/JS
            result = subprocess.run(cmd + [temp_file_path],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return result.stderr
            return result.stdout if result.stdout else "Code ran successfully!"
    except subprocess.TimeoutExpired:
        return "Code took too long to run!"

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/explain', methods=['POST'])
def explain():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')  # default Python
    output = run_code(language, code)
    return jsonify({'output': output})

if __name__ == "__main__":
    app.run(debug=True)
