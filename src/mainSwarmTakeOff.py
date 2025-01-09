from drones import DroneManager
import param as PARAM

dm = DroneManager()
dm.createSwarm(PARAM.droneNbr, takeoff=True, listenOnly=False)