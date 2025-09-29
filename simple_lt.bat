@echo off
echo Installing LocalTunnel...
npm install -g localtunnel

echo Starting tunnels...
start "Main Panel" cmd /k "lt --port 5000"
start "User Panel" cmd /k "lt --port 8080"

echo Done! Check the opened windows for tunnel URLs.
pause