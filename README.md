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




git clone


cd ~
git clone https://github.com/mailuniversal62-hue/bruh.git
cd bruh
mkdir -p logs templates
touch logs/.gitkeep


paste kali

cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
logs/*.log
logs/*.csv
logs/state.json
.env
config.local.py
EOF
