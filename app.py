from flask import Flask, render_template, request, send_file, abort, make_response, send_from_directory
attack_logs = []
import json
from datetime import datetime
from werkzeug.utils import secure_filename

import html
import html
import os
import sqlite3
import random, string
import subprocess
import sys
import json

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
        success = "ontoggle" in user_input or "onerror" in user_input or "onload" in user_input
        result_text = "Success" if success else "Failure"

        attack_logs.append({
            'attack_type': 'XSS',
            'payload':     user_input,
            'result':      result_text,
            'status_code': 200,
            'timestamp':   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

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

@app.route('/download/<path:filename>')
def download_file(filename):
    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(filename)
    file_path = os.path.join(DOWNLOADS_DIR, safe_filename)
    if not os.path.isfile(file_path):
        abort(404, description="File not found")
    response = make_response(send_from_directory(DOWNLOADS_DIR, safe_filename, as_attachment=True))
    # Optional: Add custom headers for malware files
    if safe_filename == "MalwareSimulation.exe":
        response.headers.extend({
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': "default-src 'none'",
            'X-Simulation-Malware': 'true'
        })
    return response

    # except Exception as e:
    #     # Handle errors gracefully
    #     abort(500, description=f"Error serving file: {str(e)}")


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
    # Build escaped table rows
    table_rows = ''.join(
        "<tr>"
        f"<td>{html.escape(log['timestamp'])}</td>"
        f"<td>{html.escape(log['attack_type'])}</td>"
        f"<td>{html.escape(log['payload'])}</td>"
        f"<td>{html.escape(log['result'])}</td>"
        f"<td>{html.escape(str(log['status_code']))}</td>"
        "</tr>"
        for log in attack_logs
    )

    # Full HTML response
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <!-- Font Awesome for icons -->
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
          integrity="sha512-p1CmJ7TQ5fwyfQHO+X8ZfWj1K5KfRb1EN5p5SWd1/kIkTO7EY1q4/dd+uc9Y4jXe1bZ+lPvMBNi+IbbE1JY0hQ=="
          crossorigin="anonymous" referrerpolicy="no-referrer" />
    <meta http-equiv="refresh" content="5">
    <title>Attack Logs</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f0f0f0; }}
        h2 {{ text-align: center; padding: 1rem 0; }}
        .button {{
            display: inline-block;
            margin: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            background-color: #4CAF50;
            color: #fff;
            border: none;
            border-radius: 5px;
            text-decoration: none;
        }}
        .button.blue {{ background-color: #2196F3; }}
        table {{
            border-collapse: collapse;
            width: 90%;
            margin: 1rem auto 2rem;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 0.75rem;
            text-align: center;
        }}
        th {{ background-color: #ddd; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
    <script>
        function triggerCrawl() {{
            fetch('/trigger-sqli-crawl')
              .then(r => r.ok ? alert('SQLi Crawl Started!') : alert('Failed to start SQLi'));
        }}
        function triggerXSSCrawl() {{
            fetch('/trigger-xss-crawl')
              .then(r => r.ok ? alert('XSS Crawl Started!') : alert('Failed to start XSS'));
        }}
        function triggerMaliCrawl() {{
            fetch('/trigger-mali-crawl')
              .then(r => r.ok ? alert('Malware Crawl Started!') : alert('Failed to start Malware'));
        }}
    </script>
</head>
<body>
    <h2>Attack Logs</h2>
    <div style="text-align:center;">
        <button class="button" onclick="triggerCrawl()">
            <i class="fa-solid fa-bug"></i> Trigger SQLi Crawl
        </button>
        <button class="button" onclick="triggerXSSCrawl()">
            <i class="fa-solid fa-bug"></i> Trigger XSS Crawl
        </button>
        <button class="button" onclick="triggerMaliCrawl()">
            <i class="fa-solid fa-bug"></i> Trigger Malware Crawl
        </button>
        <a href="/malware-results" target="_blank" class="button blue">
            <i class="fa-solid fa-download"></i> View Malware Results
        </a>
    </div>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Attack Type</th>
            <th>Payload</th>
            <th>Result</th>
            <th>Status Code</th>
        </tr>
        {table_rows}
    </table>
</body>
</html>"""
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



@app.route('/trigger-mali-crawl')
def trigger_mali_crawl():
    scrapy_project_dir = os.path.join(os.getcwd(), 'malicious_crawler')
    subprocess.Popen([
        sys.executable, '-m', 'scrapy', 'crawl', 'mali_spider',
        '-O', 'malware_results.json',
        '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        '-s', 'ROBOTSTXT_OBEY=False'
    ], cwd=scrapy_project_dir)
    return 'Malware Crawl initiated in background', 202

@app.route('/malware-results')
def malware_results():
    results_path = os.path.join(os.getcwd(), 'malicious_crawler', 'malware_results.json')
    if not os.path.exists(results_path):
        return "No results yet. Run the crawl first!", 404
    
    with open(results_path) as f:
        data = json.load(f)

    # Define column order and friendly names
    columns = [
        ('timestamp', 'Time Downloaded'),
        ('filename', 'File Name'),
        ('size_bytes', 'File Size'),
        ('url', 'Download URL'),
        ('status', 'Status')
    ]

    # Build table headers
    table_headers = "<tr>" + "".join(f"<th>{display}</th>" for _, display in columns) + "</tr>"

    # Build table rows with formatted values
    table_rows = []
    for row in data:
        cells = []
        for key, _ in columns:
            value = row.get(key, '')
            if key == 'timestamp':
                value = datetime.fromisoformat(value).strftime('%Y-%m-%d %H:%M:%S')
            elif key == 'size_bytes':
                value = f"{round(value/1024, 2)} KB"
            cells.append(f"<td>{value}</td>")
        table_rows.append(f"<tr>{''.join(cells)}</tr>")
    
    table_rows = ''.join(table_rows)

    html_content = f"""
    <html>
    <head>
        <title>Malware Crawl Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f8f8f8; }}
            table {{ border-collapse: collapse; width: 90%; margin: 40px auto; 
                    background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background: #2c3e50; color: #fff; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            h2 {{ text-align: center; margin: 40px 0; color: #2c3e50; }}
            .size {{ text-align: right; }}
        </style>
    </head>
    <body>
        <h2>📁 Malware Crawl Results</h2>
        <table>
            {table_headers}
            {table_rows}
        </table>
    </body>
    </html>
    """
    return html_content


@app.route('/trigger-xss-crawl', methods=['GET', 'POST'])
def trigger_xss_crawl():
    scrapy_project_dir = os.path.join(os.getcwd(), 'xss_crawler')
    subprocess.Popen([
        sys.executable, '-m', 'scrapy', 'crawl', 'xss_playwright',
        '-s', 'USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        '-s', 'ROBOTSTXT_OBEY=False'
    ], cwd=scrapy_project_dir)
    return 'XSS Crawl initiated in background', 202


if __name__ == "__main__":
    app.run(port= 5001, debug=True, host='0.0.0.0')
