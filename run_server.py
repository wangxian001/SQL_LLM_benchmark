# Version: 2026-07-06T14:36:50+08:00
# Description: Start a local HTTP server in the current directory with CORS headers, open the page in browser, and handle POST requests to save evaluation traces directly to CSV files inside a trace_log directory, supporting multi-round runs naming convention.

import http.server
import socketserver
import webbrowser
import threading
import sys
import os
import json
import csv
from datetime import datetime

PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/save_trace':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                
                # Check for structure type
                if isinstance(payload, dict) and 'results' in payload:
                    trace_data = payload.get('results', [])
                    round_num = payload.get('roundNum')
                    total_rounds = payload.get('totalRounds')
                    batch_id = payload.get('batchId')
                else:
                    trace_data = payload
                    round_num = None
                    total_rounds = None
                    batch_id = None
                
                # Generate filename and target directory
                trace_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace_log")
                if batch_id:
                    batch_dir = os.path.join(trace_log_dir, batch_id)
                    if round_num is not None:
                        filename = f"round_{round_num}.csv"
                    else:
                        filename = "trace.csv"
                else:
                    batch_dir = trace_log_dir
                    now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    if round_num is not None:
                        filename = f"test_trace_{now}_round_{round_num}.csv"
                    else:
                        filename = f"test_trace_{now}.csv"
                    
                if not os.path.exists(batch_dir):
                    os.makedirs(batch_dir)
                filepath = os.path.join(batch_dir, filename)
                
                # Write CSV with utf-8-sig to support Chinese characters in Excel
                with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    # Headers
                    writer.writerow([
                        "Question ID", "Difficulty", "Question", "Status", 
                        "Attempts", "Input Tokens", "Output Tokens", 
                        "Expected Row Count", "Actual Row Count",
                        "Expected Column Count", "Actual Column Count",
                        "Generated SQL", "Error Message", "Full Dialogue Trace"
                    ])
                    
                    for item in trace_data:
                        # Format the full dialogue trace text
                        trace_text_parts = []
                        if 'history' in item:
                            for idx, step in enumerate(item['history']):
                                step_num = idx + 1
                                trace_text_parts.append(f"--- 回合 {step_num} ---")
                                
                                resp = step.get('response', {})
                                if resp.get('reasoning'):
                                    trace_text_parts.append(f"[思维链路]\n{resp['reasoning']}")
                                
                                if resp.get('toolCall'):
                                    tc = resp['toolCall']
                                    fn = tc.get('function') or {}
                                    tc_name = tc.get('name') or fn.get('name')
                                    tc_args = tc.get('arguments') or fn.get('arguments')
                                    trace_text_parts.append(f"[工具调用] {tc_name} with args: {tc_args}")
                                elif resp.get('content'):
                                    trace_text_parts.append(f"[助手输出]\n{resp['content']}")
                                    
                                if step.get('result'):
                                    trace_text_parts.append(f"[执行结果]\n{step['result']}")
                                elif step.get('error'):
                                    trace_text_parts.append(f"[执行报错]\n{step['error']}")
                                    
                        full_trace_str = "\n\n".join(trace_text_parts)
                        
                        writer.writerow([
                            item.get('id', ''),
                            item.get('difficulty', ''),
                            item.get('question', ''),
                            item.get('status', ''),
                            item.get('attempts', 0),
                            item.get('inputTokens', 0),
                            item.get('outputTokens', 0),
                            item.get('expectedRowCount', ''),
                            item.get('actualRowCount', ''),
                            item.get('expectedColumnCount', ''),
                            item.get('actualColumnCount', ''),
                            item.get('generatedSql', ''),
                            item.get('error', ''),
                            full_trace_str
                        ])
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                resp_payload = json.dumps({"status": "success", "filename": filename, "path": filepath})
                self.wfile.write(resp_payload.encode('utf-8'))
                print(f"Successfully saved trace to: {filepath}")
                
            except Exception as e:
                print(f"Error handling save_trace POST: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
                
        elif self.path == '/save_summary':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                batch_id = payload.get('batchId')
                summary_content = payload.get('summary', '')
                
                if not batch_id or not summary_content:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Missing batchId or summary")
                    return
                
                trace_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace_log")
                batch_dir = os.path.join(trace_log_dir, batch_id)
                if not os.path.exists(batch_dir):
                    os.makedirs(batch_dir)
                    
                filename = "summary.md"
                filepath = os.path.join(batch_dir, filename)
                
                with open(filepath, mode='w', encoding='utf-8') as f:
                    f.write(summary_content)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "filename": filename, "path": filepath}).encode('utf-8'))
                print(f"Successfully saved summary to: {filepath}")
            except Exception as e:
                print(f"Error handling save_summary POST: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
                
        elif self.path == '/download_zip':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                batch_id = payload.get('batchId')
                summary_content = payload.get('summary', '')
                
                if not batch_id:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Missing batchId")
                    return
                
                import io
                import zipfile
                
                trace_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace_log")
                batch_dir = os.path.join(trace_log_dir, batch_id)
                
                # Create an in-memory zip file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # If batch directory exists, pack everything inside it
                    if os.path.exists(batch_dir):
                        for file_name in os.listdir(batch_dir):
                            file_path = os.path.join(batch_dir, file_name)
                            if os.path.isfile(file_path):
                                zip_file.write(file_path, file_name)
                    else:
                        # Fallback for old style structure or pure client-side payloads
                        if summary_content:
                            zip_file.writestr("summary.md", summary_content)
                        if os.path.exists(trace_log_dir):
                            for file_name in os.listdir(trace_log_dir):
                                if file_name.startswith(batch_id) and file_name.endswith('.csv'):
                                    file_path = os.path.join(trace_log_dir, file_name)
                                    zip_file.write(file_path, file_name)
                
                zip_data = zip_buffer.getvalue()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', f'attachment; filename={batch_id}.zip')
                self.send_header('Content-Length', str(len(zip_data)))
                self.end_headers()
                
                self.wfile.write(zip_data)
                print(f"Successfully packaged and downloaded ZIP: {batch_id}.zip")
                
            except Exception as e:
                print(f"Error handling download_zip POST: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Serving files from directory: {script_dir}")

    Handler = CORSHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server started at http://localhost:{PORT}/")
            
            url = f"http://localhost:{PORT}/sql_benchmark.html"
            print(f"Opening browser at: {url}")
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
            
            print("Press Ctrl+C to terminate the server.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
