#!/usr/bin/python3
# -*- coding: utf-8 -*-
"usage: {} <server> <value>"
import sys
import Ice
Ice.loadSlice('downloader.ice')
import Example

class Client(Ice.Application):
    def run(self, argv):
        base = self.communicator().stringToProxy(argv[1])
        math = Example.DownloadPrx.checkedCast(base)

        if not downloader:
            raise RuntimeError("invalid proxy")
        #print(math.factorial(int(argv[2])))
        return 0

if len(sys.argv) != 3:
    print(__doc__.format(__file__))
    sys.exit(1)

app = Client()
sys.exit(app.main(sys.argv))
