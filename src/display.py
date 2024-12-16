import tkinter as tk
from tkinter import ttk
from rhinoLoc import RhinoLoc

class DroneGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Rhino Search")
        
        self.map_image = tk.PhotoImage(file="ressources/mapOlPejeta.png")
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
        
        self.drones = {}

        self.drone_icon = tk.PhotoImage(file="ressources/droneIcon.png")
        self.drone_icon = self.drone_icon.subsample(self.drone_icon.width() // 40, self.drone_icon.height() // 40)

        self.rhino_icon = tk.PhotoImage(file="ressources/rhinoIcon.png")
        self.rhino_icon = self.rhino_icon.subsample(self.rhino_icon.width() // 40, self.rhino_icon.height() // 40)

        self.limit_north = 0.11518
        self.limit_south = -0.04120
        self.limit_west = 36.81828
        self.limit_east = 37.04487

        self.rhinoLoc = RhinoLoc(1, (self.limit_south, self.limit_west), (self.limit_north, self.limit_east))
        self.rhino_positions = self.rhinoLoc.get_rhino_positions()
        self.show_rhino = True
        
        self.update_positions()

    def convert_to_canvas_coords(self, lat, lon):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = (lon - self.limit_west) / (self.limit_east - self.limit_west) * canvas_width
        y = (self.limit_north - lat) / (self.limit_north - self.limit_south) * canvas_height
        return x, y
    
    def update_positions(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_image)
        for _, drone_data in self.drones.items():
            lat, lon = drone_data["position"]
            x, y = self.convert_to_canvas_coords(lat, lon)
            self.canvas.create_image(x, y, anchor=tk.CENTER, image=self.drone_icon)
        
        if self.show_rhino:
            for rlat, rlon in self.rhino_positions:
                rx, ry = self.convert_to_canvas_coords(rlat, rlon)
                self.canvas.create_image(rx, ry, anchor=tk.CENTER, image=self.rhino_icon)
        
        self.root.after(100, self.update_positions)
    
    def reset_game(self):
        # self.drones = {}
        # self.leaderboard.delete(*self.leaderboard.get_children())
        self.rhinoLoc.regenerate_rhino_positions()
        self.rhino_positions = self.rhinoLoc.get_rhino_positions()
        print(f"Dist to rhino : {self.rhinoLoc.distance_to_closest_rhino(self.drones['Drone1']['position'])}")
        
    def toggle_rhino_display(self):
        self.show_rhino = not self.show_rhino
    
    def add_drone(self, drone_id):
        self.drones[drone_id] = {"position": (0.02661, 36.91492), "rhinos": 0}
        self.leaderboard.insert("", "end", values=(drone_id, 0))
    
    def update_drone_position(self, drone_id, x, y):
        if drone_id in self.drones:
            self.drones[drone_id]["position"] = (x, y)
    
    def update_drone_rhinos(self, drone_id, rhinos):
        if drone_id in self.drones:
            self.drones[drone_id]["rhinos"] = rhinos
            for item in self.leaderboard.get_children():
                if self.leaderboard.item(item, "values")[0] == drone_id:
                    self.leaderboard.item(item, values=(drone_id, rhinos))

if __name__ == "__main__":
    root = tk.Tk()
    gui = DroneGUI(root)
    gui.add_drone("Drone1")
    gui.add_drone("Drone2")
    root.mainloop()