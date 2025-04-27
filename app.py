from flask import Flask, render_template, request, send_file, abort, make_response
logs = []  # Store attack logs
import os
import sqlite3
import random, string
import subprocess
import sys

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
        
        logs.append(f"[SQLi Attempt] Username: {username}, Password: {password}")
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
    return render_template('malware.html')

DOWNLOADS_DIR = os.path.abspath('/workspaces/ScrapyShield/mali_crawler/dist/')

@app.route('/download/MalwareSimulation.exe')
def malwareDownload():
    try:
        # Path to the file
        file_path = os.path.join(DOWNLOADS_DIR, 'MalwareSimulation.exe')

        # Check if the file exists
        if not os.path.isfile(file_path):
            abort(404, description="File not found")

        # Serve the file securely
        response = make_response(send_file(
            file_path,
            mimetype='application/vnd.microsoft.portable-executable',
            as_attachment=True,
            download_name='MalwareSimulation.exe'
        ))

        # Add security headers
        response.headers.extend({
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': "default-src 'none'",
            'X-Simulation-Malware': 'true'
        })

        return response

    except Exception as e:
        # Handle errors gracefully
        abort(500, description=f"Error serving file: {str(e)}")


@app.route('/disguised_download')
def disguised_download():
    # Generate random filename with common extensions
    ext = random.choice(['doc', 'pdf', 'exe', 'msi'])
    fake_name = ''.join(random.choices(string.ascii_lowercase, k=8)) + f'.{ext}'
    return f'<a href="/download/{fake_name}">Download Important Document</a>'

# app.py addition
@app.route('/trigger-crawl')
def trigger_crawl():
    subprocess.run([
        sys.executable, '-m', 'scrapy', 'crawl', 'malware_crawler',
        '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '-s', 'ROBOTSTXT_OBEY=False'
    ], check=True)
    return 'Crawl initiated', 202

@app.route('/logs')
def view_logs():
    return "<br>".join(logs)


if __name__ == "__main__":
    app.run(port= 5001, debug=True, host='0.0.0.0')
