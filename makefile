all:

copy_binaries:
	mkdir -p /tmp/db/registry
	mkdir -p /tmp/db/node1
	mkdir -p /tmp/db/practica
	cp src/downloader.ice /tmp/db/practica
	cp src/Factory.py /tmp/db/practica
	cp src/SyncTimer.py /tmp/db/practica

node1:
	icepatch2calc /tmp/db/practica
	icegridnode --Ice.Config=src/node1.config
