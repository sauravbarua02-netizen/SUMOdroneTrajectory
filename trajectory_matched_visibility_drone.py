import traci
from PIL import Image, ImageDraw
import os
import csv

# ===========================
# Configuration
# ===========================
SUMO_BINARY = "sumo-gui"  # or "sumo"
SUMO_CONFIG = r"C:\Users\ASUS\Desktop\Course_25_1\2101741 Saurav Barua\Assignment 3b- Saurav Barua\osm.sumocfg"
STEP_LENGTH = 1.0  # seconds per simulation step

# Drone (camera) settings
CAM_X, CAM_Y = 288.84, 187.33        # camera center in meters
CAM_SPEED_X, CAM_SPEED_Y = 0.0, 0.0  # drone movement per step (m/s)
SCALE = 5                            # pixels per meter
IMG_WIDTH, IMG_HEIGHT = 1920, 1080   # image size in pixels

# Derived coverage (in meters)
HALF_WIDTH_M = IMG_WIDTH / (2 * SCALE)   # 1920 / (2*5) = 192 m
HALF_HEIGHT_M = IMG_HEIGHT / (2 * SCALE) # 1080 / (2*5) = 108 m

# Output directories
OUTPUT_DIR = "drone_output"
CSV_FILE = os.path.join(OUTPUT_DIR, "drone_trajectories.csv")
FRAME_DIR = os.path.join(OUTPUT_DIR, "frames")

os.makedirs(FRAME_DIR, exist_ok=True)

# ===========================
# Helper function
# ===========================
def world_to_pixel(x, y, cam_x, cam_y):
    """Convert SUMO world coordinates to image pixel coordinates."""
    px = IMG_WIDTH / 2 + (x - cam_x) * SCALE
    py = IMG_HEIGHT / 2 - (y - cam_y) * SCALE  # invert Y-axis
    return int(px), int(py)

# ===========================
# Start SUMO via TraCI
# ===========================
traci.start([SUMO_BINARY, "-c", SUMO_CONFIG, "--step-length", str(STEP_LENGTH)])

with open(CSV_FILE, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["time", "veh_id", "x", "y", "speed", "lane_id"])

    frame_count = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        sim_time = traci.simulation.getTime()

        # Create a blank image for the drone view
        img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw the visible boundary box (optional visualization)
        draw.rectangle(
            [0, 0, IMG_WIDTH - 1, IMG_HEIGHT - 1],
            outline="black", width=2
        )

        # Collect and draw visible vehicle data
        for veh_id in traci.vehicle.getIDList():
            x, y = traci.vehicle.getPosition(veh_id)
            speed = traci.vehicle.getSpeed(veh_id)
            lane_id = traci.vehicle.getLaneID(veh_id)

            # Check if vehicle is inside visible frame
            if (CAM_X - HALF_WIDTH_M <= x <= CAM_X + HALF_WIDTH_M and
                CAM_Y - HALF_HEIGHT_M <= y <= CAM_Y + HALF_HEIGHT_M):

                # Record visible vehicle data
                writer.writerow([sim_time, veh_id, x, y, speed, lane_id])

                # Draw vehicle rectangle (visible ones only)
                px, py = world_to_pixel(x, y, CAM_X, CAM_Y)
                w, h = 8, 16  # rectangle size in pixels
                draw.rectangle(
                    [px - w//2, py - h//2, px + w//2, py + h//2],
                    outline="red", fill="red"
                )

        # Save image frame
        frame_path = os.path.join(FRAME_DIR, f"frame_{frame_count:06d}.png")
        img.save(frame_path)

        # Move drone (optional)
        CAM_X += CAM_SPEED_X * STEP_LENGTH
        CAM_Y += CAM_SPEED_Y * STEP_LENGTH

        frame_count += 1
        traci.simulationStep()

traci.close()

print(f"\n✅ Drone simulation complete!")
print(f"Visible trajectories saved in: {CSV_FILE}")
print(f"Frames saved in: {FRAME_DIR}")
print(f"Frame coverage ≈ {HALF_WIDTH_M*2:.0f} m × {HALF_HEIGHT_M*2:.0f} m")
