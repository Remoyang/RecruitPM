#!/bin/bash
cd /usr/local/server/recruitPM/
gunicorn manage:app  -w 2 -b 172.17.0.3:5000 -k gevent