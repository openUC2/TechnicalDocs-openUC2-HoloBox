#!/usr/bin/env bash
# register and start /home/pi/startcamera2.py as a systemd service

SERVICE=startcamera2.service

sudo bash -c "cat >/etc/systemd/system/$SERVICE" <<'UNIT'
[Unit]
Description=Pi Camera Stream
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python /home/pi/startcamera2.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE"
