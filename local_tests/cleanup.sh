#!/bin/sh
docker-compose stop
docker-compose rm
rm -rf client server
mkdir -p client/share
echo "Test file client" > client/share/client_test.txt
mkdir -p server/shares
touch client/.gitkeep client/share/.gitkeep server/.gitkeep server/shares/.gitkeep