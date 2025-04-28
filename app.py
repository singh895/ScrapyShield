from flask import Flask, render_template, request, send_file, abort, make_response
attack_logs = []
import json
from datetime import datetime

import html
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
    user_input = request.args.get('name', '')

    result_text = ""
    if user_input:
        # 1) rudimentary “did it run?” check
        success = "ontoggle" in user_input or "onerror" in user_input or "onload" in user_input
        result_text = "Success" if success else "Failure"

        # 2) log it
        attack_logs.append({
            'attack_type': 'XSS',
            'payload':     user_input,
            'result':      result_text,
            'status_code': 200,
            'timestamp':   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # 3) render the form + response + result
    return f'''
    <html>
      <head><title>Script Injection XSS</title></head>
      <body>
        <h1>Script Injection XSS</h1>
        <p>Enter your name:</p>
        <form action="/xss_script" method="GET">
          <input type="text" name="name" value="{html.escape(user_input)}">
          <input type="submit" value="Submit">
        </form>
        <p>Response:</p>
        <div>{html.escape(user_input)}</div>
        {f"<p><strong>Result:</strong> {result_text}</p>" if user_input else ""}
      </body>
    </html>
    '''

# @app.route('/xss_script')
# def xss_script():
#     # return render_template('xss_script.html')
#     user_input = request.args.get('name', '')  
#     if user_input:
#         attack_logs.append({
#             'attack_type':  'XSS',
#             'payload':      user_input,
#             'result':       'result',
#             'status_code':  200,
#             'timestamp':    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })
#     return '''
#     <html>
#     <head><title>Script Injection XSS</title></head>
#     <body>
#         <h1>Script Injection XSS</h1>
#         <p>Enter your name:</p>
#         <form action="/xss_script" method="GET">
#             <input type="text" name="name">
#             <input type="submit" value="Submit">
#         </form>
#         <p>Response:</p>
#         <div>{}</div>
#     </body>
#     </html>
#     '''.format(request.args.get('name', ''))

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
from datetime import datetime

@app.route('/sqli', methods=['GET', 'POST'])
def sqli():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            c.execute(query)
            result = c.fetchone()
            success = bool(result)
        except Exception as e:
            success = False

        # Record full attack info
        attack_logs.append({
            'attack_type': 'SQL Injection',
            'payload': f"Username: {username}, Password: {password}",
            'result': 'Success' if success else 'Failure',
            'status_code': 200,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

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
def logs():
    table_rows = ''.join(
        f"<tr><td>{html.escape(log['timestamp'])}</td><td>{html.escape(log['attack_type'])}</td><td>{html.escape(log['payload'])}</td><td>{html.escape(log['result'])}</td><td>{html.escape(str(log['status_code']))}</td></tr>"
        for log in attack_logs
    )
    html_content = f'''
    <html>
    <head>
        <meta http-equiv="refresh" content="5">
        <title>Attack Logs</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 90%; margin: auto; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .button {{
                display: block;
                margin: 20px auto;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }}
        </style>
        <script>
            function triggerCrawl() {{
                fetch('/trigger-sqli-crawl')
                    .then(response => {{
                        if (response.ok) {{
                            alert('SQL Injection Crawl Started!');
                        }} else {{
                            alert('Failed to start crawl.');
                        }}
                    }})
                    .catch(error => {{
                        alert('Error: ' + error);
                    }});
            }}
            function triggerXSSCrawl() {{
                fetch('/trigger-xss-crawl')
                    .then(response => {{
                        if (response.ok) {{
                            alert('XSS Crawl Started!');
                        }} else {{
                            alert('Failed to start crawl.');
                        }}
                    }})
                    .catch(error => {{
                        alert('Error: ' + error);
                    }});
            }}
        </script>
    </head>
    <body>
        <h2 style="text-align:center;">Attack Logs</h2>
        <button class="button" onclick="triggerCrawl()">Trigger SQLi Crawl</button>
        <button class="button" onclick="triggerXSSCrawl()">Trigger XSS Crawl</button>
        <table>
            <tr><th>Timestamp</th><th>Attack Type</th><th>Payload</th><th>Result</th><th>Status Code</th></tr>
            {table_rows}
        </table>
    </body>
    </html>
    '''
    return html_content



@app.route('/trigger-sqli-crawl')
def trigger_sqli_crawl():
    scrapy_project_dir = os.path.join(os.getcwd(), 'sql_crawler')
    subprocess.Popen([
        sys.executable, '-m', 'scrapy', 'crawl', 'sqli_test',
        '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        '-s', 'ROBOTSTXT_OBEY=False'
    ], cwd=scrapy_project_dir)
    return 'SQL Injection Crawl initiated in background', 202

@app.route('/trigger-xss-crawl')
def trigger_xss_crawl():
    scrapy_project_dir = os.path.join(os.getcwd(), 'xss_crawler')
    subprocess.Popen([
        sys.executable, '-m', 'scrapy', 'crawl', 'xss_playwright',
        '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        '-s', 'ROBOTSTXT_OBEY=False'
    ], cwd=scrapy_project_dir)
    return 'XSS Crawl initiated in background', 202


# @app.route('/trigger-xss-crawl')
# def trigger_xss_crawl():
#     scrapy_project_dir = os.path.join(os.getcwd(), 'xss_crawler')

#     # 1) Run the spider, dumping into results.json
#     subprocess.run([
#         sys.executable, '-m', 'scrapy', 'crawl', 'xss_playwright',
#         '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
#         '-s', 'ROBOTSTXT_OBEY=False',
#         '-o', 'results.json'
#     ], cwd=scrapy_project_dir, check=True)

#     # 2) Read results.json and append each entry with Success/Failure
#     results_path = os.path.join(scrapy_project_dir, '/workspaces/ScrapyShield/xss_crawler/results.json')
#     with open(results_path, 'r') as f:
#         entries = json.load(f)

#     for e in entries:
#         attack_logs.append({
#             'attack_type': 'XSS',
#             'payload':     e.get('payload', ''),
#             'result':      'Success' if e.get('xss_triggered') else 'Failure',
#             'status_code': 200,
#             'timestamp':   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })

#     return 'XSS Crawl completed and logged', 200

# @app.route('/trigger-xss-crawl')
# def trigger_xss_crawl():
#     scrapy_project_dir = os.path.join(os.getcwd(), 'xss_crawler')
#     # 1) Run the spider and dump results to results.json
#     subprocess.run([
#         sys.executable, '-m', 'scrapy', 'crawl', 'xss_playwright',
#         '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
#         '-s', 'ROBOTSTXT_OBEY=False',
#         '-o', 'results.json'
#     ], cwd=scrapy_project_dir, check=True)

#     # 2) Read the JSON and append to attack_logs
#     results_path = os.path.join(scrapy_project_dir, 'results.json')
#     with open(results_path, 'r') as f:
#         entries = json.load(f)

#     for e in entries:
#         attack_logs.append({
#             'attack_type': 'XSS',
#             'payload':      e.get('payload', ''),
#             'result':       'Success' if e.get('xss_triggered') else 'Failure',
#             'status_code':  200,
#             'timestamp':    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })

#     return 'XSS Crawl completed and logged', 200

if __name__ == "__main__":
    app.run(port= 5001, debug=True, host='0.0.0.0')
