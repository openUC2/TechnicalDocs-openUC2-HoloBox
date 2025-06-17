#!/usr/bin/env bash
# register and start HoloBox camera API as a systemd service

SERVICE=holobox-camera.service

sudo bash -c "cat >/etc/systemd/system/$SERVICE" <<'UNIT'
[Unit]
Description=HoloBox Camera API Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/holobox/Software
ExecStart=/usr/bin/python3 /opt/holobox/Software/streamlined_camera_api.py --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE"
