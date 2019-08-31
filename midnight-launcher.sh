#!/bin/bash
cd "$(dirname "$0")";
./RPi_TempCheck_email.py 80 T > ./Log/midnight-log 2>&1
