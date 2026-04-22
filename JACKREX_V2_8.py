import customtkinter as ctk
import threading
import time
import win32api
import win32con
import win32gui # 🟢 เพิ่ม Library สำหรับจับหน้าต่างเกม
import keyboard
import random
import os
import ctypes
from PIL import Image

# ==========================================
# --- Core Logic & Window Check ---
# ==========================================
PULL_STRENGTH = 5
RECOIL_ACTIVE = False

LOOT_SYSTEM_ENABLED = False # Master Switch (L)
LOOT_ACTIVE = False         # สถานะดึงของ (TAB)

LAST_RECOIL_TOGGLE = 0
LAST_LOOT_TOGGLE = 0
LAST_L_TOGGLE = 0
LAST_ADJUST_TIME = 0
IS_HOLDING_GUN = False # สถานะการถือปืนหลัก

FIRST_SLOT_X = 150  
FIRST_SLOT_Y = 150  

def is_game_active():
    """🟢 ฟังก์ชันเช็คว่าหน้าต่างที่เปิดอยู่คือ PUBG หรือไม่"""
    try:
        # ดึง ID หน้าต่างที่กำลัง Active อยู่ตอนนี้ (Foreground Window)
        hwnd = win32gui.GetForegroundWindow()
        # ดึงชื่อหน้าต่างมาเป็นตัวพิมพ์ใหญ่เพื่อเช็คคำ
        window_title = win32gui.GetWindowText(hwnd).upper()
        
        # เช็คว่ามีคำว่า PUBG หรือ BATTLEGROUNDS ในชื่อหน้าต่างหรือไม่
        if "PUBG" in window_title or "BATTLEGROUNDS" in window_title:
            return True
        return False
    except:
        return False
    
def gun_state_worker():
    global IS_HOLDING_GUN
    while True:
        if is_game_active():
            # เช็คว่ากด 1 หรือ 2 (หยิบปืนหลัก) -> 0x31 คือ '1', 0x32 คือ '2'
            if win32api.GetAsyncKeyState(0x31) < 0 or win32api.GetAsyncKeyState(0x32) < 0:
                IS_HOLDING_GUN = True
                
            # เช็คว่ากด X (เก็บปืน), 3 (ปืนพก), 4 (อาวุธประชิด), 5 (ระเบิด), G (ปาระเบิดด่วน)
            # 0x58='X', 0x33='3', 0x34='4', 0x35='5', 0x47='G'
            elif (win32api.GetAsyncKeyState(0x58) < 0 or 
                  win32api.GetAsyncKeyState(0x33) < 0 or 
                  win32api.GetAsyncKeyState(0x34) < 0 or 
                  win32api.GetAsyncKeyState(0x35) < 0 or 
                  win32api.GetAsyncKeyState(0x47) < 0):
                IS_HOLDING_GUN = False
                
        time.sleep(0.05)

def recoil_worker():
    global RECOIL_ACTIVE, PULL_STRENGTH, IS_HOLDING_GUN # <--- อย่าลืมดึงตัวแปรมาใช้
    while True:
        # 🟢 เพิ่มเช็คว่าถือปืนอยู่ (IS_HOLDING_GUN) ถึงจะทำงาน
        if is_game_active() and RECOIL_ACTIVE and IS_HOLDING_GUN and win32api.GetAsyncKeyState(0x01) < 0:
            variation = random.uniform(0.9, 1.1)
            final_pull = int(PULL_STRENGTH * variation)
            if final_pull > 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, final_pull)
        time.sleep(0.01)

def loot_worker():
    global LOOT_ACTIVE
    while True:
        # 🟢 เพิ่ม is_game_active() ป้องกันเมาส์วาร์ปไปคลิกขวารัวๆ ตอนอยู่หน้า Desktop
        if is_game_active() and LOOT_ACTIVE:
            win32api.SetCursorPos((FIRST_SLOT_X, FIRST_SLOT_Y))
            time.sleep(0.01)
            
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            
            time.sleep(random.uniform(0.35, 0.04))
        else:
            time.sleep(0.1)

threading.Thread(target=recoil_worker, daemon=True).start()
threading.Thread(target=loot_worker, daemon=True).start()
threading.Thread(target=gun_state_worker, daemon=True).start()

# ==========================================
# --- Neo-Luxe UI Design ---
# ==========================================

class JackRexApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.setup_assets()

        self.title("JACKREX NEO v2.8 [PUBG LOCK]")
        self.geometry("350x500")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#080808")

        self.clr_purple = "#BC6FF1"
        self.clr_pink   = "#FF2E63"
        self.clr_green  = "#00FFAB"
        self.clr_orange = "#F39C12" 
        self.clr_dark   = "#121212"
        self.clr_border = "#1F1F1F"

        self.setup_ui()
        self.run_hotkey_loop()

    def setup_assets(self):
        try:
            font_file = "RubikGlitch-Regular.ttf"
            font_path = os.path.join(os.path.dirname(__file__), font_file)
            if os.path.exists(font_path):
                ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)

            icon_file = "jrex.ico"
            icon_path = os.path.join(os.path.dirname(__file__), icon_file)
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('jackrex.neo.v2.8')
        except: pass

    def check_font(self, font_name):
        import tkinter.font
        return font_name in tkinter.font.families()

    def setup_ui(self):
        # Header
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(pady=(40, 2))

        target_font = "Rubik Glitch" if self.check_font("Rubik Glitch") else "Segoe UI"

        self.logo_glow = ctk.CTkLabel(self.logo_frame, text="JACKREX", 
                                      font=(target_font, 36), text_color="#3A0088")
        self.logo_glow.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_label = ctk.CTkLabel(self.logo_frame, text="JACKREX", 
                                       font=(target_font, 34), text_color=self.clr_purple)
        self.logo_label.pack()
        
        ctk.CTkLabel(self, text="= S M A R T - L O O T =", 
                     font=("Segoe UI", 9, "bold"), text_color=self.clr_pink).pack(pady=(0, 20))

        # Recoil Card
        self.recoil_card = ctk.CTkFrame(self, fg_color=self.clr_dark, corner_radius=15, 
                                        border_width=1, border_color=self.clr_border)
        self.recoil_card.pack(fill="x", padx=30, pady=10)

        self.recoil_val_lbl = ctk.CTkLabel(self.recoil_card, text=str(PULL_STRENGTH), 
                                           font=("Segoe UI", 26, "bold"), text_color="#FFFFFF")
        self.recoil_val_lbl.pack(pady=(15, 0))
        
        ctk.CTkLabel(self.recoil_card, text="INTENSITY LEVEL", 
                     font=("Segoe UI", 9, "bold"), text_color=self.clr_purple).pack()

        self.slider = ctk.CTkSlider(self.recoil_card, from_=0, to=10, number_of_steps=10, 
                                    button_color=self.clr_pink, progress_color=self.clr_purple, 
                                    command=self.update_strength)
        self.slider.set(PULL_STRENGTH)
        self.slider.pack(pady=(10, 20), padx=25)

        # Status Display
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=30, pady=10)

        self.recoil_indicator = ctk.CTkFrame(self.status_frame, fg_color=self.clr_dark, 
                                             height=45, corner_radius=10, border_width=1, border_color=self.clr_border)
        self.recoil_indicator.pack(fill="x", pady=5)
        self.recoil_indicator.pack_propagate(False)
        self.recoil_stat_txt = ctk.CTkLabel(self.recoil_indicator, text="RECOIL : STANDBY", 
                                            font=("Segoe UI", 11, "bold"), text_color="#333333")
        self.recoil_stat_txt.pack(expand=True)

        self.loot_indicator = ctk.CTkFrame(self.status_frame, fg_color=self.clr_dark, 
                                           height=45, corner_radius=10, border_width=1, border_color=self.clr_border)
        self.loot_indicator.pack(fill="x", pady=5)
        self.loot_indicator.pack_propagate(False)
        self.loot_stat_txt = ctk.CTkLabel(self.loot_indicator, text="SYSTEM : OFFLINE", 
                                          font=("Segoe UI", 11, "bold"), text_color="#333333")
        self.loot_stat_txt.pack(expand=True)

        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=25)
        guide_txt = "[ L ] ON/OFF  |  [ TAB ] LOOT  |  [ ESC ] STOP"
        ctk.CTkLabel(footer_frame, text=guide_txt, font=("Segoe UI", 10), text_color="#404040").pack()

    def update_strength(self, val):
        global PULL_STRENGTH
        PULL_STRENGTH = int(val)
        self.recoil_val_lbl.configure(text=str(PULL_STRENGTH))

    def update_loot_ui(self):
        if not LOOT_SYSTEM_ENABLED:
            self.loot_indicator.configure(border_color=self.clr_border)
            self.loot_stat_txt.configure(text="SYSTEM : OFFLINE", text_color="#333333")
        elif LOOT_SYSTEM_ENABLED and not LOOT_ACTIVE:
            self.loot_indicator.configure(border_color=self.clr_orange)
            self.loot_stat_txt.configure(text="LOOT : STANDBY", text_color=self.clr_orange)
        elif LOOT_ACTIVE:
            self.loot_indicator.configure(border_color=self.clr_green)
            self.loot_stat_txt.configure(text="LOOT : ACTIVE", text_color=self.clr_green)

    def run_hotkey_loop(self):
        global RECOIL_ACTIVE, LOOT_ACTIVE, LOOT_SYSTEM_ENABLED
        global LAST_RECOIL_TOGGLE, LAST_LOOT_TOGGLE, LAST_L_TOGGLE, PULL_STRENGTH, LAST_ADJUST_TIME
        
        try:
            now = time.time()
            
            # ปุ่ม END กดยกเลิกสคริปต์ได้เสมอ ไม่ว่าจะอยู่ในเกมหรือไม่
            if keyboard.is_pressed('end'): os._exit(0)

            # 🟢 เช็คว่าต้องอยู่ในเกม PUBG เท่านั้น ปุ่มพวกนี้ถึงจะทำงาน
            if is_game_active():
                
                # --- Toggle Recoil (ปุ่ม O สลับเปิดปิด) ---
                if (keyboard.is_pressed('o') or win32api.GetAsyncKeyState(0x06) < 0) and now - LAST_RECOIL_TOGGLE > 0.3:
                    RECOIL_ACTIVE = not RECOIL_ACTIVE
                    if RECOIL_ACTIVE:
                        win32api.Beep(1000, 100)
                        self.recoil_indicator.configure(border_color=self.clr_purple)
                        self.recoil_stat_txt.configure(text="RECOIL : ACTIVE", text_color=self.clr_purple)
                    else:
                        win32api.Beep(500, 100)
                        self.recoil_indicator.configure(border_color=self.clr_border)
                        self.recoil_stat_txt.configure(text="RECOIL : STANDBY", text_color="#333333")
                    LAST_RECOIL_TOGGLE = now

                # --- Master Switch (ปุ่ม L) ---
                if win32api.GetAsyncKeyState(0x4C) or win32api.GetAsyncKeyState(0x05) < 0 and now - LAST_L_TOGGLE > 0.3:
                    LOOT_SYSTEM_ENABLED = not LOOT_SYSTEM_ENABLED
                    if not LOOT_SYSTEM_ENABLED:
                        LOOT_ACTIVE = False
                        win32api.Beep(400, 100)
                    else:
                        win32api.Beep(800, 100)
                    self.update_loot_ui()
                    LAST_L_TOGGLE = now

                # --- Toggle Loot (TAB & ESC) ---
                if LOOT_SYSTEM_ENABLED:
                    if win32api.GetAsyncKeyState(0x09) < 0 and now - LAST_LOOT_TOGGLE > 0.3:
                        LOOT_ACTIVE = not LOOT_ACTIVE
                        if LOOT_ACTIVE: win32api.Beep(1200, 80)
                        else: win32api.Beep(600, 80)
                        self.update_loot_ui()
                        LAST_LOOT_TOGGLE = now
                    
                    if win32api.GetAsyncKeyState(0x1B) < 0 and LOOT_ACTIVE:
                        LOOT_ACTIVE = False
                        win32api.Beep(600, 80)
                        self.update_loot_ui()

                # --- Adjust Power (/ .) ---
                if win32api.GetAsyncKeyState(0xBF) < 0 and now - LAST_ADJUST_TIME > 0.15:
                    PULL_STRENGTH = min(30, PULL_STRENGTH + 1)
                    self.slider.set(PULL_STRENGTH)
                    self.recoil_val_lbl.configure(text=str(PULL_STRENGTH))
                    LAST_ADJUST_TIME = now
                if win32api.GetAsyncKeyState(0xBE) < 0 and now - LAST_ADJUST_TIME > 0.15:
                    PULL_STRENGTH = max(0, PULL_STRENGTH - 1)
                    self.slider.set(PULL_STRENGTH)
                    self.recoil_val_lbl.configure(text=str(PULL_STRENGTH))
                    LAST_ADJUST_TIME = now

        except: pass
        self.after(50, self.run_hotkey_loop)

if __name__ == "__main__":
    app = JackRexApp()
    app.mainloop()