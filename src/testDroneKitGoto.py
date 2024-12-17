#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
simple_goto.py: GUIDED mode "simple goto" example (Copter Only)

Demonstrates how to arm and takeoff in Copter and how to navigate to points using Vehicle.simple_goto.

Full documentation is provided at http://python.dronekit.io/examples/simple_goto.html
"""

import sys

# Fix from https://stackoverflow.com/questions/70943244/attributeerror-module-collections-has-no-attribute-mutablemapping
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)

import time
from dronekit import connect, VehicleMode, LocationGlobalRelative


# # Set up option parsing to get connection string
# import argparse
# parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
# parser.add_argument('--connect',
#                     help="Vehicle connection target string. If not specified, SITL automatically started and used.")
# args = parser.parse_args()

# connection_string = "udpin:localhost:14550"
# connection_string = None
connection_string = "tcp:localhost:5772"
sitl = None


# # Start SITL if no connection string specified
# if not connection_string:
#     import dronekit_sitl
#     sitl = dronekit_sitl.start_default()
#     connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

 
    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


arm_and_takeoff(10)

# print("Set default/target airspeed to 3")
# vehicle.airspeed = 3

point1 = LocationGlobalRelative(0.027467533748910547, 36.90286865957662, 20)

# vehicle = connect("tcp:localhost:5772", wait_ready=True)
vehicle.simple_goto(point1)

# vehicle1 = connect("udpin:localhost:14560", wait_ready=True)
# vehicle1.simple_goto(point1)

# vehicle2 = connect("udpin:localhost:14570", wait_ready=True)
# vehicle2.simple_goto(point1)

# vehicle3 = connect("udpin:localhost:14580", wait_ready=True)
# vehicle3.simple_goto(point1)

# vehicle4 = connect("udpin:localhost:14590", wait_ready=True)
# vehicle4.simple_goto(point1)

# # sleep so we can see the change in map
# time.sleep(30)

# print("Going towards second point for 30 seconds (groundspeed set to 10 m/s) ...")
# point2 = LocationGlobalRelative(-35.363244, 149.168801, 20)
# vehicle.simple_goto(point2, groundspeed=10)

# # sleep so we can see the change in map
# time.sleep(30)

# print("Returning to Launch")
# vehicle.mode = VehicleMode("RTL")

# # Close vehicle object before exiting script
# print("Close vehicle object")
# vehicle.close()

# # Shut down simulator if it was started.
# if sitl:
#     sitl.stop()