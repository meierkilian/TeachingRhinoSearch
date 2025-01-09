from drones import DroneManager, SimpleSearch
import param as PARAM

dm = DroneManager()
dm.createSwarm(PARAM.droneNbr, takeoff=False, listenOnly=False)
        
searcher = SimpleSearch(dm.drones[1])
searcher.search()
