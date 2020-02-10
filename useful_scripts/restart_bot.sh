#! /bin/bash
Instance=$1
pkill --full bot.py
python3 bot.py $Instance &