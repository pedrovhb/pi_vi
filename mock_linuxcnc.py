# -*- coding: UTF-8 -*-

INTERP_IDLE = 'mock_interp_state'

STATE_ESTOP = 'mock_state_estop'
STATE_ESTOP_RESET = 'mock_state_reset'
STATE_ON = 'mock_state_on'
STATE_OFF = 'mock_state_off'

JOG_INCREMENT = 1
MODE_MDI = 'mock_mode_mdi'


class MockStat:
    def __init__(self):
        self.interp_state = 'mock_interp_state'
        self.estop = False
        self.enabled = False
        self.homed = False
        self.axis = [
            {'output': 10},
            {'output': 20},
            {'output': 30},
        ]

    def poll(self):
        print('MockState poll')


class MockCommand:

    def __init__(self):
        pass

    def mode(self, mode):
        print('MockCommand mode %s' % mode)

    def mdi(self, mdi):
        print('MockCommand mdi %s' % mdi)

    def home(self, home):
        print('MockCommand home %s' % home)

    def state(self, state):
        print('MockCommand state %s' % state)


def stat():
    return MockStat()


def command():
    return MockCommand()
