"""Wrapper for operations to the Weaved Smart Plug"""

import os
import logging

# Until the IR blaster can be used through a REST API, we just use SSH for everything;
# This can then be changed to do REST calls
#
# Assumes key based authentication is already set up

class Plug(object):
    def __init__(self, ip = '192.168.1.201', user='root'):
        self.ip = ip
        self.user = user

    def power_on(self):
        return self.run_ssh("weavediot_relay_on.sh")

    def power_off(self):
        return self.run_ssh("weavediot_relay_off.sh")

    def send_ir_code(self, code):
        return self.run_ssh("'stty -F /dev/ttyS0 115200; ir tx " + code + "'")

    def run_ssh(self, cmd):
        ret = os.system('ssh ' + self.user + '@' + self.ip + ' ' + cmd)
        logging.debug('Running command - ' + `cmd`)
        if ret != 0:
            logging.error('Command ' + `cmd` + ' failed: ' + `ret`)
        return ret
