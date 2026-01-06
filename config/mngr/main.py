import os
import sys
import time

# Print version
print(f"Python is active. Version: {sys.version}")

# Periodic print
counter = 0
while 1:
    print(f"Counter: {counter}")
    counter += 1
    time.sleep(1) # 1 sec