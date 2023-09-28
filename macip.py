#!/usr/bin/env python
'''
    RUN IN A VIRTUAL MACHINE to ensure that python -> python3

    This will be run as a cron job. It's purpose is to update the macip table in macip.db
    with the names of known machines on the network. A way to get name/ip since IP is by DHCP
'''

# update 16APR2023@19:47 - Mac crashed so updating for new release.

import os
import sqlite3
from datetime import datetime, timedelta
import machine

# 30APR2023 - this is the old date format when I was adjusting for Canada DST. Now I'm
# using Nairobi time (EAT) - so no need for a timedelta.
# logtime = datetime.now() + timedelta(hours=7)
logtime = datetime.now()

db = sqlite3.connect('/home/andrew/src/python/macip/macip.db')
db.row_factory = sqlite3.Row
cur = db.cursor()
sql = 'insert into log (logtime) values (?)'
cur.execute(sql,[logtime])
db.commit()

# the following command "arp-scan --localnet" returns a list of the following format:
#Interface: enP1p4s15f0, type: EN10MB, MAC: 00:0a:95:b9:f6:98, IPv4: 192.168.1.199
#Starting arp-scan 1.10.0 with 256 hosts (https://github.com/royhills/arp-scan)
#192.168.1.1     aa:bb:cc:dd:ee:ff       zte corporation
#192.168.1.13    ee:cc:cc:bb:aa:zz       Hangzhou Hikvision Digital Technology Co.,Ltd.
#192.168.1.3     nn:mm:oo:pp:qq:rr       Raspberry Pi Trading Ltd
#192.168.1.5     zz:yy:xx:oo:nn:ss       Raspberry Pi Trading Ltd

data = os.popen('sudo arp-scan --localnet')
data = data.read().split('\n')
# clear data in the macip table.
sql = 'delete from macip'
cur.execute(sql)
db.commit()

for line in data:
  line = line.strip().split()
  if len(line) > 2 and '192.168.1' in line[0]:
    sql = 'insert into macip (position, ip, mac, manufacturer) values (?, ?, ?, ?)'
    # look for the last number in the IP address (e.g., if 192.168.1.20 - return 20)
    r = line[0].rfind('.')
    position = int(line[0][r+1:])
    cur.execute(sql,[position,line[0],line[1].lower(),' '.join(line[2:])])
    db.commit()

# get a list of known machines/mac_addresses on the network. This is so that you can
# have human names to the output
machine_list = machine.machine_list

sql = 'update macip set machine = ? where mac = ?'

for machine in machine_list:
  cur.execute(sql, machine)
  db.commit()

sql = "delete from macip where manufacturer like '%Unknown%' and machine is null"
cur.execute(sql)
db.commit()

sql = "delete from macip where manufacturer like '%DUP:%'"
cur.execute(sql)
db.commit()
