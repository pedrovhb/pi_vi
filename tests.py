# -*- coding: UTF-8 -*-

import requests

host = 'http://localhost:5000'


def teste_home():
    print('=====================================')
    print('Testando sequência de homing')
    r = requests.post('%s/home' % host)
    print(r.json())


def teste_jog():
    print('=====================================')
    print('Testando sequência de jogging')

    print('X:')
    r0 = requests.post('%s/jog' % host, json={
        'axis': 0, 'speed': 10, 'increment': -50})
    print(r0.json())

    print('Y:')
    r1 = requests.post('%s/jog' % host, json={
        'axis': 1, 'speed': 10, 'increment': -50})
    print(r1.json())

    print('Z:')
    r2 = requests.post('%s/jog' % host, json={
        'axis': 2, 'speed': 10, 'increment': -50})
    print(r2.json())


def teste_estop():
    print('=====================================')
    print('Testando parada de emergência')
    r = requests.post('%s/estop' % host)
    print(r.json())


def teste_estop_reset():
    print('=====================================')
    print('Testando reset de parada de emergência')
    r = requests.post('%s/estop_reset' % host)
    print(r.json())


def teste_state_on():
    print('=====================================')
    print('Testando state on')
    r = requests.post('%s/state_on' % host)
    print(r.json())


def teste_state_off():
    print('=====================================')
    print('Testando state off')
    r = requests.post('%s/state_off' % host)
    print(r.json())


def teste_axis_positions():
    print('=====================================')
    print('Testando posições de eixos')
    r = requests.get('%s/axis_positions' % host)
    print(r.json())
