import json
import MetaTrader5 as mt5

def handler(request):
    # Handle root path
    if request.get("path", "/") == "/":
        return {
            "statusCode": 200,
            "body": "MT5 Backend is running!"
        }

    # Handle /login-mt5 POST
    if request.get("path") == "/login-mt5" and request.get("method") == "POST":
        try:
            data = json.loads(request["body"])
        except Exception:
            return {
                "statusCode": 400,
                "body": json.dumps({"success": False, "message": "Invalid JSON"}),
                "headers": {"Content-Type": "application/json"}
            }
        server = data.get('server')
        login = data.get('login')
        password = data.get('password')

        if not server or not login or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({'success': False, 'message': 'Missing credentials'}),
                "headers": {"Content-Type": "application/json"}
            }
        try:
            login_int = int(login)
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps({'success': False, 'message': 'Account number must be numeric.'}),
                "headers": {"Content-Type": "application/json"}
            }
        if not mt5.initialize():
            return {
                "statusCode": 500,
                "body": json.dumps({'success': False, 'message': 'MT5 terminal not found or not running.'}),
                "headers": {"Content-Type": "application/json"}
            }
        authorized = mt5.login(login_int, password=password, server=server)
        if authorized:
            account_info = mt5.account_info()
            if account_info is not None:
                account_info_dict = account_info._asdict()
            else:
                account_info_dict = {}
            mt5.shutdown()
            return {
                "statusCode": 200,
                "body": json.dumps({'success': True, 'account_info': account_info_dict}),
                "headers": {"Content-Type": "application/json"}
            }
        else:
            error_code = mt5.last_error()
            mt5.shutdown()
            return {
                "statusCode": 401,
                "body": json.dumps({'success': False, 'message': f'Login failed. Check credentials. MT5 error: {error_code}'}),
                "headers": {"Content-Type": "application/json"}
            }
    # Not found
    return {
        "statusCode": 404,
        "body": json.dumps({"success": False, "message": "Not found"}),
        "headers": {"Content-Type": "application/json"}
    }