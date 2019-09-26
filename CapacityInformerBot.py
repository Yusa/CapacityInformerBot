from telegram.ext import Updater
from telegram.ext import CommandHandler 
import json
import os
import requests

with open("bot.conf", "r") as f:
	CONFS = json.loads(f.read())


updater = Updater(token=CONFS['TOKEN'])
dispatcher = updater.dispatcher
j = updater.job_queue

ENDPOINT = CONFS['ENDPOINT']

total_list = {}
if os.path.exists("./backup_list"):
	with open("./backup_list", "r") as f:
		total_list = json.loads(f.read())



def checker(bot, job):
	global total_list, ENDPOINT
	for chat_id in total_list.keys():
		chat_id_key = str(chat_id)
		for crn in total_list[chat_id_key]:
			print("Trying now: {} => {}".format(chat_id_key, crn))
			URL = f"{ENDPOINT}{crn}"
			r = requests.get(URL)
			result_json = r.json()
			print("Result is: {}".format(result_json))
			if result_json != None:
				if result_json["space"] != 0:
					bot.send_message(chat_id=chat_id, text=f"Current empty space in course with CRN: {crn} is => {result_json['space']}")
					total_list[chat_id].remove(crn)
					update_total_list()


def stop(bot, update, args):
	global total_list
	chat_id = update.message.chat_id
	if len(args) == 1:
		crn = args[0]
		chat_id_key = str(chat_id)
		if crn in total_list[chat_id_key]:
			total_list[chat_id_key].remove(crn)
			bot.send_message(chat_id=chat_id, text=f"The course with CRN: {crn} is removed from your tracked course list.")
			update_total_list()
	else:
		bot.send_message(chat_id=chat_id, text="Give me a CRN Code")


def update_total_list():
	global total_list
	with open("backup_list", "w") as f:
		f.write(json.dumps(total_list))


def check_crn(bot, update, args):
	global total_list
	chat_id = update.message.chat_id
	chat_id_key = str(chat_id)
	if len(args) == 1:
		crn_code = args[0]
		if len(crn_code) == 5 and crn_code.isdigit():
			URL = f"{ENDPOINT}{crn_code}"
			r = requests.get(URL)
			result_json = r.json()
			print("Result is: ".format(result_json))
			if result_json != None:
				bot.send_message(chat_id=chat_id, text=f"Current empty space in class with CRN {crn_code} is => {result_json['space']}")
			if chat_id_key not in total_list.keys():
				total_list[chat_id_key] = [crn_code]
				update_total_list()
				bot.send_message(chat_id=chat_id, text=f"The course with {crn_code} is now tracked. When there is an available seat, you will be informed by a message.")
			elif crn_code not in total_list[chat_id_key]:
				total_list[chat_id_key].append(crn_code)
				update_total_list()
				bot.send_message(chat_id=chat_id, text=f"The course with {crn_code} is now tracked. When there is an available seat, you will be informed by a message.")
			else:
				bot.send_message(chat_id=chat_id, text=f"The course with {crn_code} is already tracked by you. If you would like to stop tracking use /stop command.")
		else:
			bot.send_message(chat_id=chat_id, text="Incorrect CRN Code")
	else:
		bot.send_message(chat_id=chat_id, text="Give me a CRN Code")


def list_crn(bot, update):
	global total_list
	chat_id = update.message.chat_id
	print(chat_id)
	print(total_list)
	chat_id_key = str(chat_id)
	if chat_id_key in total_list.keys():
		print("THERE")
		list_message = "The courses is actively tracked by you are: " + str(total_list[chat_id_key])
		print(list_message)
		bot.send_message(chat_id=chat_id, text=list_message)
	else:
		print("HERE")
		error_message = "You haven't traced any course yet."
		bot.send_message(chat_id=chat_id, text=error_message)


def help(bot, update):
	help_message = """	Commands:
							/check <CRNCODE>  (to start tracking a course)
							/list 		      (to list the courses you are tracking)
							/stop <CRNCODE>	  (to stop tracking a course)
						Example:
							/check 15132
							/list
							/stop 15132
							"""
	bot.send_message(chat_id=update.message.chat_id, text=help_message)


def start(bot, update):
	welcoming_message = """
	_________________________________________________
                  .......,        .
                '      ,           ``
             '      ,                . `
          '        `                     `
       '.     ,  `   `                `    .
         ' ,       `    `                   .
                      `   `            `
                        `    `         :     :
                           `   `             :
                             `    `   '
                                `   `       '
             ,                    `        '
           ,    `               '         `
         ,   , `.      `   '          , `   `
       ,   ,      `               ,       `   `
     ,   ,             `     '              `    `
    (  ,                                       `   )
     ~~                                          ~~
	_________________________________________________

    Wellcome to the Course Capacity Informer Bot.
    Usage:
    	/check <CRNCODE>
    Example:
    	/check 15132

    For more information use /help
    	"""
	bot.send_message(chat_id=update.message.chat_id, text=welcoming_message)


job1 = j.run_repeating(checker, interval=60, first=0)
job2 = j.run_repeating(checker, interval=60, first=30)


help_handler = CommandHandler('help', help)
start_handler = CommandHandler('start', start)
checkcrn_handler = CommandHandler('check', check_crn, pass_args=True)
listcrn_handler = CommandHandler('list', list_crn)
stopcrn_handler =CommandHandler('stop', stop, pass_args=True) 


dispatcher.add_handler(help_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(checkcrn_handler)
dispatcher.add_handler(listcrn_handler)
dispatcher.add_handler(stopcrn_handler)


updater.start_polling()
updater.idle()
