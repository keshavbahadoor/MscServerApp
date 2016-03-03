from flask import Flask
from flask import request
from flask import jsonify
import dataservice
import config


app = Flask(__name__)


# ----------------------------------------------------------------------------------------|
# Executes before the request method is called.
# If this function returns data, then this is treated as the
# response of the request - good for error handling
# ----------------------------------------------------------------------------------------|
@app.before_request
def init_request():

    # TODO : Log API request here

    app.data_service = dataservice.DataService()
    if app.data_service.connect() is False:
        return jsonify({'error': 'Database connection error'}), 404

    # API Authentication check
    if not 'datadump' in request.url_rule.rule:
        if app.data_service.api_key_exists(request.headers.get('X-API-KEY')) is False:
            return jsonify({'error': 'Authentication error'}), 404


@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# ----------------------------------------------------------------------------------------|
# Executes after the request is finished.
# Closes database connections, etc.
# ----------------------------------------------------------------------------------------|
@app.teardown_appcontext
def destroy(exception):
    if hasattr(app, 'data_service') and app.data_service is not None:
        app.data_service.close()


# ----------------------------------------------------------------------------------------|
# Accepts username / userkey to register App user
# ----------------------------------------------------------------------------------------|
@app.route('/registeruser', methods=['POST'])
def register_user():
    if ('userid' not in request.form or
            'email' not in request.form or
            'usertype' not in request.form or
            'photourl' not in request.form or
            'displayname' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404

    if app.data_service.user_exists(request.form.get('userid')):
        return jsonify({'error': 'User already exists'}), 401

    if request.form.get('usertype') == 'google':
        app.data_service.add_google_user(request.form.get('userid'),
                                         request.form.get('email'),
                                         request.form.get('displayname'),
                                         request.form.get('photourl'))
    else:
        return jsonify({'error': 'Usertype not supported'}), 401
    return jsonify({'success': 'user reigstered'}), 200


# ----------------------------------------------------------------------------------------|
# Adds user's latitude, longitude and speed data
# NOTE : functionality used for early stages of testing - not for production
# ----------------------------------------------------------------------------------------|
@app.route('/addlocationdata', methods=['POST'])
def add_location_data():
    if ('latitude' not in request.form or
            'longitude' not in request.form or
            'speed' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    app.data_service.add_location_data(request.form.get('latitude'),
                                       request.form.get('longitude'),
                                       request.form.get('speed'))
    return jsonify({'success': 'data captured'}), 200


# ----------------------------------------------------------------------------------------|
# Adds user's latitude, longitude and speed data
# client can pass timestamp - this is for cached data
# ----------------------------------------------------------------------------------------|
@app.route('/addgpsdata', methods=['POST'])
def add_gps_data():
    if ('userid' not in request.form or
            'latitude' not in request.form or
            'longitude' not in request.form or
            'speed' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    app.data_service.add_gps_weather_data(request.form.get('latitude'),
                                          request.form.get('longitude'),
                                          request.form.get('speed'),
                                          request.form.get('userid'),
                                          request.form.get('weatherid'),
                                          request.form.get('rain'),
                                          request.form.get('wind'),
                                          request.form.get('temp'),
                                          request.form.get('pressure'),
                                          request.form.get('humidity'),
                                          request.form.get('timestamp'))
    return jsonify({'success': 'data captured'}), 200


# ----------------------------------------------------------------------------------------|
# Adds user's acceleration data to server
# client can pass timestamp - this is for cached data
# ----------------------------------------------------------------------------------------|
@app.route('/addaccsensordata', methods=['POST'])
def add_acc_sensor_data():
    if ('userid' not in request.form or
            'accx' not in request.form or
            'accy' not in request.form or
            'accz' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    app.data_service.add_acc_sensor_data(request.form.get('userid'),
                                         request.form.get('accx'),
                                         request.form.get('accy'),
                                         request.form.get('accz'),
                                         request.form.get('timestamp'))
    return jsonify({'success': 'data captured'}), 200


# ----------------------------------------------------------------------------------------|
# For testing purposes only
# ----------------------------------------------------------------------------------------|
@app.route('/testmethod')
def test():
    keys = app.data_service.get_api_keys()
    if keys is False:
        return jsonify({'error': 'Database request error'}), 404
    return jsonify(keys)


@app.route('/datadump')
def get_all_data():
    data = app.data_service.get_all_data()
    if data is False:
        return jsonify({'error': 'Database request error'}), 404
    return jsonify(data=data)


# Default server root
@app.route('/')
def default():
    return jsonify({'success': 'API access point success.'}), 200


if __name__ == '__main__':
    if config.DEBUG_MODE:
        app.debug
        app.run()
    else:
        app.run(host='0.0.0.0')
