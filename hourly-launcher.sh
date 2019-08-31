#!/bin/bash
cd "$(dirname "$0")";
./RPi_TempCheck_email.py 80 F > ./Log/hourly-log 2>&1
