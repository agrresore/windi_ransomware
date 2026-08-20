# windi_ransomware
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
