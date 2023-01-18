#!/bin/bash

echo "Copying data from ~/stretch_user/$HELLO_FLEET_ID to the stretch_fleet repo..."
cp -rf ~/stretch_user/$HELLO_FLEET_ID/* ~/repos/stretch_fleet/robots/$HELLO_FLEET_ID/
echo "Removing mesh files from stretch_fleet..."
rm ~/repos/stretch_fleet/robots/$HELLO_FLEET_ID/exported_urdf/meshes/*
echo "Copying data from ~/stretch_user/$HELLO_FLEET_ID to /etc ..."
sudo cp -rf ~/stretch_user/$HELLO_FLEET_ID/* /etc/hello-robot/$HELLO_FLEET_ID/


cd ~/repos/stretch_fleet
git pull
git add *
git commit -m "${HELLO_FLEET_ID} ready to ship"
git push
