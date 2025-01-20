# TeachingRhinoSearch

## Overview
This software was developped to support an outreach/teaching activity at Kenyatta University (Kenya) during the WildDrone hackathon 2025. It is a small game inspired from the need the Ol Pejeta conservancy has to survey all its rhinos every three days and how drones could potentially provide support to this task. At the same time this game aims at introducing the Ardupilot autopilot and learn how to interact with UAVs in simulation (SITL).

The game unfolds on a map of Ol Pejeta, on which a certain number of rhino are hidden. The goal for each team is to find as many rhinos as possible using thier search drone. Each drone is equipped with a "rhino range finder", telling each team, on activation, if a rhino is detected (range is limited) and at what distance. If a team overflies a rhino and detects it, then the rhino is found and shown on the map. Teams interact with their drone using mavlink.

## Launch
### SITL
Assuming:
- $HOME/.config/ardupilot/locations.txt exists, with a location named OlPejetaStables.
- the ardupilot repository is cloned at `/home/wp23610/Documents/GitHub/ardupilot` and is installed in a conda environment named `sitl` 
- 5 drones are needed

```
cd /home/wp23610/Documents/GitHub/ardupilot
conda activate sitl
sim_vehicle.py -v Copter --map --console --count 5 --auto-sysid --location OlPejetaStables --auto-offset-line 90,10
```
Add UPD output for Mission Planner (assuming Mission Planner is running on a machine with address REMOTE_IP)
```
output add {REMOTE_IP}:14550
```
Start all drones by running `mainSwarmTakeOff.py` in the `rhino` environment. 

### Game
Run `mainGame.py` in the `rhino` environment.

### Example search algorithm 
Run `mainSearchExample.py` in the `rhino` environment.

## Testing
### Sensor server
Adjust IP address and run `testSensServer.py`

### PyMavlink
Adjust IP address and run `testPyMavlink.py`

## Misc
### Adjusting simulation speed
```
vehicle <ID> # to select vehicle
param set SIM_SPEEDUP <factor>
param show SIM_SPEEDUP
```

### Mavproxy swarm module
Once mavproxy is launched, start the swarm module for convinience.
```
module load swarm
```

 
