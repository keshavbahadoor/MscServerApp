__author__ = 'Keshav'
from flask import Flask
from flask import request
from flask import jsonify
import dataservice
import config

app = Flask(__name__)

# Executes before the request method is called.
# If this function returns data, then this is treated as the
# response of the request - good for error handling
@app.before_request
def init_request():
    app.data_service = dataservice.DataService()
    if app.data_service.connect() is False:
        return jsonify({'error': 'Database connection error'}), 404

    # API Authentication check
    if app.data_service.api_key_exists(request.headers.get('X-API-KEY')) is False:
        return jsonify({'error': 'Authentication error'}), 404

# Executes after the request is finished.
# Closes database connections, etc.
@app.teardown_appcontext
def destroy(exception):
    if hasattr(app, 'data_service') and app.data_service is not None:
        app.data_service.close()

# For testing purposes
@app.route('/testmethod')
def test():
    keys = app.data_service.get_api_keys()
    if keys is False:
        return jsonify({'error': 'Database request error'}), 404
    return jsonify(keys)

# Accepts username / userkey to register App user
@app.route('/registeruser', methods=['POST'])
def register_user():
    return jsonify({'error': 'function not supported'}), 200


@app.route('/addlocationdata', methods=['POST'])
def add_location_data():
    return jsonify({'error': 'function not supported'}), 200







if __name__ == '__main__':
    app.debug = config.DEBUG_MODE
    app.run()
