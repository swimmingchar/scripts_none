#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

class MyHandler(LoggingEventHandler):
    def on_modified(self, event):
        print("%s is dir,%sis dst." %(event.src_path, event.dest_path))
    
    def on_moved(self,event):
        pass
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()