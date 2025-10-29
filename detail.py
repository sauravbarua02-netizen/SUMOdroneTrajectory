import pandas as pd
import numpy as np

def calculate_traffic_metrics(df):
    """
    Calculate 60-second aggregated traffic metrics
    """
    # Convert time to integer
    df['time_sec'] = df['time'].astype(int)
    
    # Sort by vehicle and time for proper tracking
    df = df.sort_values(['veh_id', 'time_sec'])
    
    # Calculate time intervals
    max_time = df['time_sec'].max()
    intervals = list(range(0, max_time + 60, 60))
    
    results = []
    
    for i in range(len(intervals) - 1):
        start, end = intervals[i], intervals[i + 1]
        
        # Data for current interval
        interval_data = df[(df['time_sec'] >= start) & (df['time_sec'] < end)]
        
        if interval_data.empty:
            continue
        
        # Basic metrics
        vehicle_count = interval_data['veh_id'].nunique()
        avg_speed = interval_data['speed'].mean()
        
        # Calculate travel times for vehicles with multiple observations
        travel_times = []
        for vehicle in interval_data['veh_id'].unique():
            vehicle_data = interval_data[interval_data['veh_id'] == vehicle]
            
            if len(vehicle_data) > 1:
                # Calculate time difference between first and last observation
                time_diff = vehicle_data['time_sec'].max() - vehicle_data['time_sec'].min()
                if time_diff > 0:
                    travel_times.append(time_diff)
        
        avg_travel_time = np.mean(travel_times) if travel_times else 0
        
        results.append({
            'interval': f"{start}-{end}",
            'start_time': start,
            'end_time': end,
            'vehicle_count': vehicle_count,
            'avg_travel_time_sec': round(avg_travel_time, 2),
            'avg_speed': round(avg_speed, 2)
        })
    
    return pd.DataFrame(results)

# Read and process data
df = pd.read_excel(r"C:\Users\ASUS\Desktop\Course_25_1\SUMO_practice\Pratunam_intersection\drone_output\drone_trajectories.xlsx")
metrics_df = calculate_traffic_metrics(df)

# Display results
print("60-Second Aggregated Traffic Metrics")
print("=" * 70)
print(f"{'Interval':<12} {'Vehicles':<10} {'Avg Travel Time':<16} {'Avg Speed':<10}")
print("-" * 70)

for _, row in metrics_df.iterrows():
    print(f"{row['interval']:<12} {row['vehicle_count']:<10} {row['avg_travel_time_sec']:<16} {row['avg_speed']:<10}")

# Plot results (optional - requires matplotlib)
try:
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Vehicle count over time
    ax1.bar(range(len(metrics_df)), metrics_df['vehicle_count'])
    ax1.set_title('Vehicle Count per 60-Second Interval')
    ax1.set_ylabel('Number of Vehicles')
    ax1.set_xlabel('Time Interval')
    
    # Average speed over time
    ax2.plot(metrics_df['avg_speed'], marker='o')
    ax2.set_title('Average Speed per 60-Second Interval')
    ax2.set_ylabel('Speed (m/s)')
    ax2.set_xlabel('Time Interval')
    ax2.grid(True, alpha=0.3)
    
    # Average travel time over time
    ax3.plot(metrics_df['avg_travel_time_sec'], marker='s', color='green')
    ax3.set_title('Average Travel Time per 60-Second Interval')
    ax3.set_ylabel('Travel Time (seconds)')
    ax3.set_xlabel('Time Interval')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('traffic_metrics_plot.png', dpi=300, bbox_inches='tight')
    plt.show()
    
except ImportError:
    print("\nMatplotlib not available for plotting")

# Save detailed results
metrics_df.to_csv('detailed_traffic_metrics.csv', index=False)
print(f"\nDetailed results saved to 'detailed_traffic_metrics.csv'")