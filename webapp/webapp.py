from flask import Flask
from flask import request
from flask import jsonify
import dataservice
import config
import json


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
# PUSH NOTIFICATIONS
# Currently the applicaion is using OneSignal as its push notification service.
# This call captures a mapping between the google id and the one signal client id.
# Using this, it is possible to send notifications to specific clients.
# ----------------------------------------------------------------------------------------|
@app.route('/registeronesignal', methods=['POST'])
def add_one_signal_mapping():
    if ('googleid' not in request.form or
            'onesignalid' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404

    if app.data_service.pushnotification_map_exists(request.form.get('googleid')):
        return jsonify({'error': 'User already exists'}), 401

    app.data_service.insert_onesingal_mapping(request.form.get('googleid'),
                                              request.form.get('onesignalid'))
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
# Adds GPS Data in bulk
# ----------------------------------------------------------------------------------------|
@app.route('/addgpsdatabulk', methods=['POST'])
def add_gps_data_bulk():
    if ('userid' not in request.form or
            'data' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    data = json.loads(request.form.get('data'))
    for row in data:
        app.data_service.add_gps_weather_data(row['latitude'],
                                              row['longitude'],
                                              row['speed'],
                                              request.form.get('userid'),
                                              row['weatherid'],
                                              row['rain'],
                                              row['wind'],
                                              row['temp'],
                                              row['pressure'],
                                              row['humidity'],
                                              row['time'])
    return jsonify({'success': 'bulk data captured'}), 200


# ----------------------------------------------------------------------------------------|
# Adds GPS Data in bulk
# ----------------------------------------------------------------------------------------|
@app.route('/addaccsensordatabulk', methods=['POST'])
def add_acc_sensor_data_bulk():
    if ('userid' not in request.form or
            'data' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    data = json.loads(request.form.get('data'))
    for row in data:
        app.data_service.add_acc_sensor_data(request.form.get('userid'),
                                             row['AccX'],
                                             row['AccY'],
                                             row['AccZ'],
                                             row['time'])
    return jsonify({'success': 'bulk data captured'}), 200


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
# Returns the driving event records by the supplied GoogleID
# ----------------------------------------------------------------------------------------|
@app.route('/getdrivingevent', methods=['POST'])
def get_driving_event_data():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(events=app.data_service.get_driving_events(request.form.get('userid')))


# ----------------------------------------------------------------------------------------|
# Gets news feed data
# ----------------------------------------------------------------------------------------|
@app.route('/getfeed', methods=['POST'])
def get_feed():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(events=app.data_service.get_feed())


# ----------------------------------------------------------------------------------------|
# Gets news feed data with limit
# ----------------------------------------------------------------------------------------|
@app.route('/getfeedlimitoffset', methods=['POST'])
def get_feed_limit():
    if ('userid' not in request.form or
            'limit' not in request.form or
            'offset' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(events=app.data_service.get_feed_limit_offset(request.form.get('limit'),
                                                                 request.form.get('offset')))


# ----------------------------------------------------------------------------------------|
# Gets profile
# ----------------------------------------------------------------------------------------|
@app.route('/getprofile', methods=['POST'])
def get_profile():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(score=app.data_service.get_score(request.form.get('userid')),
                   badges=app.data_service.get_user_badges(request.form.get('userid')))


# ----------------------------------------------------------------------------------------|
# Gets profile by user name
# ----------------------------------------------------------------------------------------|
@app.route('/getprofilebyname', methods=['POST'])
def get_profile_by_name():
    if 'name' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    data = app.data_service.get_user_id(request.form.get('name'))
    return jsonify(score=app.data_service.get_score(data[0].__str__()),
                   badges=app.data_service.get_user_badges(data[0].__str__()),
                   photo=data[1].__str__())


# ----------------------------------------------------------------------------------------|
# Returns all current users signed up for the application
# ----------------------------------------------------------------------------------------|
@app.route('/getusers', methods=['POST'])
def get_users():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(users=app.data_service.get_all_users(request.form.get('userid')))


# ----------------------------------------------------------------------------------------|
# Returns all badges assigned to the user
# ----------------------------------------------------------------------------------------|
@app.route('/getuserbadges', methods=['POST'])
def get_user_badges():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(data=app.data_service.get_user_badges(request.form.get('userid')))


# ----------------------------------------------------------------------------------------|
# Returns all badges assigned to the user
# ----------------------------------------------------------------------------------------|
@app.route('/getmapdata', methods=['POST'])
def get_map_badges():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(data=app.data_service.get_map_badges())


# ----------------------------------------------------------------------------------------|
# Returns all user activity assigned to user
# ----------------------------------------------------------------------------------------|
@app.route('/getuseractivity', methods=['POST'])
def get_user_activity():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(data=app.data_service.get_user_activity(request.form.get('userid')))


# ----------------------------------------------------------------------------------------|
# Returns all user activity for all users except current user
# ----------------------------------------------------------------------------------------|
@app.route('/getuseractivityall', methods=['POST'])
def get_user_activity_all():
    if 'userid' not in request.form:
        return jsonify({'error': 'missing parameters'}), 404
    return jsonify(data=app.data_service.get_user_activity_all(request.form.get('userid')))


# ----------------------------------------------------------------------------------------|
# Add and remove likes
# ----------------------------------------------------------------------------------------|
@app.route('/addlike', methods=['POST'])
def add_like():
    if ('userid' not in request.form or
            'badgeid' not in request.form or
            'displayname' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    app.data_service.insert_like(request.form.get('badgeid'),
                                 request.form.get('userid'),
                                 request.form.get('displayname'))
    return jsonify({'success': 'data captured'}), 200


@app.route('/removelike', methods=['POST'])
def remove_like():
    if ('userid' not in request.form or
            'badgeid' not in request.form):
        return jsonify({'error': 'missing parameters'}), 404
    app.data_service.remove_like(request.form.get('badgeid'),
                                 request.form.get('userid'))
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
        app.debug = True
        app.run()
    else:
        app.run(host='0.0.0.0')
