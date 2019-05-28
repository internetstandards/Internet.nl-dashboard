from typing import Dict


def operation_response(error: bool = False, success: bool = False, message: str = "", data: Dict = None):
    return {'error': error,
            'success': success,
            'message': message,
            'state': "error" if error else "success",
            'data': data
            }
