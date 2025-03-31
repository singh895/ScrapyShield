from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__, template_folder="src/template", static_folder="src/static")

def init_db():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)
    ''')
    c.execute('''
    INSERT INTO users (username, password) VALUES ('admin', 'password123')
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/xss')
def xss():
    return render_template('xss.html')
    # return '<h1>XSS Test Page</h1><script>alert("XSS")</script>'

@app.route('/xss_script')
def xss_script():
    # return render_template('xss_script.html')
    user_input = request.args.get('name', '')  
    return '''
    <html>
    <head><title>Script Injection XSS</title></head>
    <body>
        <h1>Script Injection XSS</h1>
        <p>Enter your name:</p>
        <form action="/xss_script" method="GET">
            <input type="text" name="name">
            <input type="submit" value="Submit">
        </form>
        <p>Response:</p>
        <div>{}</div>
    </body>
    </html>
    '''.format(request.args.get('name', ''))

@app.route('/xss_img')
def xss_img():
    # return render_template('xss_img.html')
    return '''
    <html>
    <head><title>Image Injection XSS</title></head>
    <body>
        <h1>Image Injection XSS</h1>
        <p>This page attempts to execute JavaScript using an image tag.</p>
        <img src="x" onerror="alert('XSS via Image!')">
    </body>
    </html>
    '''


@app.route('/xss_iframe')
def xss_iframe():
    # return render_template('xss_iframe.html')
    return '''
    <html>
    <head><title>Iframe Injection XSS</title></head>
    <body>
        <h1>Iframe Injection XSS</h1>
        <p>This page loads an iframe that may contain malicious scripts.</p>
        <iframe src="javascript:alert('XSS via Iframe!')"></iframe>
    </body>
    </html>
    '''

@app.route('/sqli', methods=['GET', 'POST'])
def sqli():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        # Retrieve input from form
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Perform the SQL query with the injected inputs
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        c.execute(query)
        
        result = c.fetchone()
        if result:
            return f"Welcome, {username}!"
        else:
            return "Invalid credentials"
    return '''
        <h1>SQL Injection Test</h1>
        <form method="POST">
            <input name="username" placeholder="Username"><br><br>
            <input name="password" placeholder="Password"><br><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/malware')
def malware():
    return '<h1>Malware Test Page</h1><a href="/download/malware.exe">Download</a>'

if __name__ == "__main__":
    app.run(port= 5001, debug=True, host='0.0.0.0')
