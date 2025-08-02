from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Simulated MT5 functionality for VPS without Wine
class MockMT5:
    def __init__(self):
        self.initialized = False
        self.logged_in = False
        self.account_info = None
    
    def initialize(self):
        self.initialized = True
        return True
    
    def login(self, login, password, server):
        # Simulate login - you can add real validation here
        if login and password and server:
            self.logged_in = True
            self.account_info = {
                'login': login,
                'server': server,
                'balance': 10000.0,
                'equity': 10000.0,
                'margin': 0.0,
                'margin_free': 10000.0,
                'profit': 0.0,
                'currency': 'USD'
            }
            return True
        return False
    
    def account_info(self):
        if self.account_info:
            return type('AccountInfo', (), self.account_info)()
        return None
    
    def last_error(self):
        return (0, "No error")
    
    def shutdown(self):
        self.initialized = False
        self.logged_in = False

# Global MT5 instance
mt5 = MockMT5()

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

        # Initialize MT5
        if not mt5.initialize():
            return jsonify({'success': False, 'message': 'MT5 initialization failed'}), 500

        # Attempt login
        authorized = mt5.login(login_int, password=password, server=server)
        if authorized:
            account_info = mt5.account_info()
            if account_info is not None:
                account_info_dict = {
                    'login': account_info.login,
                    'server': account_info.server,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'margin_free': account_info.margin_free,
                    'profit': account_info.profit,
                    'currency': account_info.currency
                }
            else:
                account_info_dict = {}
            
            mt5.shutdown()
            return jsonify({'success': True, 'account_info': account_info_dict})
        else:
            error_code = mt5.last_error()
            mt5.shutdown()
            return jsonify({'success': False, 'message': f'Login failed. Check credentials. Error: {error_code}'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Internal server error: {str(e)}'}), 500

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'MT5 Backend is running (Mock Mode)!',
        'note': 'This is a simulated MT5 for VPS deployment'
    })

@app.route('/api/start-ea', methods=['POST'])
def start_ea():
    return jsonify({'success': True, 'message': 'EA endpoint reached (Mock Mode)'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'mt5_available': True,
        'mode': 'mock'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 