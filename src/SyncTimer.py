#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('downloader.ice')
import Downloader
import time

KEY = 'Practica.IceStorm/TopicManager'
TOPIC_NAME = 'SyncTopic'

class SyncTimer(Ice.Application):
   def run(self, args):
      broker = self.communicator()
      topic_mgr_proxy = self.communicator().stringToProxy(KEY) #get topic manager
      if topic_mgr_proxy is None:
         print("property {0} not set".format(KEY))
         return 1
      topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
      if not topic_mgr:
         print(': invalid proxy')
         return 2
      try:
         topic = topic_mgr.retrieve(TOPIC_NAME) #get topic
      except IceStorm.NoSuchTopic:
         topic = topic_mgr.create(TOPIC_NAME)
      publisher  = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())

      while True:
         print('sync requested')
         publisher.requestSync() #publish events
         time.sleep(5.0)
      return 0

if __name__ == '__main__':
    app = SyncTimer()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
