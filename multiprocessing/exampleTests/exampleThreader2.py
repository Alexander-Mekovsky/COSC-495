import threading
import time
import random
from queue import Queue
from collections import defaultdict
import statistics
import numpy as np

# Statistical data for API call simulations
api_call_stats = {
    'average': 3.5081841786702475,
    'std_dev': 0.8198141376325683,
    'min': 2.2610180377960205,
    'max': 4.956922769546509
}

# Initialize lists for analysis
active_times = []
start_times = []
end_times = []

def simulate_api_call_duration():
    """Simulates an API call duration based on statistical data."""
    duration = random.normalvariate(api_call_stats['average'], api_call_stats['std_dev'])
    return max(api_call_stats['min'], min(duration, api_call_stats['max']))

def worker(worker_id, start_signal_queue):
    while True:
        signal = start_signal_queue.get()
        if signal is None:
            start_signal_queue.task_done()
            break  # Shutdown signal received

        start_time = time.time()
        start_times.append(start_time)

        call_duration = simulate_api_call_duration()
        time.sleep(call_duration)  # Simulate the API call duration

        end_time = time.time()
        end_times.append(end_time)
        active_times.append(call_duration)

        start_signal_queue.task_done()
        print(f"Worker {worker_id} completed an API call in {call_duration:.2f} seconds.")

def scheduler(start_signal_queue, call_rate_per_second, total_runtime):
    for _ in range(int(total_runtime * call_rate_per_second)):
        start_signal_queue.put('start')  # Signal workers to start an API call
        time.sleep(1 / call_rate_per_second)

    # Send shutdown signal to all workers
    for _ in range(num_workers):
        start_signal_queue.put(None)

# Simulation parameters
num_workers = 18  # Number of workers
call_rate_per_second = 8  # Target API calls per second
total_runtime = 60  # Duration of simulation in seconds

# Queue for coordination between scheduler and workers
start_signal_queue = Queue()

# Start workers
workers = [threading.Thread(target=worker, args=(i, start_signal_queue)) for i in range(num_workers)]
for w in workers:
    w.start()

# Start scheduler
scheduler_thread = threading.Thread(target=scheduler, args=(start_signal_queue, call_rate_per_second, total_runtime))
scheduler_thread.start()

# Wait for all threads to complete
for w in workers:
    w.join()
scheduler_thread.join()

# Analysis
total_calls_made = len(active_times)
total_active_time = sum(active_times)
total_runtime_observed = max(end_times) - min(start_times)
average_calls_per_second = total_calls_made / total_runtime_observed
downtime = total_runtime_observed - total_active_time

print(f"Total Calls Made: {total_calls_made}")
print(f"Total Active Time: {total_active_time:.2f} seconds")
print(f"Total Runtime Observed: {total_runtime_observed:.2f} seconds")
print(f"Average Calls per Second: {average_calls_per_second:.2f}")
print(f"Downtime: {downtime:.2f} seconds")

calls_per_second = defaultdict(int)
for start_time in start_times:
    second = int(start_time)  # Convert to integer to group by second
    calls_per_second[second] += 1

cps_counts = list(calls_per_second.values())  # Convert to list for statistical analysis

# Handle case with no calls made to avoid errors in statistical calculations
if cps_counts:
    average_cps = statistics.mean(cps_counts)
    median_cps = statistics.median(cps_counts)
    mode_cps = statistics.mode(cps_counts)
    min_cps = np.min(cps_counts)
    max_cps = np.max(cps_counts)
    std_dev_cps = statistics.stdev(cps_counts) if len(cps_counts) > 1 else 0  # Std. dev requires at least 2 data points
else:
    average_cps = median_cps = mode_cps = std_dev_cps = 0

# Displaying the calculated statistics
print(f"\nCalls Per Second Analysis:")
print(f"Average Calls Per Second: {average_cps:.2f}")
print(f"Median Calls Per Second: {median_cps:.2f}")
print(f"Max Calls Per Second: {max_cps:.2f}")
print(f"Min Calls Per Second: {min_cps:.2f}")
print(f"Mode Calls Per Second: {mode_cps}")
print(f"Standard Deviation of Calls Per Second: {std_dev_cps:.2f}")

calls_within_next_second = []

# Iterate through each start time
for i, current_start in enumerate(start_times):
    # Count how many other calls started within 1 second after the current call's start time
    count = sum(1 for future_start in start_times[i+1:] if 0 <= future_start - current_start < 1)
    calls_within_next_second.append(count)
    
if calls_within_next_second:
    avg_within_next_second = statistics.mean(calls_within_next_second)
    median_within_next_second = statistics.median(calls_within_next_second)
    mode_within_next_second = statistics.mode(calls_within_next_second)
    max_within_next_second = np.max(calls_within_next_second)
    min_within_next_second = np.min(calls_within_next_second)
    std_dev_within_next_second = statistics.stdev(calls_within_next_second) if len(calls_within_next_second) > 1 else 0
else:
    avg_within_next_second = median_within_next_second = mode_within_next_second = std_dev_within_next_second = 0

# Displaying the calculated statistics for calls within the next second
print("\nAnalysis of Calls Starting Within 1 Second After Each Call's Start Time:")
print(f"Average Calls Starting Within Next Second: {avg_within_next_second:.2f}")
print(f"Median Calls Starting Within Next Second: {median_within_next_second:.2f}")
print(f"Mode of Calls Starting Within Next Second: {mode_within_next_second}")
print(f"Max of Calls Starting Within Next Second: {max_within_next_second}")
print(f"Min of Calls Starting Within Next Second: {min_within_next_second}")
print(f"Standard Deviation of Calls Starting Within Next Second: {std_dev_within_next_second:.2f}")
