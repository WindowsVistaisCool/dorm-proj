#!/bin/sh

replace_code() {
    # move contents from ~/temp to ~/deploy

    cd ~
    rm -rf ./deploy/

    mkdir deploy
    cp -r ./temp/* ./deploy/

    cd deploy

    chmod +x ./main.py

    echo "Code replaced successfully."
}

cd /home/kiosk/deploy

# check if X is running
if ! timeout 1s xset q &>/dev/null; then
    # kill existing window process if it exists
    task_pid=$(cat /home/kiosk/deploy/window.pid)
    if [[ -z $task_pid ]]; then
        echo "No existing window process found."
        task_pid=0
    else
        echo $task_pid
        echo "Killing existing window process with PID $task_pid..."
        kill $task_pid
    fi

    sleep 0.5

    replace_code

    DISPLAY=:0 xset s reset # reset screensaver 
    DISPLAY=:0 python3 ./main.py & # launch new app

    echo "Launched successfully."

else
    echo "DISPLAY is not set, skipping window launch."
    replace_code
fi