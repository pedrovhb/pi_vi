# -*- coding: UTF-8 -*-

from flask import Flask, Response, jsonify, request
import json
import inspect

try:
    import linuxcnc
except ImportError:
    import mock_linuxcnc as linuxcnc

app = Flask(__name__)

s = linuxcnc.stat()
c = linuxcnc.command()


def ok_for_mdi():
    s.poll()
    return not s.estop and s.enabled and s.homed and (s.interp_state == linuxcnc.INTERP_IDLE)


# Info Linux CNC:
# http://linuxcnc.org/docs/2.6/html/common/python-interface.html


#########################################################
# Info

@app.route("/axis_positions")
def get_axis_positions():
    s.poll()
    axes = s.axis[:3]
    axes_positions = [round(axis['output'], 4) for axis in axes]
    axes_positions = {
        'X': axes_positions[0],
        'Y': axes_positions[1],
        'Z': axes_positions[2]}
    return jsonify(axes_positions)


@app.route("/status")
def get_status():
    s.poll()
    props = inspect.getmembers(s, lambda a: not (inspect.isroutine(a)))
    props_dict = {}
    for p in props:
        key, val = p[0], p[1]
        props_dict[key] = val
    props_dict = json.dumps(props_dict, default=lambda x: repr(x))
    return Response(props_dict, 200, mimetype='application/json')


#########################################################
# Movimentação


@app.route("/jog", methods=['POST'])
def jog():
    if not ok_for_mdi():
        return jsonify({'status': 'busy'})

    data = request.get_json()
    print(data)
    axis = data.get('axis')
    speed = data.get('speed')
    increment = data.get('increment')
    c.jog(linuxcnc.JOG_INCREMENT, axis, speed, increment)
    return jsonify({'status': 'ok'})


@app.route("/mdi", methods=['POST'])
def mdi():
    if not ok_for_mdi():
        return jsonify({'status': 'busy'})
    print(request.headers)
    data = request.get_json()
    print(data)
    mdi_command = data.get('mdi')
    c.mode(linuxcnc.MODE_MDI)
    c.mdi(mdi_command)
    return jsonify({'status': 'ok'})


@app.route("/home", methods=['POST'])
def home():
    if ok_for_mdi():
        c.home(0)
        c.home(1)
        c.home(2)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'busy'})


#########################################################
# Emergência

@app.route("/estop", methods=["POST", "GET"])
def state_estop():
    c.state(linuxcnc.STATE_ESTOP)
    return jsonify({'status': 'ok'})


@app.route("/estop_reset", methods=["POST"])
def state_estop_reset():
    c.state(linuxcnc.STATE_ESTOP_RESET)
    return jsonify({'status': 'ok'})


#########################################################
# On/Off

@app.route("/state_on", methods=["POST", "GET"])
def state_on():
    c.state(linuxcnc.STATE_ON)
    return jsonify({'status': 'ok'})


@app.route("/state_off", methods=["POST"])
def state_off():
    c.state(linuxcnc.STATE_OFF)
    return jsonify({'status': 'ok'})


#########################################################

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


if __name__ == '__main__':
    app.run('0.0.0.0')
