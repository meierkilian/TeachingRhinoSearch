from pymavlink import mavutil
from dataTypes import geoLoc

class Drone:
    def __init__(self, IP="0.0.0.0", portNumber=14550):
        self.mavLinkHandle = mavutil.mavlink_connection(f'udpin:{IP}:{portNumber}')
        self.mavLinkHandle.wait_heartbeat()
        # self.mavLinkHandle.set_mode("GUIDED")
        # self.mavLinkHandle.arducopter_arm()
        # self.take_off(10)

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
        self.mavLinkHandle.mav.command_long_send(
            self.mavLinkHandle.target_system,
            self.mavLinkHandle.target_component,
            mavutil.mavlink.SET_POSITION_TARGET_GLOBAL_INT,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            3576, # use position, (see POSITION_TARGET_TYPEMASK enum)
            int(waypoint.lat*1e7),
            int(waypoint.lon*1e7),
            int(waypoint.alt*1e3),
            0, 0, 0,
            0, 0, 0,
            0, 0
        )

class DroneManager:
    def __init__(self):
        self.drones = {}

    def add_drone(self, droneID, IP="0.0.0.0", portNumber=14550):
        self.drones[droneID] = Drone(IP, portNumber)

    def get_drone_position(self, droneID):
        return self.drones[droneID].get_position()

    def send_drone_to_waypoint(self, droneID, waypoint):
        self.drones[droneID].send_to_waypoint(waypoint)

if __name__ == "__main__":
    dm = DroneManager()
    dm.add_drone("Drone1")
    dm.send_drone_to_waypoint("Drone1", geoLoc(-35.363393573486036, 149.16265183485982, 10))
    while True:
        pos = dm.get_drone_position("Drone1")
        print(pos.lat, pos.lon, pos.alt)

