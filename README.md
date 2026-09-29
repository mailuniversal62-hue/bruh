# install, configure, run
cd ~/acetrader
chmod +x setup.sh
./setup.sh

nano config.py
# set POCKET_SSID = "..."
# save: Ctrl+O, Enter, Ctrl+X

source venv/bin/activate
python3 launcher.py

push to GitHub (once it runs)
git add .
git commit -m "Initial commit"
git push
