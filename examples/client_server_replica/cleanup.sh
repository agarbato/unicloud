#!/bin/sh
docker-compose stop
docker-compose rm
rm -rf client client_replica server replica_server

echo "Create dirs.."
mkdir -p client/share client_replica/share  replica_server/share server/shares

echo "Create some files to test sync"
echo "Test file client" > client/share/client_test.txt
echo "Test file client" > client_replica/share/client_replica_test.txt

touch client/.gitkeep client/share/.gitkeep
touch client_replica/.gitkeep client_replica/share/.gitkeep
touch server/.gitkeep server/shares/.gitkeep replica_server/.gitkeep replica_server/share/.gitkeep
