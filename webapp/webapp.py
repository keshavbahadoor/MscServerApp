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

    # TODO : Log API request here

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

# Accepts username / userkey to register App user
@app.route('/registeruser', methods=['POST'])
def register_user():
    return jsonify({'error': 'function not supported'}), 200

# Adds user's latitude, longitude and speed data
@app.route('/addlocationdata', methods=['POST'])
def add_location_data():
    if ('latitude' not in request.form or
       'longitude' not in request.form or
        'speed'    not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    app.data_service.add_location_data(request.form.get('latitude'),
                                       request.form.get('longitude'),
                                       request.form.get('speed'))
    return jsonify({'success': 'data captured'}), 200

# For testing purposes only
@app.route('/testmethod')
def test():
    keys = app.data_service.get_api_keys()
    if keys is False:
        return jsonify({'error': 'Database request error'}), 404
    return jsonify(keys)

# Default server root
@app.route('/')
def default():
    return jsonify({'success': 'API access point success.'}), 200


if __name__ == '__main__':
#    app.debug = config.DEBUG_MODE
    app.run(host='0.0.0.0')
