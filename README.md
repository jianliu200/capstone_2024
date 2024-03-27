# How to get this running on a Raspberry Pi 5

### Steps
1. Connecting Camera to Raspberry Pi
	- run `sudo apt-get update -y`
	- run `sudo apt-get upgrade`
	- run `sudo nano /boot/firmware/config.txt`
	- in the `/boot/firmware/config.txt` file change the `camera-auto-detect=1` to  `camera-auto-detect=0`
	- add `dtoverlay=imx219,cam0` to the bottom of the file
 	- run `sudo reboot`
	- run `sudo libcamera-hello -t 0` to make sure the camera is working
	
2. Creating a virtual env
   	- clone the repo
	- run `cd capstone_2024`
	- run `python -m venv --system-site-package env`
	
4. Getting the code running
	- run `. env/bin/activate`
	- run `pip install -r requirements.txt`
	- run `python model.py`
