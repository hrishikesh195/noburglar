import logging
import time
import datetime
import random

import weaved

# BEGIN Configuration

# Weaved related configuration
PLUG_IP = '192.168.1.201'       # Assumes the Smart Plug is configured for SSH and IR blaster
PLUG_USER = 'root'              # Assumes password-less (key based) SSH authentication is set up
# IR codes for turning TV on/off; use the POWER code if there aren't separate codes for POWER ON and POWER OFF
TV_ON_CODE = '2203D6F71297971C8C47206E8C743267654B3708D374B492211147000111746D0100116D75110058770065476D006D654774657400000000000000000000000000000000000000000000000000000000'
TV_OFF_CODE = '2203D6F71197971B8C47206E8C743267654B3708D374B492211147000111746D0000116D76110058770065476D006D654774657400000000000000000000000000000000000000000000000000000000'

# NoBurglar configuration
START_TIME = '1930'             # Daily start time in military time
END_TIME = '2300'               # Daily end time
TV_ON_PERCENTAGE = 50.0         # Probably don't want the TV on the entire duration of the time window

# Quick way to enable/disable
# File in the local directory containing 0 or 1; 1 => enabled
# To enable - $ echo 1 > enabled
# To disable - $ echo 0 > enabled
ENABLED_FILENAME = 'enabled'

POLL_INTERVAL = 60             # seconds

# END Configuration

DEBUG = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] %(message)s')

def enabled():
    '''Checks the file to see if this is enabled'''

    with open(ENABLED_FILENAME) as f:
        if f.read().strip() == "1":
            return True
        else:
            return False

# Global state
class State:
    def __init__(self):
        self.reset()

    def reset(self):
        self.is_light_on = False
        self.is_tv_on = False

        self.tv_start_time = 0  # When TV should be started today
        self.tv_total_time = 0  # How long the TV has been on today
        self.tv_done = False    # Whether we have completed TV time today

state = State()
plug = weaved.Plug(PLUG_IP, PLUG_USER)

def run_triggers():
    '''Run the triggers (TV/light) if applicable'''

    logging.debug("Processing triggers")

    now = datetime.datetime.today()
    t1 = datetime.datetime.combine(now.date(), datetime.datetime.strptime(START_TIME, '%H%M').time())
    t2 = datetime.datetime.combine(now.date(), datetime.datetime.strptime(END_TIME, '%H%M').time())
    in_range = t1 <= now <= t2

    # Check the light state
    if not in_range:
        if state.is_light_on:
            logging.info('Turning light off')
            if DEBUG or not plug.power_off():
                state.is_light_on = False

    elif not state.is_light_on:
        logging.info('Turning light on')
        if DEBUG or not plug.power_on():
            state.is_light_on = True

    # Randomly start the TV based on the percentage and the start and end times
    if in_range:
        if not state.tv_done:
            tv_target_duration = TV_ON_PERCENTAGE / 100 * (t2 - t1).total_seconds()
            if not state.tv_start_time:
                delay = random.random() * ((t2 - t1).total_seconds() - tv_target_duration)
                state.tv_start_time = t1 + datetime.timedelta(seconds = delay)
                logging.info('TV will turn on at around ' + str(state.tv_start_time.time()) +
                             ' for ' + str(tv_target_duration) + ' seconds')

            if now > state.tv_start_time:
                state.tv_total_time = (now - state.tv_start_time).total_seconds()
                if state.tv_total_time >= tv_target_duration:
                    # time to turn the TV off
                    logging.info('Turning TV off')
                    if DEBUG or not plug.send_ir_code(TV_OFF_CODE):
                        state.is_tv_on = False
                        state.tv_start_time = state.tv_total_time = None
                        state.tv_done = True

                elif not state.is_tv_on:
                    logging.info('Turning TV on')
                    if DEBUG or not plug.send_ir_code(TV_ON_CODE):
                        state.is_tv_on = True
    else:
        if state.is_tv_on:
            # Usually shouldn't happen unless the tv end time is close to the END_TIME
            # and the thread doesn't get woken up until it's past END_TIME
            logging.info('Turning TV off since time window has elapsed')
            if DEBUG or not plug.send_ir_code(TV_OFF_CODE):
                state.tv_start_time = state.tv_total_time = None
                state.is_tv_on = False
        state.tv_done = False

if __name__ == '__main__':

    # Check for action periodically
    while True:
        if enabled():
            run_triggers()
        else:
            # If this goes from enabled -> disabled in the middle of time window, leave the
            # physical state of the devices as it is; just reset the in-memory state
            state.reset()

        time.sleep(POLL_INTERVAL)
