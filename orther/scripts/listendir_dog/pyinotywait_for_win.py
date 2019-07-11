#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import time
import yaml

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import configparser2 as config 



def listendog():
    path = "c:\Import\help\"
    event_handler = LoggingEventHandler()
    observer = Observer
    observer.schedule(event_handler, path, recursize=True) 
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    config_file = os.path.dirname(os.path.realpath(__file__)) + '\config\config.yml'
    configs = yaml.load(open(config_file, 'r'))
    conns = configs.get('')
    parser = config.ConfigParser()
    parser.read_file(config_file)
    