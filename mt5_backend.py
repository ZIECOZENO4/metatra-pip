from flask import Flask, request, jsonify
from flask_cors import CORS
import MetaTrader5 as mt5

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/login-mt5', methods=['POST'])
def login_mt5():
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

    # Initialize connection to MetaTrader 5 terminal
    if not mt5.initialize():
        return jsonify({'success': False, 'message': 'MT5 terminal not found or not running.'}), 500

    # Attempt login
    authorized = mt5.login(login_int, password=password, server=server)
    if authorized:
        account_info = mt5.account_info()
        if account_info is not None:
            account_info_dict = account_info._asdict()
        else:
            account_info_dict = {}
        mt5.shutdown()
        return jsonify({'success': True, 'account_info': account_info_dict})
    else:
        error_code = mt5.last_error()
        mt5.shutdown()
        return jsonify({'success': False, 'message': f'Login failed. Check credentials. MT5 error: {error_code}'}), 401
@app.route('/')
def index():
    return "MT5 Backend is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)