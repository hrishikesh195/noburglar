NoBurglar
=========

NoBurglar is a simple, automated way to turn on lights and TV late in the evenings when you're not in town; so that burglars walking/driving by casually will not suspect that your house is empty.

Hardware Setup 
---------------

- [Weaved SmartPlug](https://developer.weaved.com/portal/members/plug_alpha_landing.php) (along with IR Blaster)
- A regular floor lamp
- Your living room TV
- A computer to run the NoBurglar code on (I'm using a [Raspberry Pi](https://www.raspberrypi.org))

Connect the floor lamp to the SmartPlug. Verify that it turns on/off using the button on top of the Plug. Position the IR blaster such that it is directly facing the TV.

Software Setup
--------------

### SmartPlug Setup

- Set up the Plug using [these](https://developer.weaved.com/portal/members/plug_instructions.php) instructions and make sure SSH access is enabled
- Set up public-key authentication for SSH ([instructions](http://wiki.openwrt.org/doc/howto/dropbear.public-key.auth)) so that the computer running NoBurglar can connect to the `root` account on the Plug without a password
- Make sure the IR blaster is set up and identify the POWER ON and POWER OFF IR codes for your TV ([instructions](http://forum.weaved.com/t/using-the-ir-blaster-on-the-weaved-smart-plug/)); note - it's preferable to use the separate on and off codes but if your TV only has a single POWER code, use that for both

### NoBurglar Setup

Settings are defined at the top of [noburglar.py](noburglar.py) in between `BEGIN Configuration` and `END Configuration`. Parameters to be set are the IP address for the Plug, daily start and end times, IR codes, TV on duration (in the interest of saving power, we may not want the TV to be on during the entire time window when the light is on).

Using NoBurglar
---------------

### Running NoBurglar

Once the setup is done, simply -

    $ python noburglar.py

### Enable/Disable NoBurglar

If you're running NoBurglar as part of system-wide init scripts, this is handy way to enable/disable the functionality without having to kill/restart the whole thing. Put `1` or `0` in the [enabled](enabled) file. It is enabled by default. To disable -

    $ echo 0 > enabled

To enable it again -

    $ echo 1 > enabled

License
-------
[FreeBSD](LICENSE)
