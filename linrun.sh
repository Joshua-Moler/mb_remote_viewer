cd ./status_server && gnome-terminal --title="STATUS SERVER" -- python3 statusServer.py
cd ../backend && gnome-terminal --title="REMOTE BACKEND" -- python3 main.py
cd ../frontend && gnome-terminal --title="REMOTE FRONTEND" -- npm start
cd ../controller && gnome-terminal --title="REMOTE DAEMON" -- python3 remote_daemon.py; gnome-terminal --title="CONTROLLER BACKEND" -- python3 main.py
cd ../ && gnome-terminal -- bash