import threading
import os
import time
from backend.api.main import app
from fastapi.testclient import TestClient

print(f"Process ID: {os.getpid()}")

with TestClient(app) as client:
    # Let threads initialize
    time.sleep(1)
    
    print("Threads:")
    for t in threading.enumerate():
        print(f" - {t.name} (Alive: {t.is_alive()})")

    print("\nHealth Check Response:")
    print(client.get("/health").json())
