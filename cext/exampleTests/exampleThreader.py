import threading
import time
import random
import statistics

# Statistical data setup (simplified)
average = 3.508
std_dev = 0.8198
min_time = 2.261
max_time = 4.956

# Global lists to store times for analysis
waiting_times = []
active_times = []

def simulate_api_call_duration():
    duration = random.normalvariate(average, std_dev)
    return max(min_time, min(duration, max_time))

def api_call(worker_id, interval, run_time):
    end_time = time.time() + run_time
    while time.time() < end_time:
        start_wait = time.time()
        next_call_time = start_wait + interval
        call_duration = simulate_api_call_duration()
        
        # Log active time
        active_times.append(call_duration)

        # Simulate API call
        time.sleep(call_duration)  # Simulate the API call duration

        # Calculate and log waiting time
        time_to_wait = next_call_time - time.time()
        if time_to_wait > 0:
            waiting_times.append(time_to_wait)
            time.sleep(time_to_wait)
            
        print(f"Worker {worker_id} making an API call. Duration: {call_duration:.2f} seconds, Waiting: {time_to_wait:.2f} seconds.")

# Parameters
workers_count = 8
interval = 1.0 / 8
run_time = 60  # Run the simulation for 10 seconds

# Start workers
workers = []
for i in range(workers_count):
    worker = threading.Thread(target=api_call, args=(i, interval, run_time))
    workers.append(worker)
    worker.start()

for worker in workers:
    worker.join()

# Calculate and print statistics
total_waiting_time = sum(waiting_times)
total_active_time = sum(active_times)
print(f"Total Waiting Time: {total_waiting_time:.2f} seconds")
print(f"Total Active Time: {total_active_time:.2f} seconds")
print(f"Total Downtime: {(run_time * workers_count) - total_active_time:.2f} seconds")
print(f"API Calls Made: {len(active_times)}")
print(f"API Calls per Second: {len(active_times) / run_time:.2f}")
