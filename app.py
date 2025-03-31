from flask import Flask, render_template

app = Flask(__name__, template_folder="src/template", static_folder="src/static")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/xss')
def xss():
    return render_template('xss.html')
    # return '<h1>XSS Test Page</h1><script>alert("XSS")</script>'

@app.route('/xss_script')
def xss_script():
    return render_template('xss_script.html')

@app.route('/xss_img')
def xss_img():
    return render_template('xss_img.html')

@app.route('/xss_iframe')
def xss_iframe():
    return render_template('xss_iframe.html')

@app.route('/sqli')
def sqli():
    return '<h1>SQL Injection Test</h1><form action="login"><input name="username"><input name="password"></form>'

@app.route('/malware')
def malware():
    return '<h1>Malware Test Page</h1><a href="/download/malware.exe">Download</a>'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
