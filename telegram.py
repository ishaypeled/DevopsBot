#!/bin/python
from twx.botapi import TelegramBot, ReplyKeyboardMarkup
import sqlite3
import shlex
import os
import subprocess
import commands
import thread
from multiprocessing import Queue
from Command import Command

class DevopsBot:
    def __init__(self):
        self.bot=None
        self.conn=None
        self.c=None
        self.queue=Queue()

        # Initialize DB
        self.conn = sqlite3.connect('telegram.db')
        self.c = self.conn.cursor()
        
        # Create tables
        self.c.execute('''create table if not exists Telegram (name STRING, last_name STRING, userid STRING UNIQUE)''')

        # Initialize bot
        self.bot = TelegramBot('162715180:AAFvQCJjdpws6T3lp45t8svt9X-ENVd_zwo')
        self.bot.update_bot_info().wait()

    def _monitor():
        print "Monitor"

    def _listen():
        print "Listen"

    def new_user(self, name, lastname, userid):
        # Insert a row of data
        strr="INSERT INTO Telegram VALUES (\""+name+"\",\""+lastname+"\",\""+str(userid)+"\")"
        print(strr)
        # Save (commit) the changes
        try:
            self.c.execute(strr)
            self.conn.commit()
            self._send_message(userid, "Welcome, "+name+" "+lastname)
        except:# sqlite3.IntegrityError:
            self._send_message(userid, "Thanks, "+name+" "+lastname+". No need to reregister")

    def handle_messages(self):
        while True:
            print ("Waiting for message in queue")
            message = self.queue.get()
            print ("Got and handle message "+str(message.text))
            res="Command not understood"
            try:
                #Extract the command
                cmd_list = message.text.split()
                #Replace protocol command with OS command
                cmd = commands.allowable_commands[cmd_list[0]]
                cmd_list[0] = cmd
                runner = Command(cmd_list)
                runner.run(5)
                print("RES "+str(runner.res)+" /RES")
                self._send_message(message.sender.id, runner.res)
            except Exception as e:
                print ("Except: "+str(e))

    def _send_message(self, uid, message):
        self.bot.send_message(int(uid), message)

    def listen(self):
        offset=0
        while (True):
            updates = self.bot.get_updates(offset).wait()
            for cnt,update in enumerate(updates):
                offset=update.update_id+1
                print("Putting message: "+str(update.message.text))
                self.queue.put(update.message)
        
if (__name__ == "__main__"):
    botInstance = DevopsBot()
    thread.start_new_thread(botInstance.handle_messages, ())
    botInstance.listen()
