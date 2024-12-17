from pymavlink import mavutil
from pymavlink.mavutil import mavlink as mavlink
from dataTypes import geoLoc
import time

class Drone:
    def __init__(self, IP="localhost", portNumber=5762):
        print(f"Connecting to drone at {IP}:{portNumber}")
        self.mavLinkHandle = mavutil.mavlink_connection(f'udpin:{IP}:{portNumber}')
        self.mavLinkHandle.wait_heartbeat()
        print(self.get_position())
        # time.sleep(1)
        # self.mavLinkHandle.set_mode("GUIDED")
        # time.sleep(1)
        # self.mavLinkHandle.arducopter_arm()
        # time.sleep(1)tcp
        # self.take_off(10)
        # time.sleep(1)

    def take_off(self, altitude):
        self.mavLinkHandle.mav.command_long_send(
            self.mavLinkHandle.target_system,
            self.mavLinkHandle.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, altitude
        )    

    def get_position(self):
        msg = self.mavLinkHandle.recv_match(type='GLOBAL_POSITION_INT', blocking=True).to_dict()
        return geoLoc(msg['lat']*1e-7, msg['lon']*1e-7, msg['relative_alt']*1e-3)

    def send_to_waypoint(self, waypoint):
        self.mavLinkHandle.mav.command_int_send(
            self.mavLinkHandle.target_system,
            self.mavLinkHandle.target_component,
            6,
            mavutil.mavlink.MAV_CMD_DO_REPOSITION,
            0, 0,0, -1, 1, 0,
            int(waypoint.lat * 1e7), int(waypoint.lon * 1e7), float(waypoint.alt))
        
    def get_sysID(self):
        return self.mavLinkHandle.target_system
        
    # def is_waypoint_reached(self, waypoint, threshold=10):
    #     pos = self.get_position()

class DroneManager:
    def __init__(self):
        self.drones = {}

    def add_drone(self, IP="127.0.0.1", portNumber=5762):
        drone = Drone(IP, portNumber)
        id = drone.get_sysID()
        self.drones[id] = Drone(IP, portNumber)

    def get_drone_position(self, droneID):
        return self.drones[droneID].get_position()

    def send_drone_to_waypoint(self, droneID, waypoint):
        self.drones[droneID].send_to_waypoint(waypoint)

    def createSwarm(self, n):
        for i in range(n):
            self.add_drone(portNumber=5762 + i*10)

    def getDroneIDs(self):
        return self.drones.keys()

if __name__ == "__main__":
    # dm = DroneManager()
    # dm.createSwarm(5)
    # print(dm.getDroneIDs())

    # for droneID in dm.getDroneIDs():
    #     input(f"Press Enter to send {droneID} to waypoint")
    #     dm.send_drone_to_waypoint(droneID, geoLoc(0.027467533748910547, 36.90286865957662, 10))

    # while True:
    #     pos = dm.get_drone_position(droneID = 1)
    #     print(pos.lat, pos.lon, pos.alt)

    while True:
        port = input("Enter port number: ")
        drone = Drone(portNumber=port)
        id = drone.get_sysID()
        print(f"drone sysID: {id}")
        print(drone.get_position())