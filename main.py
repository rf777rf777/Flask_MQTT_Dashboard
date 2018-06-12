import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

eventlet.monkey_patch()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '35.227.109.21'
app.config['MQTT_BROKER_PORT'] = 1883

app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('home.html')


@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])

@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe('home/mytopic')

'''
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
	mqtt.subscribe('home/mytopic')
'''

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(data)
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, use_reloader=True, debug=True)

