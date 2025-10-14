from pynput import keyboard
import pygame
import random
import os
import sys
import threading
import winreg
import pystray
from PIL import Image

# === SETTINGS ===
APP_NAME = "KeyClicker Pro"
SOUNDS_DIR = "Sounds"
ICON_PATH = "icon.ico"
AUTO_START_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
DELAY = 0.05  # Mindestabstand zwischen Sounds (Sekunden)


# === SOUND LADEN ===
pygame.mixer.init()

def load_variants(prefix):
    return [pygame.mixer.Sound(os.path.join(SOUNDS_DIR, f))
            for f in os.listdir(SOUNDS_DIR)
            if f.lower().startswith(prefix) and f.lower().endswith(".wav")]

default_sounds = load_variants("click")
space_sounds = load_variants("space")
enter_sounds = load_variants("enter")
backspace_sounds = load_variants("backspace")

print(f"Geladen: {len(default_sounds)} default, "
      f"{len(space_sounds)} space, {len(enter_sounds)} enter, "
      f"{len(backspace_sounds)} backspace")


# === SOUND LOGIK ===
pressed_keys = set()
last_sound_time = 0

def random_play(sound_list):
    if not sound_list:
        return
    snd = random.choice(sound_list)
    if snd:
        snd.set_volume(random.uniform(0.85, 1.0))
        snd.play()

def play_for_key(key_name):
    global last_sound_time
    import time
    now = time.time()
    if now - last_sound_time < DELAY:
        return
    last_sound_time = now

    if key_name == "space":
        random_play(space_sounds)
    elif key_name == "enter":
        random_play(enter_sounds)
    elif key_name == "backspace":
        random_play(backspace_sounds)
    else:
        random_play(default_sounds)


# === KEYBOARD ===
def on_press(key):
    try:
        kname = getattr(key, "char", None)
        if kname is None:
            kname = getattr(key, "name", str(key))
        kname = kname.lower()
        if kname in pressed_keys:
            return
        pressed_keys.add(kname)
        play_for_key(kname)
    except Exception as e:
        print("Fehler:", e)

def on_release(key):
    try:
        kname = getattr(key, "char", None)
        if kname is None:
            kname = getattr(key, "name", str(key))
        kname = kname.lower()
        pressed_keys.discard(kname)
    except Exception:
        pass


# === AUTOSTART ===
def toggle_autostart(enable):
    exe = os.path.abspath(sys.argv[0])
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTO_START_REG_KEY, 0, winreg.KEY_SET_VALUE)
    if enable:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe)
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTO_START_REG_KEY)
        val, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return bool(val)
    except FileNotFoundError:
        return False


# === TRAY ICON ===
def run_tray():
    image = Image.open(ICON_PATH)

    def on_exit(icon, item):
        icon.visible = False
        os._exit(0)

    def on_toggle_autostart(icon, item):
        toggle_autostart(not is_autostart_enabled())
        icon.update_menu()

    def create_menu():
        autostart_state = "✅" if is_autostart_enabled() else "❌"
        return pystray.Menu(
            pystray.MenuItem(f"Autostart {autostart_state}", on_toggle_autostart),
            pystray.MenuItem("Beenden", on_exit),
        )

    icon = pystray.Icon(APP_NAME, image, APP_NAME, create_menu())
    icon.run()


# === STARTUP ===
def main():
    t1 = threading.Thread(target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).run(), daemon=True)
    t1.start()

    run_tray()

if __name__ == "__main__":
    main()