#! /usr/bin/env python2

import socket
import os
from kazoo.client import KazooClient
from kazoo.client import KazooState

def zk_status(state):
	if state == KazooState.LOST:
		print 'lost session'
	elif state == KazooState.SUSPENDED:
		print 'disconnected from ZK'
	elif state == KazooState.CONNECTED:
		print 'connected'

# API 0.3 spec
# http://kazoo.readthedocs.org/en/0.3/api/client.html

zk = KazooClient( hosts='server1:2181,vmk1:2181,vmk2:2181' )
zk.add_listener( zk_status )
zk.start()
lock = zk.Lock('/master', '%s-%d' %(socket.gethostname(), os.getpid()))
zk.ensure_path("/path")
zk.set("/path", "data_string".encode('utf8')) 
start_key, stat = zk.get("/path")
