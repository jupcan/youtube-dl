#!/usr/bin/python3
# -*- mode:python; coding:utf-8; tab-width:4 -*-
'''
transfer file over ICE implementation
'''

#################
#               #
#  SERVER SIDE  #
#               #
#################

import binascii
import Ice
Ice.loadSlice('downloader.ice')
#pylint: disable=E0401
import Downloader

class TransferI(Downloader.Transfer):
    '''
    transfer file
    '''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current=None):
        '''send data block to client'''
        return str(binascii.b2a_base64(self.file_contents.read(size), newline=False))

    def end(self, current=None):
        '''close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)

#################
#               #
#  CLIENT SIDE  #
#               #
#################

import binascii
BLOCK_SIZE = 10240

def receive(transfer, destination_file):
    '''
    read a complete file using a Downloader; transfer object
    '''
    with open(destination_file, 'wb') as file_contents:
        remoteEOF = False
        while not remoteEOF:
            data = transfer.recv(BLOCK_SIZE)
            # Remove additional byte added by str() at server
            if len(data) > 1:
                data = data[1:]
            data = binascii.a2b_base64(data)
            remoteEOF = len(data) < BLOCK_SIZE
            if data:
                file_contents.write(data)
        transfer.end()
