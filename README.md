# TinyTuya + Telegram Bot Control

Dieu khien thiet bi Tuya (den, o cam, cong tac) qua **Giao dien GUI** va **Telegram Bot**.

## 📋 Muc luc
- [Chuan bi](#chuan-bi)
- [Cai dat](#cai-dat)
- [Cau hinh thiet bi](#cau-hinh-thiet-bi)
- [Lay Telegram Bot Token](#lay-telegram-bot-token)
- [Chay ung dung](#chay-ung-dung)
- [Lenh Telegram](#lenh-telegram)
- [Cau truc du an](#cau-truc-du-an)
- [Cau hinh systemd (Linux)](#cau-hinh-systemd-linux)
- [Cau hinh launchd (macOS)](#cau-hinh-launchd-macos)

---

## 🔧 Chuan bi

### Phan cung
- May tinh/Laptop/Server chay Python 3.11+
- Cac thiet bi Tuya da duoc ket noi WiFi va cau hinh qua Smart Life/Smart Tuya App

### Phan mem
- Python 3.11+ (khuyen dung 3.11)
- pip (Python package manager)
- Tkinter (cho GUI)

---

## ⚙️ Cai dat

### 1. Clone du an
```bash
git clone https://github.com/vdlaptrinh/tinytuya-control
cd tinytuya-control
```

Hoac neu da co san:
```bash
cd /Users/dailuu/Desktop/CT2026/tuya2
```

### 2. Cai dat Python 3.11 (neu chua co)
```bash
# macOS (Homebrew)
brew install python@3.11

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-tk

# Kiem tra
/opt/homebrew/bin/python3.11 --version  # macOS
python3.11 --version              # Linux
```

### 3. Tao Virtual Environment (khuyen dung)
```bash
/opt/homebrew/bin/python3.11 -m venv my_env    # macOS
python3.11 -m venv my_env                # Linux

# Kich hoat
source my_env/bin/activate
```

### 4. Cai dat thu vien
```bash
pip install -r requirements.txt
```

**Thu vien can thiet:**
- `tinytuya` - Dieu khien thiet bi Tuya
- `python-telegram-bot` - Tao Telegram Bot
- `requests` - (tu dong cai kem)

Hoac cai tay:
```bash
pip install tinytuya python-telegram-bot requests
```

---

## ⚙️ Cau hinh thiet bi

### Buoc 1: Lay thong tin thiet bi tu Tuya Cloud

1. Tao tai khoan [Tuya IoT Platform](https://iot.tuya.com/)
2. Tao Project → Lay "Access ID/Client ID" va "Access Secret/Client Secret"
3. Lien ket voi Smart Life App (quet QR code)
4. Chay Wizard de lay `devices.json`:
   ```bash
   /opt/homebrew/bin/python3.11 -m tinytuya wizard
   ```
   - Nhap API Key, Secret, Region
   - Chon thiet bi mau de quet

### Buoc 2: Quet thiet bi trong mang LAN
```bash
/opt/homebrew/bin/python3.11 -m tinytuya scan
```
→ Tao file `snapshot.json` chua IP va Version cua thiet bi.

### Buoc 3: Kiem tra file cau hinh
File `config.json` phai co dinh dang:
```json
{
  "IOT_DEVICES": {
    "Ten_Thiet_Bi": {
      "enabled": true,
      "device_id": "abc123...",
      "ip_address": "192.168.1.x",
      "local_key": "your_local_key",
      "version": 3.3,
      "product_name": "Smart Bulb"
    }
  }
}
```

**Luu y:** Thiet bi khong co IP (pin, sub-device) se bi an khoi danh sach dieu khien.

---

## 🤖 Lay Telegram Bot Token

1. Mo Telegram, tim `@BotFather`
2. Gui lenh: `/newbot`
3. Nhap ten bot (vi du: `TinyTuyaBot`)
4. Nhap username bot (phai ket thuc bang `bot`, vi du: `TinyTuyaBot`)
5. Nhan duoc **BOT_TOKEN** (dang: `123456789:ABCdefGHIjklMNO...`)

Saochep token vao file:
```bash
echo "YOUR_BOT_TOKEN_HERE" > token.txt
```

---

## 🚀 Chay ung dung

### 1. Chay GUI (Giao dien do hoa)
```bash
# Cach 1: Truc tiep
/opt/homebrew/bin/python3.11 gui_control.py

# Cach 2: Dung shortcut (da tao)
./tuya-gui.command

# Cach 3: Dung alias (da cau hinh trong ~/.zshrc)
tuya-gui
```

**Giao dien GUI cho phep:**
- Xem danh sach thiet bi co IP
- Dieu khien den (bat/tat, doi mau, do sang, che do)
- Dieu khien cong tac o cam (SW1, SW2, bat/tat tat ca)

### 2. Chay Telegram Bot
```bash
# Cach 1: Truc tiep voi token
/opt/homebrew/bin/python3.11 telegram_bot.py YOUR_BOT_TOKEN

# Cach 2: Dung token tu file
/opt/homebrew/bin/python3.11 telegram_bot.py "$(cat token.txt)"

# Cach 3: Chay nen (background)
nohup /opt/homebrew/bin/python3.11 telegram_bot.py "$(cat token.txt)" > bot.log 2>&1 &
echo "Bot PID: $!"

# Xem log
tail -f bot.log

# Dung bot
kill <PID>
```

### 3. Chay quet thiet bi dinh ky
```bash
# Quet trong 30 giay
/opt/homebrew/bin/python3.11 -m tinytuya scan 30

# Hoac dung alias
tuya-scan 30
```

---

## 📱 Lenh Telegram

Mo Telegram, tim bot cua ban va gui cac lenh:

| Lenh | Mo ta | Vi du |
|------|-------|-------|
| `/start` | Xem huong dan va danh sach lenh | `/start` |
| `/list` | Liet ke thiet bi co IP | `/list` |
| `/on <ten>` | Bat thiet bi | `/on Den_Ngu` |
| `/off <ten>` | Tat thiet bi | `/off Den_Gac` |
| `/on <ten> <sw>` | Bat switch cu the (1-4) | `/on Den_Gac 2` |
| `/off <ten> <sw>` | Tat switch cu the (1-4) | `/off Den_Phong_Khach 1` |
| `/status <ten>` | Xem trang thai | `/status IR_Thong_Minh` |
| `/allon` | Bat tat ca thiet bi | `/allon` |
| `/alloff` | Tat tat ca thiet bi | `/alloff` |

**Luu y cho IR_Thong_Minh:** Lenh `/status` se hien thi:
```
Status: IR_Thong_Minh [ir]
  Nhiet do: 27.4°C
  Do am: 60%
```

---

## 📂 Cau truc du an

```
tuya2/
├── README.md           # ← Huong dan nay
├── requirements.txt    # ← Thu vien can thiet
├── config.json       # Cau hinh thiet bi (IOT_DEVICES)
├── devices.json       # Danh sach thiet bi (tu wizard)
├── snapshot.json      # IP va Version (tu scan)
├── token.txt         # Telegram Bot Token
├── gui_control.py     # Giao dien GUI (Tkinter)
├── telegram_bot.py   # Telegram Bot
├── control.py        # CLI dieu khien (legacy)
├── tuya-gui.command # Shortcut chay GUI (macOS)
├── run_bot.sh        # Script chay bot
├── devices_list.csv   # Danh sach CSV
├── devices_list.xlsx  # Danh sach Excel
├── bot.log           # Log cua Telegram bot
└── my_env/           # Virtual environment (tuy chon)
```

---

## ⚙️ Cau hinh systemd (Linux)

Tao file service de bot tu dong chay khi khoi dong:

### 1. Tao file service
```bash
sudo nano /etc/systemd/system/tinytuya-bot.service
```

Noi dung:
```ini
[Unit]
Description=TinyTuya Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tuya2
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3.11 /path/to/tuya2/telegram_bot.py YOUR_BOT_TOKEN
Restart=always
RestartSec=10
StandardOutput=append:/path/to/tuya2/bot.log
StandardError=append:/path/to/tuya2/bot.log

[Install]
WantedBy=multi-user.target
```

**Luu y:** Thay `your_username` va `/path/to/tuya2` bang duong dan that.

### 2. Kich hoat service
```bash
# Tai lai systemd
sudo systemctl daemon-reload

# Khoi dong cung he thong
sudo systemctl enable tinytuya-bot.service

# Khoi dong service
sudo systemctl start tinytuya-bot.service

# Kiem tra trang thai
sudo systemctl status tinytuya-bot.service

# Xem log
sudo journalctl -u tinytuya-bot.service -f
```

### 3. Quan ly service
```bash
# Dung bot
sudo systemctl stop tinytuya-bot.service

# Khoi dong lai
sudo systemctl restart tinytuya-bot.service

# Tat khoi dong cung
sudo systemctl disable tinytuya-bot.service
```

---

## ⚙️ Cau hinh launchd (macOS)

Tao plist de bot tu dong chay khi khoi dong tren macOS:

### 1. Tao file plist
```bash
nano ~/Library/LaunchAgents/com.tinytuya.bot.plist
```

Noi dung:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tinytuya.bot</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3.11</string>
        <string>/Users/dailuu/Desktop/CT2026/tuya2/telegram_bot.py</string>
        <string>7892400158:AAF__JFfS_IjXkI6WOSeMhDvMbuno15mUgE</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/dailuu/Desktop/CT2026/tuya2</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/dailuu/Desktop/CT2026/tuya2/bot.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/dailuu/Desktop/CT2026/tuya2/bot.log</string>
</dict>
</plist>
```

**Luu y:** Thay token bang token that cua ban.

### 2. Kich hoat service
```bash
# Tai plist vao launchd
launchctl load ~/Library/LaunchAgents/com.tinytuya.bot.plist

# Kiem tra trang thai
launchctl list | grep tinytuya

# Xem log
tail -f ~/Desktop/CT2026/tuya2/bot.log
```

### 3. Quan ly service
```bash
# Dung bot
launchctl unload ~/Library/LaunchAgents/com.tinytuya.bot.plist

# Khoi dong lai
launchctl load ~/Library/LaunchAgents/com.tinytuya.bot.plist

# Xoa khoi khoi dong cung
launchctl unload ~/Library/LaunchAgents/com.tinytuya.bot.plist
```

---

## 🔍 Van de thuong gap

### Bot khong chay
```bash
# Kiem tra token
cat token.txt

# Kiem tra log
tail bot.log

# Kiem tra ket noi
ping api.telegram.org
```

### Khong tim thay thiet bi
```bash
# Quet lai mang
/opt/homebrew/bin/python3.11 -m tinytuya scan 30

# Kiem tra snapshot.json co IP khong
cat snapshot.json | grep ip
```

### Loi Tkinter
```bash
# macOS: cai python-tk
brew install python-tk@3.11

# Linux: cai python3-tk
sudo apt install python3.11-tk
```

---

## 📝 Ghi chu

- Thiet bi chay pin (Wireless Switch, sub-device) **khong co IP**, khong dieu khien truc tiep qua LAN
- Ten chay bot tren server luon hoat dong de nhan lenh Telegram 24/7
- Khong chia se `config.json`, `token.txt`, `devices.json` co chua thong tin nhay cam
- Phien ban TinyTuya ho tro: Protocol 3.1, 3.2, 3.3, 3.4, 3.5

---

## 📞 Lien he & Dong gop

- Tac gia: Dailuu
- Duoc xay dung tren [TinyTuya](https://github.com/jasonacox/tinytuya)
- Telegram Bot: @TinyTuyaBot

---

**🎉 Chuc ban dieu khien thiet bi thanh cong!**
