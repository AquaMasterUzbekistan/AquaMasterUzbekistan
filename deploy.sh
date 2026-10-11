#!/usr/bin/env bash
# ==============================================================================
# AquaMasterUzbekistan Telegram Bot - VPS Avtomatik O'rnatish Skripti
# ==============================================================================

set -e

echo "🚀 AquaMasterUzbekistan botini serverga o'rnatish boshlandi..."

# 1. Tizim paketlarini yangilash va kerakli kutubxonalarni o'rnatish
echo "📦 Tizim paketlari tekshirilmoqda..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl

# 2. Virtual muhit (venv) yaratish
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

if [ ! -d ".venv" ]; then
    echo "🐍 Virtual muhit (.venv) yaratilmoqda..."
    python3 -m venv .venv
fi

# 3. Paketlarni o'rnatish
echo "📥 Python kutubxonalari o'rnatilmoqda..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# 4. Kerakli papkalarni yaratish
mkdir -p logs media

# 5. Systemd servisini sozlash
echo "⚙️ Systemd servisi (24/7 rejim) sozlanmoqda..."
SERVICE_FILE="/etc/systemd/system/aquamaster.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=AquaMasterUzbekistan Telegram Bot Daemon
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=append:$APP_DIR/logs/bot.log
StandardError=append:$APP_DIR/logs/bot.log
Environment="PYTHONUNBUFFERED=1"
Environment="TZ=Asia/Tashkent"

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable aquamaster
sudo systemctl restart aquamaster

echo ""
echo "✅ Bot muvaffaqiyatli serverga o'rnatildi va 24/7 rejimida ishga tushirildi!"
echo "Holatni tekshirish uchun: sudo systemctl status aquamaster"
echo "Loglarni ko'rish uchun:   tail -f logs/bot.log"
