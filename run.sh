#!/usr/bin/env bash
docker build -t web-monitor .
docker run -it --rm --name web-monitor-app web-monitor