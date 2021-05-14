#! /bin/bash
sudo apt-get update
sudo apt-get install -y python3.7
python3 -m pip install pandas
python3 -m pip install selenium
python3 -m pip install webdriver_manager
python3 -m pip install six==1.15.0
python3 -m pip install openpyxl
python3 -m pip install xlrd>=1.0.0
python3 -m pip install google-cloud-storage
sudo python3 /home/ajimenez/ui-automation/ui-auto.py