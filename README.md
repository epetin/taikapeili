# taikapeili

Simple magic mirror / weather screen for the good old Raspberry Pi 1 (Model B) that everyone has in the drawer anyway.

RasPi configuration:
- Web Server: nginx
- Web Browser: kweb3

~/.config/lxsession/LXDE:
kweb3 -KJ http://localhost &

/etc/systemd/system$ cat taikapeili.service  
[Unit]  
Description=Run taikapeili update script  
After=network.target  

[Service]  
ExecStart=/usr/bin/python3 -u get_weather.py  
WorkingDirectory=/var/www/taikapeili  
StandardOutput=inherit  
StandardError=inherit  
Restart=always  
User=pi  

[Install]  
WantedBy=multi-user.target  
