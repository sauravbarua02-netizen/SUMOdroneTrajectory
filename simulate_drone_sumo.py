import traci
from PIL import Image, ImageDraw
import os
import csv

# ===========================
# Configuration
# ===========================
SUMO_BINARY = "sumo-gui"  # or "sumo-gui"
SUMO_CONFIG = r"C:\Users\ASUS\Desktop\Course_25_1\SUMO_practice\Pratunam_intersection\osm.sumocfg"  # replace with your SUMO config
STEP_LENGTH = 1.0  # simulation step in seconds

# Drone (camera) settings
CAM_X, CAM_Y = 288.84, 187.33  # initial drone center in meters
CAM_SPEED_X, CAM_SPEED_Y = 0.0, 0.0  # optional drone movement per step
SCALE = 5  # pixels per meter
IMG_WIDTH, IMG_HEIGHT = 1920, 1080

OUTPUT_DIR = "drone_output"
CSV_FILE = os.path.join(OUTPUT_DIR, "drone_trajectories.csv")
FRAME_DIR = os.path.join(OUTPUT_DIR, "frames")

# ===========================
# Helper functions
# ===========================
def world_to_pixel(x, y, cam_x, cam_y):
    px = IMG_WIDTH / 2 + (x - cam_x) * SCALE
    py = IMG_HEIGHT / 2 - (y - cam_y) * SCALE  # invert y-axis for image
    return int(px), int(py)

# ===========================
# Setup output directories
# ===========================
os.makedirs(FRAME_DIR, exist_ok=True)

# ===========================
# Start SUMO with TraCI
# ===========================
traci.start([SUMO_BINARY, "-c", SUMO_CONFIG, "--step-length", str(STEP_LENGTH)])

# Open CSV for trajectories
with open(CSV_FILE, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["time", "veh_id", "x", "y", "speed", "lane_id"])

    frame_count = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        sim_time = traci.simulation.getTime()

        # Create a blank image for drone view
        img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Collect vehicle data
        for veh_id in traci.vehicle.getIDList():
            x, y = traci.vehicle.getPosition(veh_id)
            speed = traci.vehicle.getSpeed(veh_id)
            lane_id = traci.vehicle.getLaneID(veh_id)
            writer.writerow([sim_time, veh_id, x, y, speed, lane_id])

            # Draw vehicle on image (simple rectangle)
            px, py = world_to_pixel(x, y, CAM_X, CAM_Y)
            w, h = 8, 16  # size in pixels
            draw.rectangle([px - w//2, py - h//2, px + w//2, py + h//2], outline="red", fill="red")

        # Save drone view frame
        img.save(os.path.join(FRAME_DIR, f"frame_{frame_count:06d}.png"))

        # Advance drone position (optional)
        CAM_X += CAM_SPEED_X * STEP_LENGTH
        CAM_Y += CAM_SPEED_Y * STEP_LENGTH

        frame_count += 1
        traci.simulationStep()  # advance SUMO simulation

traci.close()
print(f"Drone simulation complete! Trajectories saved in {CSV_FILE} and frames in {FRAME_DIR}")
