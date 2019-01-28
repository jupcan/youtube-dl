#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import sys
import os.path
from threading import Thread
from queue import Queue
import binascii
import youtube_dl
import Ice
# pylint: disable=E0401
import IceStorm
Ice.loadSlice('downloader.ice')
from Downloader import *
# pylint: disable=E1101
# pylint: disable=E0602

class NullLogger:
    '''logger used to disable youtube-dl output'''
    def debug(self, msg):
        '''ignore debug messages'''

    def warning(self, msg):
        '''ignore warnings'''

    def error(self, msg):
        '''ignore errors'''

#youtube-dl default configuration
DOWNLOADER_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': NullLogger()
}

def _download_mp3_(url, destination='./'):
    '''synchronous download from youtubez'''
    options = {}
    task_status = {}
    def progress_hook(status):
        task_status.update(status)
    options.update(DOWNLOADER_OPTS)
    options['progress_hooks'] = [progress_hook]
    options['outtmpl'] = os.path.join(destination, '%(title)s.%(ext)s')
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])
    filename = task_status['filename']
    # BUG: filename extension is wrong, it must be mp3
    filename = filename[:filename.rindex('.') + 1]
    return filename + options['postprocessors'][0]['preferredcodec']

class WorkQueue(Thread):
    '''job queue to dispatch tasks'''
    QUIT = 'QUIT'
    CANCEL = 'CANCEL'

    def __init__(self, scheduler):
        super(WorkQueue, self).__init__()
        self.scheduler = scheduler
        self.queue = Queue()

    def run(self):
        '''task dispatcher loop'''
        for job in iter(self.queue.get, self.QUIT):
            job.download()
            self.queue.task_done()
        self.queue.task_done()
        self.queue.put(self.CANCEL)

        for job in iter(self.queue.get, self.CANCEL):
            job.cancel()
            self.queue.task_done()
        self.queue.task_done()

    def send_status(self, url, status):
        '''notify data status'''
        status_data = ClipData()
        status_data.URL = url
        status_data.status = status
        self.scheduler.stats.notify(status_data)

    def add(self, callback, url):
        '''add new task to queue'''
        self.send_status(url, Status.PENDING)
        self.queue.put(Job(callback, url, self))

    def destroy(self):
        '''cancel tasks queue'''
        self.queue.put(self.QUIT)
        self.queue.join()

class Job:
    '''task: clip to download'''
    def __init__(self, callback, url, work_queue):
        self.callback = callback
        self.url = url
        self.work_queue = work_queue

    def download(self):
        '''donwload clip'''
        self.work_queue.send_status(self.url, Status.INPROGRESS)
        result = _download_mp3_(self.url)
        self.work_queue.scheduler.SongList.add(result)
        self.work_queue.send_status(self.url, Status.DONE)
        self.callback.set_result(result)

    def cancel(self):
        '''cancel donwload'''
        self.work_queue.send_status(self.url, Status.ERROR)
        self.callback.ice_exception(SchedulerCancelJob())

class TransferI(Transfer):
    '''transfer file'''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current=None):
        '''send data block to client'''
        return str(binascii.b2a_base64(self.file_contents.read(size), newline=False))

    def end(self, current=None):
        '''close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)

class DownloadSchedulerI(DownloadScheduler, SyncEvent):
    '''servidores de descarga'''
    def __init__(self, name):
        self.publicador = None
        self.stats = None
        self.SongList = set()
        self.name = name
        self.path = "./"
        self.cola_trabajo = WorkQueue(self)
        self.cola_trabajo.start()

    def getSongList(self, current=None):
        '''obtener lista de canciones'''
        return list(self.SongList)

    def addDownloadTask(self, url, current=None):
        '''añadir tarea de descargar a la cola'''
        callback = Ice.Future()
        self.cola_trabajo.add(callback, url)
        print('downloader {}: descargando canción de {}'.format(self.name, url))
        return callback

    def get(self, song, current=None):
        '''transferir archivo al cliente'''
        print('downloader {}: preparándose para transferir la canción {}'.format(self.name, song))
        controller = TransferI('{}{}'.format(self.path, song))
        prx = current.adapter.addWithUUID(controller)
        transfer = TransferPrx.checkedCast(prx)
        return transfer

    def requestSync(self, current=None):
        '''petición de sincronización entre servidores'''
        self.publicador.notify(list(self.SongList))

    def notify(self, songs, current=None):
        '''notify canciones existentes en local'''
        songs = set(songs)
        self.SongList = self.SongList.union(songs)

    def cancelTask(url):
        '''cancelar tarea de la cola'''
        print('procesando...')

class SchedulerFactoryI(SchedulerFactory):
    '''implementacion de factoria'''
    def __init__(self, adapter, ic, synctopic, statstopic):
        self.synctopic = synctopic
        self.statstopic = statstopic
        self.adapters, self.names, self.ids = [], [], []
        self.ic = ic
        self.adapter = adapter

    def availableSchedulers(self, current=None):
        '''número de servidores desplegados'''
        return len(self.names)

    def kill(self, name, current=None):
        '''eliminar servidor'''
        indice = 0
        encontrado = False
        if name in self.names:
            print('downloader {}: cerrando...'.format(name))
            id = Ice.stringToIdentity(name)
            for i in range(0, len(self.adapters)):
                if self.ids[i] == id:
                    current.adapter.remove(id)
                    indice = i
                    encontrado = True
            if encontrado:
                self.synctopic.unsubscribe(self.adapters[indice])
                del self.adapters[indice]
                del self.ids[indice]
                del self.names[indice]
        else:
            raise SchedulerNotFound()

    def make(self, name, current=None):
        '''crear nuevo servidor'''
        if not name in self.names:
            self.names.append(name)
            print('downloader {}: creándose...'.format(name))
            properties = self.ic.getProperties()
            id = Ice.stringToIdentity(name)
            self.ids.append(id)
            controller = DownloadSchedulerI(name)
            qos = {}
            prx = current.adapter.add(controller, id)
            self.synctopic.subscribeAndGetPublisher(qos, prx)
            sync = self.synctopic.getPublisher()
            self.adapters.append(sync)
            controller.publicador = SyncEventPrx.uncheckedCast(sync)
            statsproxy = self.statstopic.getPublisher()
            controller.stats = ProgressEventPrx.uncheckedCast(statsproxy)
            downloader = DownloadSchedulerPrx.checkedCast(prx)
        else:
            raise SchedulerAlreadyExists()
        return DownloadSchedulerPrx.checkedCast(prx)

class Server(Ice.Application):
    '''canales de eventos'''
    def get_topic_manager(self):
        key = 'Practica.IceStorm/TopicManager'
        proxy = self.communicator().stringToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None

        print("using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        '''creación de canales'''
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("invalid proxy")
            return 2

        ic = self.communicator()
        adapter = ic.createObjectAdapter("PrinterAdapter")
        topic_name2 = "ProgressTopic"
        topic_name1 = "SyncTopic"

        try:
            synctopic = topic_mgr.retrieve(topic_name1)
        except IceStorm.NoSuchTopic:
            synctopic = topic_mgr.create(topic_name1)
        try:
            statstopic = topic_mgr.retrieve(topic_name2)
        except IceStorm.NoSuchTopic:
            statstopic = topic_mgr.create(topic_name2)

        servant = SchedulerFactoryI(adapter, ic, synctopic, statstopic)
        subscriber = adapter.addWithUUID(servant)
        print("waiting events... '{}'".format(subscriber))

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()
        return 0

SERVER = Server()
sys.exit(SERVER.main(sys.argv))
