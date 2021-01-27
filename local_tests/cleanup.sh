#!/bin/sh
docker-compose stop
docker-compose rm
rm -rf client server
mkdir -p client/share
echo "Test file client" > client/share/client_test***REMOVED***txt
mkdir -p server/shares
touch client/***REMOVED***gitkeep client/share/***REMOVED***gitkeep server/***REMOVED***gitkeep server/shares/***REMOVED***gitkeep