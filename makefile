all:

clean:
	$(RM) *~ server.proxy

run-server:
	./server.py --Ice.Config=Server.config | tee server.proxy

run-client:
	./client.py '$(shell head -1 server.proxy)' 4
