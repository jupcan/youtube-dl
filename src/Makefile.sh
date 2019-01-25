#!/bin/sh

echo "creando directorios"
mkdir -p /tmp/db/registry
mkdir -p /tmp/db/node1

echo "copiando binarios"
mkdir -p /tmp/db/practica
cp downloader.ice /tmp/db/practica
cp Factory.py /tmp/db/practica
cp SyncTimer.py /tmp/db/practica
icepatch2calc /tmp/db/practica
icegridnode --Ice.Config=node1.config
