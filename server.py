#!/usr/bin/python3 -u
# -*- mode:python; coding:utf-8; tab-width:4 -*-
import sys
import os
import Ice
import IceStorm
Ice.loadSlice('downloader.ice')
import Example
from work_queue import WorkQueue

class DownloaderI(Example.Downloader):
    def __init__(self, work_queue):
        self.work_queue = work_queue
        self.download_path = os.getcwd() + '/downloads'
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def download(self, url, current=None):
        f = Ice.Future()
        self.work_queue.add(f, url)
        return f

    def getSongsList(self, current=None):
        return os.listdir(self.download_path)

class Server(Ice.Application):
    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {0} not set".format(key))
            return None
        print("using icestorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, args):
        topic_mgr = self.get_topic_manager() #proxy to topic
        if not topic_mgr:
            print(': invalid proxy')
            return 2
        topic_name = "ProgressTopic"
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        publisher = topic.getPublisher()
        progress_topic = Example.ProgressSuscriberPrx.uncheckedCast(publisher)
        work_queue = WorkQueue(progress_topic)
        servant = DownloaderI(work_queue)
        ic = self.communicator()
        adapter = ic.createObjectAdapter("DownloadAdapter")
        print(adapter.add(servant, ic.stringToIdentity("downloader1")))
        adapter.activate()
        work_queue.start()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()
        work_queue.destroy()
        return 0
    
sys.exit(Server().main(sys.argv))
