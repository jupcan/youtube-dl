#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import binascii
import time
import Ice
# pylint: disable=E0401
Ice.loadSlice('src/downloader.ice')
import Downloader
# pylint: disable=E1101
# pylint: disable=E0602

BLOCK_SIZE = 10240

class ProgressStatus(Downloader.ProgressEvent):
    '''clip progress status'''
    def __init__(self, client):
        self.client = client

    def notify(self, clipdata, current=None):
        '''notify status'''
        if self.client is None:
            return
        self.client.diccionario[clipdata.URL] = clipdata.status

def receive(transfer, destination_file):
    '''receive file from download server'''
    with open(destination_file, 'wb') as file_contents:
        remoteEOF = False
        while not remoteEOF:
            data = transfer.recv(BLOCK_SIZE)
            if len(data) > 1:
                data = data[1:]
            data = binascii.a2b_base64(data)
            remoteEOF = len(data) < BLOCK_SIZE
            if data:
                file_contents.write(data)
        transfer.end()

class User(Ice.Application):
    '''client class starting without servers'''
    def __init__(self):
        self.servers = {}

    def Opciones(self, current=None):
        '''opciones del menú'''
        print('1.crear nuevo servidor\n2.eliminar servidor\n3.ver lista de' \
        'canciones\n4.descargar canción\n5.obtener canción\n6.servidores des'\
        'plegados\n7.salir de la aplicación')

    def Actuar(self, x, prx, current=None):
        '''acciones de cada una de las opciones'''
        if x == 1:
            name = input('introduzca el nombre del servidor: ')
            try:
                nuevo = prx.make(name)
                self.servers[name] = nuevo
            except Downloader.SchedulerAlreadyExists:
                print('error: scheduler ya existe')

        elif x == 2:
            name = input('introduzca el nombre del servidor a eliminar: ')
            try:
                prx.kill(name)
                del self.servers[name]
            except Downloader.SchedulerNotFound:
                print('error: scheduler no encontrado')

        elif x == 3:
            name = input('servidor al que realizar la solicitud: ')
            if name in self.servers:
                res = self.servers[name].getSongListAsync()
                while res.running():
                    print('obteniendo lista de canciones...')
                    time.sleep(1.0)
                    if res.done():
                        print('[obtenida]')
                        lista = res.result()
                        for x in lista:
                            print(x)
            else:
                print('error')

        elif x == 4:
            name = input('servidor al que realizar la solicitud: ')
            if name in self.servers:
                URL = input('introduce la url: ')
                res = self.servers[name].addDownloadTaskAsync(URL)
                while res.running():
                    print('descargando...')
                    time.sleep(1.0)
                    if res.done():
                        print('[descargada]')
            else:
                print('error')

        elif x == 5:
            name = input('servidor al que realizar la solicitud: ')
            if name in self.servers:
                cancion = input('introduce el nombre de la canción: ')
                res = self.servers[name].getAsync(cancion)
                while res.running():
                    print('transfiriendo...')
                    time.sleep(1.0)
                    if res.done():
                        print('[transferida]')
                        prx_transf = res.result()
                cancion = input('nuevo nombre de la canción: ')
                nueva = cancion+".mp3"
                receive(prx_transf, nueva)
            else:
                print('error')

        elif x == 6:
            n = prx.availableSchedulers()
            print("%d servidor/es: %s" %  (n, list(self.servers.keys())))

        elif x == 7:
            print('ha seleccionado salir')
        else:
            print('opción incorrecta')

    def Main(self, prx, current=None):
        '''main'''
        if prx.availableSchedulers() > 0:
            self.Opciones()
            x = int(input('introduzca una opción: '))
            if x != 7:
                self.Actuar(x, prx)
                self.Main(prx)
        else:
            posible = False
            while not posible:
                name = input('introduzca el nombre de un servidor: ')
                try:
                    nuevo = prx.make(name)
                    posible = True
                    self.servers[name] = nuevo
                except Downloader.SchedulerAlreadyExists:
                    print('error: scheduler ya existe')
                    posible = False
                if not posible:
                    print('vuelva a intentarlo')
            self.Main(prx)

    def run(self, argv):
        '''communication with factory'''
        proxy = self.communicator().stringToProxy(argv[1])
        factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)
        if not factory:
            raise RuntimeError('proxy factoría inválido')
        self.Main(factory)
        print('finalizando ejecución')
        return 0

sys.exit(User().main(sys.argv))
