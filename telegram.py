#!/usr/bin/env python
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
        self.keyboard = []
        self.row = []
        self.items_in_row = 3

        # Initialize DB
        self.conn = sqlite3.connect('telegram.db')
        self.c = self.conn.cursor()

        # Create tables
        self.c.execute('''create table if not exists Telegram (name STRING, last_name STRING, userid STRING UNIQUE)''')

        # Set keyboard buttons from commands.allowable_commands list
        for key in commands.allowable_commands.keys():
            self.row.append(key)
            if len(self.row) == self.items_in_row:
                self.keyboard.append(self.row)
                self.row = []

        self.reply_markup = ReplyKeyboardMarkup.create(self.keyboard)

        # Initialize bot
#         self.bot = TelegramBot('162715180:AAFvQCJjdpws6T3lp45t8svt9X-ENVd_zwo')
        self.bot = TelegramBot('172231085:AAHdG-B_ch2RTRXIupshiBpPqf7j21XLCik')
        self.bot.update_bot_info().wait()

    def _monitor():
        print("Monitor")

    def _listen():
        print("Listen")

    def new_user(self, name, lastname, userid):
        # Insert a row of data
        strr="INSERT INTO Telegram VALUES (\""+name+"\",\""+lastname+"\",\""+str(userid)+"\")"
        print(strr)
        # Save (commit) the changes
        try:
            self.c.execute(strr)
            self.conn.commit()
            self._send_message(userid, "Welcome, "+name+" "+lastname)
        except Exception as e:# sqlite3.IntegrityError:
            print(e)
            self._send_message(userid, "Thanks, "+name+" "+lastname+". No need to reregister")

    def handle_messages(self):
        while True:
            print ("Waiting for message in queue")
            message = self.queue.get()
            user_info = message[1]
            user_id = user_info[0]
            first_name = user_info[1]
            last_name = user_info[2]
            if last_name is None:
                last_name = "N/A"
            print ("Got and handle message "+str(message.text))
            res="Command not understood"
            try:
                #Extract the command
                cmd_list = message.text.split()
                if str(message.text) == "/start":
                    self.new_user(first_name, last_name, user_id)
                    continue
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
        self.bot.send_message(int(uid), message, reply_markup=self.reply_markup)

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
