#!/bin/bash

# Start the ADB server
adb start-server

# Wait for ADB server to start
sleep 2

# Run the Python script passed as arguments
exec "$@"