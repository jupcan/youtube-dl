#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import Ice
# pylint: disable=E0401
import IceStorm
Ice.loadSlice('downloader.ice')
import Downloader
# pylint: disable=E1101

KEY = 'Practica.IceStorm/TopicManager'
TOPIC_NAME = 'SyncTopic'

class SyncTimer(Ice.Application):
    '''server to sync downloader objects'''
    def run(self, args):
        '''subscribe to SyncTopic and notify'''
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
        publisher = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())

        while True:
            print('sync requested')
            publisher.requestSync() #publish events
            time.sleep(5.0)
        return 0

if __name__ == '__main__':
    APP = SyncTimer()
    EXIT_STATUS = APP.main(sys.argv)
    sys.exit(EXIT_STATUS)
