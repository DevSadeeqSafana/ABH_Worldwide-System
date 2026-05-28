#!/bin/bash
clear
echo ""
echo "  ============================================================"
echo "    ABH WORLDWIDE MULTIPURPOSE COMPANY"
echo "    Inventory & Sales Management System"
echo "  ============================================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "  [ERROR] Python 3 is not installed."
    echo "  Download from: https://www.python.org"
    exit 1
fi

echo "  Installing dependencies..."
pip3 install flask flask-sqlalchemy werkzeug --quiet 2>/dev/null

echo "  Starting server..."
echo ""
echo "  Once started, check the network address printed below."
echo "  Other devices on the same WiFi can use that address."
echo ""

python3 app.py
