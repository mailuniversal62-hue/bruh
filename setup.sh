cat > setup.sh << 'EOF'
#!/bin/bash
set -e
echo "[*] Creating venv..."
python3 -m venv venv
source venv/bin/activate
echo "[*] Installing deps..."
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p logs templates
echo "[+] Done. Run: source venv/bin/activate && python3 launcher.py"
EOF
chmod +x setup.sh
