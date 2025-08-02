from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def run_mt5_command(command_type, **kwargs):
    """Run MT5 commands through Wine Python"""
    try:
        # Create a temporary Python script
        script_content = f"""
import MetaTrader5 as mt5
import json

# Initialize MT5
if not mt5.initialize():
    print(json.dumps({{"success": False, "error": "MT5 initialization failed"}}))
    exit(1)

try:
    if "{command_type}" == "login":
        login = {kwargs.get('login', 0)}
        password = "{kwargs.get('password', '')}"
        server = "{kwargs.get('server', '')}"
        
        authorized = mt5.login(login, password=password, server=server)
        if authorized:
            account_info = mt5.account_info()
            if account_info is not None:
                account_info_dict = account_info._asdict()
            else:
                account_info_dict = {{}}
            print(json.dumps({{"success": True, "account_info": account_info_dict}}))
        else:
            error_code = mt5.last_error()
            print(json.dumps({{"success": False, "error": f"Login failed: {{error_code}}"}}))
    else:
        print(json.dumps({{"success": False, "error": "Unknown command"}}))
        
finally:
    mt5.shutdown()
"""
        
        # Write script to temporary file
        with open('/tmp/mt5_script.py', 'w') as f:
            f.write(script_content)
        
        # Run with Wine Python using virtual display
        result = subprocess.run(['DISPLAY=:99', 'wine', 'python', '/tmp/mt5_script.py'], 
                              capture_output=True, text=True, timeout=30, env={'DISPLAY': ':99'})
        
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        else:
            return {"success": False, "error": f"Wine execution failed: {result.stderr}"}
            
    except Exception as e:
        return {"success": False, "error": f"Exception: {str(e)}"}

@app.route('/login-mt5', methods=['POST'])
def login_mt5():
    try:
        data = request.json
        server = data.get('server')
        login = data.get('login')
        password = data.get('password')

        # Validate input
        if not server or not login or not password:
            return jsonify({'success': False, 'message': 'Missing credentials'}), 400

        try:
            login_int = int(login)
        except ValueError:
            return jsonify({'success': False, 'message': 'Account number must be numeric.'}), 400

        # Run MT5 login through Wine
        result = run_mt5_command('login', login=login_int, password=password, server=server)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'success': False, 'message': result.get('error', 'Login failed')}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Internal server error: {str(e)}'}), 500

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'MT5 Backend is running with Wine!',
        'wine_version': '9.0'
    })

@app.route('/api/start-ea', methods=['POST'])
def start_ea():
    return jsonify({'success': True, 'message': 'start-ea endpoint reached'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    # Check if Wine and MT5 are available
    try:
        result = subprocess.run(['wine', 'python', '-c', 'import MetaTrader5; print("MT5 available")'], 
                              capture_output=True, text=True, timeout=10, env={'DISPLAY': ':99'})
        mt5_available = result.returncode == 0
    except:
        mt5_available = False
    
    return jsonify({
        'status': 'healthy',
        'wine_available': True,
        'mt5_available': mt5_available
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)