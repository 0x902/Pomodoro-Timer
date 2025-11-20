import streamlit as st
from pynput import mouse, keyboard
from pynput.mouse import Controller
import time
import threading
import json
import os
import random

# -----------------------------
# Settings persistence
# -----------------------------
SETTINGS_FILE = "settings.json"

custom_css = """
<style>
.stAppToolbar {
display: none !important;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

default_settings = {
    "idle_threshold": 20,
    "move_distance": 2,
    "check_interval": 1.0,
    "enabled": True
}

# Load settings
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
else:
    settings = default_settings

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Pomodoro Timer")


idle_threshold = st.slider("Idle Threshold (seconds)",
                           min_value=5, max_value=300,
                           value=settings.get("idle_threshold", 20))
move_distance = st.slider("Max Move Distance (pixels)",
                          min_value=1, max_value=50,
                          value=settings.get("move_distance", 1))
check_interval = st.slider("Check Idle Interval (seconds)",
                           min_value=0.5, max_value=10.0,
                           value=settings.get("check_interval", 1.0))
enabled = st.checkbox("Enable Pomodoro Timer", value=settings.get("enabled", False))

# Save current settings
current_settings = {
    "idle_threshold": idle_threshold,
    "move_distance": move_distance,
    "check_interval": check_interval,
    "enabled": enabled
}

with open(SETTINGS_FILE, "w") as f:
    json.dump(current_settings, f)

# -----------------------------
# Mouse mover logic
# -----------------------------
last_activity_time = time.time()
mouse_controller = Controller()

def on_mouse_move(x, y):
    global last_activity_time
    last_activity_time = time.time()

def on_mouse_click(x, y, button, pressed):
    global last_activity_time
    last_activity_time = time.time()

def on_key_press(key):
    global last_activity_time
    last_activity_time = time.time()

mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_mouse_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener.start()
keyboard_listener.start()

def mouse_mover_loop():
    global last_activity_time
    while True:
        if enabled:
            now = time.time()
            idle_time = now - last_activity_time
            if idle_time > idle_threshold:
                x, y = mouse_controller.position
                # Randomize movement distance and direction
                dx = random.randint(1, move_distance) * random.choice([-1, 1])
                dy = random.randint(1, move_distance) * random.choice([-1, 1])
                mouse_controller.position = (x + dx, y + dy)
                time.sleep(random.uniform(0.05, 0.15))  # small pause
                mouse_controller.position = (x, y)
                last_activity_time = time.time()
        # Randomize interval slightly to avoid detection
        time.sleep(check_interval + random.uniform(-0.2, 0.2))

# Run in background thread
thread = threading.Thread(target=mouse_mover_loop, daemon=True)
thread.start()

# -----------------------------
# Display info
# -----------------------------
status = "Running 🟢" if enabled else "Stopped 🔴"
st.info(f"Pomodoro status: **{status}**")
st.success("Settings are saved automatically and loaded next time you open this app.")
