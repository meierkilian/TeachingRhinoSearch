cd /home/wp23610/Documents/GitHub/ardupilot
conda activate sitl
# Assuming $HOME/.config/ardupilot/locations.txt exists
# sim_vehicle.py -v copter --console --map -w
sim_vehicle.py -v Copter --map --console --count 5 --auto-sysid --location OlPejetaStables --auto-offset-line 90,10
