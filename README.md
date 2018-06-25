# taikapeili

Simple magic mirror / weather screen for the good old Raspberry Pi 1 (Model B) that everyone has in the drawer anyway.

RasPi configuration:  
pi@taikapeili:~$ cat /proc/version  
Linux version 4.9.59+ (dc4@dc4-XPS13-9333) (gcc version 4.9.3 (crosstool-NG crosstool-ng-1.22.0-88-g8460611) ) #1047 Sun Oct 29 11:47:10 GMT 2017  

pi@taikapeili:~$ cat /etc/*-release  
PRETTY_NAME="Raspbian GNU/Linux 9 (stretch)"  
NAME="Raspbian GNU/Linux"  
VERSION_ID="9"  
VERSION="9 (stretch)"  
ID=raspbian  
ID_LIKE=debian  
HOME_URL="http://www.raspbian.org/"  
SUPPORT_URL="http://www.raspbian.org/RaspbianForums"  
BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"  


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
