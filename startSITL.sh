cd /home/wp23610/Documents/GitHub/ardupilot
conda activate sitl
# Assuming $HOME/.config/ardupilot/locations.txt exists
# sim_vehicle.py -v copter --console --map -w
sim_vehicle.py -v Copter --map --console --count 5 --auto-sysid --location OlPejetaStables --auto-offset-line 90,10
# sim_vehicle.py -v Copter --map --console --count 5 --auto-sysid --location OlPejetaStables --swarm /home/wp23610/Documents/GitHub/TeachingRhinoSearch/src/swarminit.text


module load swarm
param set SIM_SPEEDUP 5
param show SIM_SPEEDUP

# To connect from mission planner add ouput on SITL and connect via UDP 
output add {REMOTE_IP}:14550
output add 192.168.1.128:14550