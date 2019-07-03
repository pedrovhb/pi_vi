# -*- coding: UTF-8 -*-

from flask import Flask, Response, jsonify, request, redirect
import json
import inspect
from multiprocessing import Process, Pipe
import thread_logica

try:
    import linuxcnc
except ImportError:
    import mock_linuxcnc as linuxcnc

app = Flask(__name__)


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


@app.route("/status_linuxcnc")
def get_status_linuxcnc():
    s.poll()
    props = inspect.getmembers(s, lambda a: not (inspect.isroutine(a)))
    props_dict = {}
    for p in props:
        key, val = p[0], p[1]
        props_dict[key] = val
    props_dict = json.dumps(props_dict, default=lambda x: repr(x))
    return Response(props_dict, 200, mimetype='application/json')


@app.route("/status")
def get_status():
    parent_conn.send({'comando': 'info'})
    info = parent_conn.recv()
    d = json.dumps(info, default=lambda x: repr(x))
    return Response(d, 200, mimetype='application/json')


@app.route("/comando", methods=["POST"])
def comando():
    dados = request.get_json()
    comandos_validos = ['abrir_morsa', 'fechar_morsa',
                        'iniciar_ciclo_continuo', 'parar_ciclo_continuo',
                        'iniciar_ciclo_individual']

    if dados.get('comando') in comandos_validos:
        parent_conn.send({'comando': dados['comando']})
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'Formato inválido ou comando desconhecido.'})


# Emergência

@app.route("/estop", methods=["POST", "GET"])
def state_estop():
    c.state(linuxcnc.STATE_ESTOP)
    return jsonify({'status': 'ok'})


@app.route("/estop_reset", methods=["POST"])
def state_estop_reset():
    c.state(linuxcnc.STATE_ESTOP_RESET)
    return jsonify({'status': 'ok'})


@app.route("/")
def index():
    return redirect('static/index.html')


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


if __name__ == '__main__':
    s = linuxcnc.stat()
    c = linuxcnc.command()

    parent_conn, child_conn = Pipe()
    p = Process(target=thread_logica.rodar_logica_pi, args=(child_conn,))
    p.daemon = True
    p.start()
    app.run('0.0.0.0', port=80)
