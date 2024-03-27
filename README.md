# How to get this running on a Raspberry Pi 5

### Steps
1. Connecting Camera to Raspberry Pi
	- run the following commands:
		`sudo apt-get update -y`
		`sudo apt-get upgrade-`
		`sudo nano /boot/firmware/config.txt`
		
	- in the `/boot/firmware/config.txt` file change the `camera-auto-detect=1` to  `camera-auto-detect=0`
	- add `dtoverlay=imx219,cam0` to the bottom of the file
	- save and exit
	
2. Creating a virtual env
	- run `python -m venv --system-site-package env`
	
3. Getting the code running
	- clone the repo
	- cd into `/seniorcapstone/deep_learning_models/YOLOv8`
	- run `. env/bin/activate`
	- run `pip install -r requirements.txt`
	- run `python3 test7.py`
