from pynput import keyboard
import pygame
import random
import os

pygame.mixer.init()
SOUNDS_DIR = "Sounds"

def load_sound(filename):
    path = os.path.join(SOUNDS_DIR, filename)
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

# --- Mehrere Varianten laden ---
default_sounds = [s for name in os.listdir(SOUNDS_DIR)
                  if name.startswith("click") and name.endswith(".wav")
                  for s in [load_sound(name)] if s]

enter_sounds =  [s for name in os.listdir(SOUNDS_DIR)
                  if name.startswith("enter") and name.endswith(".wav")
                  for s in [load_sound(name)] if s]

space_sounds =  [s for name in os.listdir(SOUNDS_DIR)
                  if name.startswith("space") and name.endswith(".wav")
                  for s in [load_sound(name)] if s]

backspace_sounds = [s for name in os.listdir(SOUNDS_DIR)
                    if name.startswith("backspace") and name.endswith(".wav")
                    for s in [load_sound(name)] if s]

print(f"Geladen: {len(default_sounds)} Default, "
      f"{len(space_sounds)} Space, "
      f"{len(enter_sounds)} Enter, "
      f"{len(backspace_sounds)} Backspace Sounds")

# --- gerade gedrückte Keys merken ---
pressed_keys = set()

def random_play(sound_list):
    if not sound_list:
        return
    snd = random.choice(sound_list)
    if snd:
        snd.set_volume(random.uniform(0.85, 1.0))
        snd.play()

def on_press(key):
    try:
        kname = getattr(key, "char", None)
        if kname is None:
            kname = getattr(key, "name", str(key))
        kname = kname.lower()

        # nur erster Druck – kein Autorepeat
        if kname in pressed_keys:
            return
        pressed_keys.add(kname)

        if kname == "space":
            random_play(space_sounds)
        elif kname == "enter":
            random_play(enter_sounds)
        elif kname == "backspace":
            random_play(backspace_sounds)
        else:
            random_play(default_sounds)

        print("Key pressed:", kname)
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

print("⏺ KeyClicker Pro läuft – drücke ESC zum Beenden")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()