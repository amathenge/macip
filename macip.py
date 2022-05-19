#!/usr/bin/python3
import os
import sqlite3
from datetime import datetime, timedelta
import machine

logtime = datetime.now() + timedelta(hours=7)

db = sqlite3.connect('/home/andrew/src/python/showip/macip.db')
db.row_factory = sqlite3.Row
cur = db.cursor()
sql = 'insert into log (logtime) values (?)'
cur.execute(sql,[logtime])
db.commit()

data = os.popen('sudo arp-scan --localnet')
data = data.read().split('\n')
sql = 'delete from macip'
cur.execute(sql)
db.commit()

for line in data:
  line = line.strip().split()
  if len(line) > 2 and '192.168.1' in line[0]:
    sql = 'insert into macip (position, ip, mac, manufacturer) values (?, ?, ?, ?)'
    r = line[0].rfind('.')
    position = int(line[0][r+1:])
    cur.execute(sql,[position,line[0],line[1].lower(),' '.join(line[2:])])
    db.commit()

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

