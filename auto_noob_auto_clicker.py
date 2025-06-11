import customtkinter as ctk
import threading
import time
import pyautogui
import keyboard
from tkinter import messagebox

# Configuration de CustomTkinter
ctk.set_appearance_mode("System")  # Par défaut, le mode système
ctk.set_default_color_theme("green")

clicking = False
click_thread = None
lock = threading.Lock()
hotkey = "f6"
dark_mode = False  # Variable globale pour suivre le mode sombre (False = clair, True = sombre)

def clicker(cps, duration, button):
    global clicking
    interval = 1 / cps if cps > 0 else 0
    start_time = time.time()
    while True:
        with lock:
            if not clicking:
                break
        if duration > 0 and (time.time() - start_time) >= duration:
            break
        pyautogui.click(button=button)
        if interval > 0:
            time.sleep(interval)
        else:
            time.sleep(0)
    with lock:
        clicking = False
    update_button_texts()

def toggle_click():
    global clicking, click_thread
    with lock:
        if clicking:
            clicking = False
            update_button_texts()
            return
        else:
            try:
                cps = float(cps_entry.get())
                if cps < 1 or cps > 100000:
                    messagebox.showerror("Erreur", "CPS doit être entre 1 et 100000")
                    return
            except:
                messagebox.showerror("Erreur", "CPS invalide")
                return
            try:
                duration = float(duration_entry.get())
                if duration < 0:
                    messagebox.showerror("Erreur", "Durée doit être positive ou zéro")
                    return
            except:
                messagebox.showerror("Erreur", "Durée invalide")
                return
            button = mouse_button.get()
            clicking = True
            update_button_texts()
            click_thread = threading.Thread(target=clicker, args=(cps, duration, button), daemon=True)
            click_thread.start()

def start_click():
    with lock:
        if not clicking:
            toggle_click()

def stop_click():
    with lock:
        if clicking:
            toggle_click()

def update_button_texts():
    if clicking:
        start_button.configure(text=f"Arrêter ({hotkey.upper()})")
        stop_button.configure(text=f"Arrêter ({hotkey.upper()})")
    else:
        start_button.configure(text=f"Démarrer ({hotkey.upper()})")
        stop_button.configure(text=f"Arrêter ({hotkey.upper()})")

def on_hotkey():
    toggle_click()

def wait_for_new_hotkey():
    global hotkey
    messagebox.showinfo("Info", "Appuie sur la touche que tu veux utiliser.")
    try:
        keyboard.remove_hotkey(hotkey)
    except:
        pass

    event = keyboard.read_event(suppress=False)
    while event.event_type != keyboard.KEY_DOWN:
        event = keyboard.read_event(suppress=False)
    new_hotkey = event.name

    hotkey = new_hotkey
    update_button_texts()

    try:
        keyboard.add_hotkey(hotkey, on_hotkey)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'enregistrer la touche: {e}")
        return
    messagebox.showinfo("Info", f"Nouvelle touche hotkey : {hotkey}")

def on_slider_change(value):
    cps_entry.delete(0, "end")
    cps_entry.insert(0, str(int(value)))

def on_entry_change(event=None):
    try:
        val = float(cps_entry.get())
        if 1 <= val <= 100000:
            cps_slider.set(val)
    except:
        pass

# Nouvelle fonction pour basculer le mode sombre
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        ctk.set_appearance_mode("Dark")
        dark_mode_label.config(text="Mode sombre activé")
    else:
        ctk.set_appearance_mode("Light")
        dark_mode_label.config(text="Mode clair activé")

# Interface Graphique
root = ctk.CTk()
root.title("Noob Auto")
root.geometry("700x450")
root.resizable(False, False)

ctk.CTkLabel(root, text="Noob Auto - Auto Clicker", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=15)

frame_controls = ctk.CTkFrame(root)
frame_controls.pack(padx=30, pady=10, fill="both", expand=True)

# CPS slider + entry
ctk.CTkLabel(frame_controls, text="Clics par seconde (1 - 100000)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10,3))
cps_slider = ctk.CTkSlider(frame_controls, from_=1, to=100000, number_of_steps=100000, command=on_slider_change)
cps_slider.set(10)
cps_slider.pack(fill="x", pady=5)

cps_entry = ctk.CTkEntry(frame_controls, font=ctk.CTkFont(size=14))
cps_entry.insert(0, "10")
cps_entry.pack(fill="x", pady=5)
cps_entry.bind("<KeyRelease>", on_entry_change)

# Durée
ctk.CTkLabel(frame_controls, text="Durée (secondes, 0 = illimité)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10,3))
duration_entry = ctk.CTkEntry(frame_controls, font=ctk.CTkFont(size=14))
duration_entry.insert(0, "0")
duration_entry.pack(fill="x", pady=5)

# Bouton souris
ctk.CTkLabel(frame_controls, text="Bouton de la souris", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10,3))
mouse_button = ctk.StringVar(value="left")
buttons_frame = ctk.CTkFrame(frame_controls)
buttons_frame.pack(pady=5)
ctk.CTkRadioButton(buttons_frame, text="Gauche", variable=mouse_button, value="left", font=ctk.CTkFont(size=14)).pack(side="left", padx=20)
ctk.CTkRadioButton(buttons_frame, text="Droit", variable=mouse_button, value="right", font=ctk.CTkFont(size=14)).pack(side="left", padx=20)
ctk.CTkRadioButton(buttons_frame, text="Milieu", variable=mouse_button, value="middle", font=ctk.CTkFont(size=14)).pack(side="left", padx=20)

# Boutons Start / Stop / Hotkey
buttons_frame2 = ctk.CTkFrame(root)
buttons_frame2.pack(pady=15)

start_button = ctk.CTkButton(buttons_frame2, text=f"Démarrer ({hotkey.upper()})", width=160, height=50, font=ctk.CTkFont(size=16), command=start_click)
start_button.pack(side="left", padx=20)

stop_button = ctk.CTkButton(buttons_frame2, text=f"Arrêter ({hotkey.upper()})", width=160, height=50, font=ctk.CTkFont(size=16), command=stop_click)
stop_button.pack(side="left", padx=20)

hotkey_button = ctk.CTkButton(buttons_frame2, text="Hotkey Settings", width=160, height=50, font=ctk.CTkFont(size=16), command=lambda: threading.Thread(target=wait_for_new_hotkey, daemon=True).start())
hotkey_button.pack(side="left", padx=20)

# Ajout de l'option Mode sombre
dark_mode_btn = ctk.CTkButton(root, text="Basculer mode sombre", width=160, height=40, font=ctk.CTkFont(size=16), command=toggle_dark_mode)
dark_mode_btn.pack(pady=5)

dark_mode_label = ctk.CTkLabel(root, text="Mode clair activé", font=ctk.CTkFont(size=14))
dark_mode_label.pack(pady=5)

# Enregistre la hotkey
try:
    keyboard.add_hotkey(hotkey, on_hotkey)
except Exception as e:
    messagebox.showerror("Erreur", f"Impossible d'enregistrer la touche par défaut: {e}")

root.mainloop()
