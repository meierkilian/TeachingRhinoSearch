import tkinter as tk
from tkinter import ttk
from rhinoLoc import RhinoLoc
from drones import DroneManager
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import param as PARAM

rhinoLoc = None 
droneManager = None

class DroneGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Rhino Search")
        
        self.map_image = tk.PhotoImage(file="ressources/mapOlPejeta.png")
        self.map_image = self.map_image.zoom(2, 2)
        # https://www.openstreetmap.org/export#map=16/0.02800/36.90505
        # Use Export tab for map limit and Share tab for map image
        image_width = self.map_image.width()
        image_height = self.map_image.height()
        
        self.map_frame = tk.Frame(self.root, width=image_width, height=image_height)
        self.map_frame.grid(row=0, column=0, padx=10, pady=10)
        
        self.leaderboard_frame = tk.Frame(self.root)
        self.leaderboard_frame.grid(row=0, column=1, padx=10, pady=10)
        
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.canvas = tk.Canvas(self.map_frame, width=image_width, height=image_height, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_image)
        
        self.leaderboard = ttk.Treeview(self.leaderboard_frame, columns=("drone", "rhinos"), show="headings")
        self.leaderboard.heading("drone", text="Drone")
        self.leaderboard.heading("rhinos", text="Rhinos Found")
        self.leaderboard.pack()
        
        self.reset_button = tk.Button(self.control_frame, text="Reset Game", command=self.reset_game)
        self.reset_button.grid(row=0, column=0, padx=5)
        
        self.toggle_rhino_button = tk.Button(self.control_frame, text="Toggle Rhino Display", command=self.toggle_rhino_display)
        self.toggle_rhino_button.grid(row=0, column=1, padx=5)
        
        self.sense_button = tk.Button(self.control_frame, text="Sense Rhinos", command=self.print_sense_status)
        self.sense_button.grid(row=0, column=2, padx=5)

        global droneManager
        droneManager = DroneManager()
        droneManager.createSwarm(PARAM.droneNbr, takeoff=False, listenOnly=True)
        for drone_id in droneManager.getDroneNames():
            self.leaderboard.insert("", "end", values=(drone_id, 0))

        self.drone_icon = tk.PhotoImage(file="ressources/droneIcon.png")
        self.drone_icon = self.drone_icon.subsample(self.drone_icon.width() // 40, self.drone_icon.height() // 40)

        self.rhino_icon_green = tk.PhotoImage(file="ressources/rhinoIcon_green.png")
        self.rhino_icon_green = self.rhino_icon_green.subsample(self.rhino_icon_green.width() // 40, self.rhino_icon_green.height() // 40)

        self.rhino_icon_red = tk.PhotoImage(file="ressources/rhinoIcon_red.png")
        self.rhino_icon_red = self.rhino_icon_red.subsample(self.rhino_icon_red.width() // 40, self.rhino_icon_red.height() // 40)
        
        self.limit_north = PARAM.limit_north
        self.limit_south = PARAM.limit_south
        self.limit_west = PARAM.limit_west
        self.limit_east = PARAM.limit_east

        global rhinoLoc
        rhinoLoc = RhinoLoc(PARAM.rhinoNbr, (self.limit_south, self.limit_west), (self.limit_north, self.limit_east))
        self.show_rhino = True
        
        self.update()

    def convert_to_canvas_coords(self, lat, lon):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = (lon - self.limit_west) / (self.limit_east - self.limit_west) * canvas_width
        y = (self.limit_north - lat) / (self.limit_north - self.limit_south) * canvas_height
        return x, y
    
    def update(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_image)
        scores = {}
        for drone, name in zip(droneManager.getDroneIDs(), droneManager.getDroneNames()):
            pos = droneManager.get_drone_position(drone)
            scores[name] = droneManager.get_rhinos_found(drone)
            x, y = self.convert_to_canvas_coords(pos.lat, pos.lon)
            self.canvas.create_image(x, y, anchor=tk.CENTER, image=self.drone_icon)
            self.canvas.create_text(x, y, text=drone, fill="white", font=("HelveticaBold", 10))

        scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
        for item, droneID, score in zip(self.leaderboard.get_children(), scores.keys(), scores.values()):
            self.leaderboard.item(item, values=(droneID, score))
        
        for pos, found in zip(rhinoLoc.get_rhino_positions(), rhinoLoc.get_rhino_found()):
            if self.show_rhino or found:
                rx, ry = self.convert_to_canvas_coords(pos.lat, pos.lon)
                if found:
                    self.canvas.create_image(rx, ry, anchor=tk.CENTER, image=self.rhino_icon_green)
                else:
                    self.canvas.create_image(rx, ry, anchor=tk.CENTER, image=self.rhino_icon_red)
        
        self.root.after(100, self.update)
    
    def reset_game(self):
        for drone in droneManager.getDroneIDs():
            droneManager.reset_rhinos_found(drone)
        rhinoLoc.regenerate_rhino_positions()
        
    def toggle_rhino_display(self):
        self.show_rhino = not self.show_rhino

    def print_sense_status(self):
        for drone in droneManager.getDroneIDs():
            sense_status = rhinoLoc.senseRhino(droneManager.get_drone_position(drone))
            print(f"Drone {drone} sense status: {sense_status}")
    
    def run_server(self):
        server_address = ('', 8080)
        httpd = HTTPServer(server_address, RequestHandler)
        print("HTTP server running on port 8080")
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/handshake":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": "Hello from the Rhino Search server!"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/sense":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            drone_id = data.get("drone_id")
            if drone_id:
                sense_status = rhinoLoc.senseRhino(droneManager.get_drone_position(drone_id))
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"sense_status": sense_status}
                if sense_status["state"] == "found":
                    droneManager.rhinoFound(drone_id)
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"error": "Missing drone_id parameter"}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()



if __name__ == "__main__":
    root = tk.Tk()
    gui = DroneGUI(root)
    gui.run_server()
    root.mainloop()