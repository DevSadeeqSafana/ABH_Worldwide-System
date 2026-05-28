# ABH WORLDWIDE MULTIPURPOSE COMPANY
## Inventory & Sales Management System

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FIRST-TIME SETUP (do this once)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Install Python from: https://www.python.org/downloads/
   ⚠️  IMPORTANT: During install, TICK "Add Python to PATH"

2. Double-click START.bat (Windows) or run: bash START.sh (Mac/Linux)

3. Your browser opens automatically. Log in with:
      Username : admin
      Password : admin1234

4. Go to My Profile → change your name, username and password.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  USING ON ONE COMPUTER ONLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Just double-click START.bat every time you want to use the system.
Your browser will open automatically at: http://localhost:5000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  USING ON MULTIPLE DEVICES (WiFi / LAN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This system can run on ONE main computer and be used from ANY
other device (phone, tablet, laptop) on the same WiFi — with
no extra software needed on those devices.

HOW IT WORKS:
  - Your main computer is the "server"
  - All other devices connect to it through your WiFi router
  - Other devices just open a browser — nothing to install

STEP 1: Set up the main (server) computer
  - Connect it to your WiFi router
  - Double-click START.bat
  - The black window will show two addresses like this:

        THIS COMPUTER  →  http://localhost:5000
        OTHER DEVICES  →  http://192.168.1.5:5000
                                   ↑
                          This is your LAN IP address.
                          It may be different on your network.

  - Keep this window open the whole time. Closing it stops the server.

STEP 2: Connect other devices
  Option A — Type the address manually (easiest):
    On any phone, tablet or laptop connected to the SAME WiFi,
    open any browser (Chrome, Safari, Firefox) and type:
        http://192.168.1.5:5000
    (use the exact address shown on your server screen)

  Option B — Use the shortcut file (most convenient):
    When the server starts, it creates a file called:
        CONNECT_FROM_OTHER_DEVICE.html
    Copy that file to a USB stick or send it via WhatsApp/email
    to the other device. Double-clicking it opens the app
    automatically — no typing needed.

  Option C — Save it as a bookmark:
    On the other device, open the address in the browser,
    then bookmark it / add to home screen. One tap from then on.

TIPS:
  ✔  The server computer does NOT need internet — just WiFi
  ✔  All devices see the same live data instantly
  ✔  Works on Windows, Mac, Android, iPhone, any tablet
  ✔  Up to 20+ devices can connect at the same time
  ✔  If the IP address changes (uncommon), just check the
     server window again and update the bookmark

TROUBLESHOOTING:
  "Cannot connect" on other device?
    → Make sure all devices are on the SAME WiFi network
    → Make sure the server (START.bat) is still running
    → Try turning off Windows Firewall temporarily, or add
      Python as an exception in firewall settings
    → Check the IP shown on the server screen matches what
      you typed in the browser

  Windows Firewall prompt:
    When you first run START.bat, Windows may ask
    "Allow Python to communicate on this network?"
    → Click "Allow Access" — this is required for other
      devices to connect.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FILES IN THIS FOLDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  START.bat                    → Double-click to launch (Windows)
  START.sh                     → Launch on Mac/Linux
  app.py                       → Main application
  requirements.txt             → Python packages needed
  templates/index.html         → The interface
  abh_worldwide.db             → Your database (auto-created)
  CONNECT_FROM_OTHER_DEVICE    → Auto-created shortcut for
  .html                          other devices (after first run)

  ⚠️  BACKUP: Copy abh_worldwide.db regularly to keep your data safe.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DATA & BACKUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  All data is stored in:  abh_worldwide.db
  To back up:  Copy that one file to a USB drive or cloud storage.
  To restore:  Replace the file with your backed-up copy.
  SQLite handles millions of records — suitable for 10+ years of use.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ABH Worldwide Multipurpose Company
  Built with Python Flask + SQLite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
