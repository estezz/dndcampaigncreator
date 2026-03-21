sudo cp dnd.service /etc/systemd/system/.
systemctl daemon-reload
systemctl enable dnd.service
systemctl start dnd.service
systemctl start dnd.service