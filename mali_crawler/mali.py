# mali.py
import sys
import ctypes
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='simulation.log',
    level=logging.INFO,
    format='%(asctime)s [SIMULATION] %(message)s'
)

def simulate_root_access():
    """Simulate privilege escalation without actual system changes"""
    logging.info("Attempting simulated root access")
    print("[SIMULATION] Would now execute: sudo rm -rf / --no-preserve-root")
    print("Safety override active - No actual files modified")

def alarming_message():
    """Show controlled warning message"""
    if sys.platform == 'win32':
        ctypes.windll.user32.MessageBoxW(
            0, 
            "This is a security simulation\nNo actual harm done", 
            "Security Test", 
            0x40  # Information icon
        )
    else:
        print("\033[91mSECURITY SIMULATION: Mock system compromise detected\033[0m")

def fake_data_exfiltration():
    """Simulate data theft without real network calls"""
    fake_data = "SIMULATED SENSITIVE DATA: " + datetime.now().isoformat()
    logging.info(f"Would exfiltrate: {fake_data[:30]}...")
    with open("simulated_data.txt", "w") as f:
        f.write(fake_data)
    print("Data simulation file created: simulated_data.txt")

if __name__ == "__main__":
    alarming_message()
    simulate_root_access()
    fake_data_exfiltration()
    print("Simulation complete. Check simulation.log for details")
