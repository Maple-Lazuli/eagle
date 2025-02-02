import datetime
import time

time_scale = 1.00000001
time_scale = 1.0000001
time_scale = 1.000001

current = datetime.datetime.now().timestamp()
scaled = current * time_scale

if __name__ == "__main__":
    while True:
        time.sleep(1)
        current = datetime.datetime.now().timestamp()
        scaled = scaled * time_scale
        print(f'{datetime.datetime.fromtimestamp(current)} ----> {datetime.datetime.fromtimestamp(scaled)}')
