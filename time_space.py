import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the Excel file
df = pd.read_excel(r"C:\Users\ASUS\Desktop\Course_25_1\SUMO_practice\Pratunam_intersection\drone_output\drone_trajectories.xlsx")

# Create space-time diagram
plt.figure(figsize=(14, 10))

# Get all unique vehicle IDs
vehicle_ids = df['veh_id'].unique()
colors = plt.cm.tab20(np.linspace(0, 1, len(vehicle_ids)))

# Plot each vehicle's trajectory in space-time
for i, vehicle_id in enumerate(vehicle_ids):
    vehicle_data = df[df['veh_id'] == vehicle_id].sort_values('time')
    
    if len(vehicle_data) > 1:
        # Calculate distance traveled (arc length)
        x = vehicle_data['x'].values
        y = vehicle_data['y'].values
        time = vehicle_data['time'].values
        
        # Calculate cumulative distance from start point
        dx = np.diff(x)
        dy = np.diff(y)
        distances = np.sqrt(dx**2 + dy**2)
        cumulative_distance = np.concatenate(([0], np.cumsum(distances)))
        
        plt.plot(time, cumulative_distance, 
                color=colors[i], linewidth=2, marker='o', markersize=3,
                label=f'{vehicle_id}', alpha=0.8)

plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('Distance Traveled from Start (m)', fontsize=12)
plt.title('Space-Time Diagram: Distance vs Time for All Vehicles', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()