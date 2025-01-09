# Fix from https://stackoverflow.com/questions/70943244/attributeerror-module-collections-has-no-attribute-mutablemapping
import sys
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)

from dataTypes import geoLoc, geoCircle
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import itertools
from pymavlink import mavutil
import param as PARAM
import requests
import numpy as np
import socket

class Drone:
    def __init__(self, sysID, IP, portNumber, takeoff):
        self.sysID = sysID
        self.IP = IP
        self.portNumber = portNumber
        self.takeoff = takeoff

        self.name = f"Drone{sysID}"
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.rhinosFound = 0
        self.isLastWait = False

        self.printInfo(f"Connecting to {IP}:{portNumber}")
        self.startConnection()

    def startConnection(self):
        self.vehicle = connect(f"tcp:{self.IP}:{self.portNumber}", wait_ready=True)
        
        if self.takeoff:
            while not self.vehicle.is_armable:
                self.printInfo(" Waiting for vehicle to initialise...", wait=True)
                time.sleep(1)
            
            self.arm()
            self.take_off(PARAM.takeOffAltitude)

    def printInfo(self, msg, wait=False):
        if wait:
            if not self.isLastWait:
                print()
            sys.stdout.write("\033[F\033[K")
            sys.stdout.write(f"\r{time.strftime('%Y-%m-%d %H:%M:%S')} - {self.name}: {next(self.spinner)} {msg}\n")
            self.isLastWait = True
        else:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {self.name}: {msg}")        
            self.isLastWait = False

    def arm(self):
        self.printInfo("Switch to GUIDED and arming motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
    
        # Wait for vehicle to arm
        while not self.vehicle.armed:
            self.printInfo(" Waiting for arming...", wait=True)
            time.sleep(1)


    def take_off(self, altitude):
        self.printInfo("Taking off!")
        self.vehicle.simple_takeoff(altitude) 

        while True:
            self.printInfo(f" Altitude: {self.vehicle.location.global_relative_frame.alt}", wait=True)
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= altitude * PARAM.takeOffThreshold:
                self.printInfo("Reached target altitude")
                break
            time.sleep(1) 

    def get_position(self) -> geoLoc:
        pos = self.vehicle.location.global_relative_frame
        return geoLoc(pos.lat, pos.lon, pos.alt)

    def send_to_waypoint(self, waypoint : geoLoc):
        if waypoint.alt is None:
            waypoint.alt = self.vehicle.location.global_relative_frame.alt
        point = LocationGlobalRelative(waypoint.lat, waypoint.lon, waypoint.alt)
        self.vehicle.simple_goto(point)

    def gotoWP(self, waypoint : geoLoc):
        self.send_to_waypoint(waypoint)
        while not self.is_waypoint_reached(waypoint):
            self.printInfo(f"Moving to {waypoint}", wait=True)
            # self.vehicle.home_location = self.vehicle.location.global_frame
            time.sleep(1)

        self.printInfo(f"Waypoint reached {waypoint}")
            
    def is_waypoint_reached(self, waypoint : geoLoc, threshold=10):
        pos = self.get_position()
        dist = pos.distTo(waypoint)
        return dist < threshold
    
    def get_rhinos_found(self):
        return self.rhinosFound
    
    def reset_rhinos_found(self):
        self.rhinosFound = 0

class DroneListener(Drone):
    def __init__(self, sysID, IP, portNumber, mavlinkHandler):
        self.mavlinkHandler = mavlinkHandler
        super().__init__(sysID, IP, portNumber, False)

    def startConnection(self):
        # self.vehicle = mavutil.mavlink_connection(f'udpin:{self.IP}:{self.portNumber}')
        self.vehicle = self.mavlinkHandler

    def get_position(self):
        while True:
            msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if not msg:
                continue
            elif msg.get_srcSystem()==self.sysID:
                msg = msg.to_dict()
                return geoLoc(msg["lat"] * 1e-7, msg["lon"] * 1e-7, msg["alt"]  * 1e-3)
            else:
                continue

class DroneManager:
    def __init__(self):
        self.drones = {}

    def get_drone_position(self, droneID):
        return self.drones[droneID].get_position()
    
    def get_rhinos_found(self, droneID):
        return self.drones[droneID].get_rhinos_found()
    
    def reset_rhinos_found(self, droneID):
        self.drones[droneID].reset_rhinos_found()

    def send_drone_to_waypoint(self, droneID, waypoint):
        self.drones[droneID].send_to_waypoint(waypoint)

    def getDroneNames(self):
        return [self.drones[droneID].name for droneID in self.drones.keys()]

    def getDroneIDs(self):
        return self.drones.keys()
    
    def rhinoFound(self, droneID):
        self.drones[droneID].rhinosFound += 1

    def createSwarm(self, n, takeoff=True, listenOnly=False):
        if listenOnly:
            mavlinkHandler = mavutil.mavlink_connection(f'udpin:{PARAM.IP}:{PARAM.PORT_LISTERNER}')
            for i in range(n):
                self.drones[i+1] = DroneListener(sysID=i+1, IP=PARAM.IP, portNumber=PARAM.PORT_LISTERNER, mavlinkHandler=mavlinkHandler)
        else:
            for i in range(n):
                self.drones[i+1] = Drone(sysID=i+1, IP=PARAM.IP, portNumber=PARAM.PORT_MASTER + i*10, takeoff=takeoff)

    def getDroneIP(self, droneID, listenOnly=False):
        if PARAM.IP in {"localhost", "0.0.0.0", "127.0.0.1"}:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                IP = s.getsockname()[0]
            except Exception:
                IP = "127.0.0.1"
            finally:
                s.close()
        else:
            IP = PARAM.IP
        if listenOnly:
            return f"udpin:{IP}:{PARAM.PORT_LISTERNER}"
        else:
            return f"tcp:{IP}:{PARAM.PORT_MASTER + (droneID-1)*10}"

    def manualSearch(self, droneID, step=0.01):
        print(f"@@@@ Manual search\n\tDrone ID: {droneID}\n\tPress a,s,d,w to move the drone\n\tPress e to sense\n\tPress q to quit")
        while True:
            key = input()
            if key == "q":
                break
            elif key == "e":
                print(f"@@@@ Sensing with drone {droneID}")
                 # Sense
                response = requests.post(PARAM.URL_SENSE, json={"drone_id": droneID}).json()["sense_status"]
                print(f"\t\t{response}")
            elif key == "a":
                print(f"@@@@ Moving drone {droneID} west 100m")
                pos = self.drones[droneID].get_position()
                pos.lon -= step
                self.drones[droneID].send_to_waypoint(pos)
            elif key == "d":
                print(f"@@@@ Moving drone {droneID} east 100m")
                pos = self.drones[droneID].get_position()
                pos.lon += step
                self.drones[droneID].send_to_waypoint(pos)
            elif key == "w":
                print(f"@@@@ Moving drone {droneID} north 100m")
                pos = self.drones[droneID].get_position()
                pos.lat += step
                self.drones[droneID].send_to_waypoint(pos)
            elif key == "s":
                print(f"@@@@ Moving drone {droneID} south 100m")
                pos = self.drones[droneID].get_position()
                pos.lat -= step
                self.drones[droneID].send_to_waypoint(pos)
            elif key in ["1", "2", "3", "4", "5"]:
                print(f"@@@@ Switching to drone {key}")
                droneID = int(key)
            else:
                continue

class SimpleSearch:
    def __init__(self, drone : Drone):
        self.drone = drone

    def search(self):
        limit_north = PARAM.limit_north
        limit_south = PARAM.limit_south
        limit_east = PARAM.limit_east
        limit_west = PARAM.limit_west

        pNW = geoLoc(limit_north, limit_west)
        pNE = geoLoc(limit_north, limit_east)
        pSW = geoLoc(limit_south, limit_west)

        latStepNbr = int(pNW.distTo(pNE) // PARAM.sensorRange + 1)
        lonStepNbr = int(pNW.distTo(pSW) // PARAM.sensorRange + 1)

        lat_points = np.linspace(limit_south, limit_north, latStepNbr).tolist()
        lon_points = np.linspace(limit_west, limit_east, lonStepNbr).tolist()
        grid_points = [geoLoc(lat, lon, PARAM.takeOffAltitude) for lat in lat_points for lon in (lon_points if lat_points.index(lat) % 2 == 0 else lon_points[::-1])]
        for point in grid_points:
            self.drone.gotoWP(point)
            self.sense()
    
    def sense(self):
        result =  requests.post(PARAM.URL_SENSE, json={"drone_id": self.drone.sysID}).json()["sense_status"]
        pos = self.drone.get_position()
        if result["state"] == "found":
            self.drone.printInfo(f"Rhino found at {pos}")
            self.sense() # Sense again to check if multiple rhinos are in range 
        elif result["state"] == "out_of_range":
            pass
        else:
            self.drone.printInfo(f"Rhino in range at {pos}")
            self.proximitySearch(geoCircle(pos, result["distance"]))

    def proximitySearch(self, circle : geoCircle):
        offset = PARAM.foundThreshold
        p = []
        p.append(circle.center.offset(-offset, offset))
        p.append(circle.center.offset(offset, offset))
        p.append(circle.center.offset(offset, -offset))
        p.append(circle.center.offset(-offset, -offset))

        circles = []
        for point in p:
            self.drone.gotoWP(point)
            rep = requests.post(PARAM.URL_SENSE, json={"drone_id": self.drone.sysID}).json()["sense_status"]
            if rep["state"] == "found":
                self.drone.printInfo(f"Rhino found at {point}")
                self.sense()
                return
            elif rep["state"] == "in_range":
                circles.append(geoCircle(point, rep["distance"]))
            else:
                pass
        
        if len(circles) >= 2:
            intersection = circle.intersection3circle(circles[0], circles[1])
            self.drone.gotoWP(intersection)
            self.sense()
        elif len(circles) == 1:
            self.drone.gotoWP(circles[0].center)
            self.proximitySearch(circles[0])
        else:
            raise ValueError(f"Unexpected number of circles: {len(circles)}")

if __name__ == "__main__":
    dm = DroneManager()
    # dm.createSwarm(5, takeoff=True, listenOnly=False)
    dm.createSwarm(5, takeoff=False, listenOnly=False)
    
    # center = dm.drones[1].get_position()
    # l = 15
    # square = itertools.cycle([center.offset(-l, l), center.offset(l, l), center.offset(l, -l), center.offset(-l, -l)])
    # while True:
    #     dm.drones[1].gotoWP(next(square))
        

    searcher = SimpleSearch(dm.drones[1])
    searcher.search()

    # for droneID in dm.getDroneIDs():
    #     print(dm.get_drone_position(droneID))


    # dm.send_drone_to_waypoint(1, geoLoc(0.05791118977016864, 36.91820202292705, 10))

    
   

    