# =======================================================================
#  Copyleft CityArtsTeam 2018-∞.
#  Distributed under the terms of the MIT License.
#  (See accompanying file LICENSE or copy at
#   https://opensource.org/licenses/MIT)
# =======================================================================

import json, requests
import configparser
import subprocess
import time
import logging
import sqlite3
import mcrcon
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# conn = sqlite3.connect('cityarts.db')
# c = conn.cursor()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


config = configparser.ConfigParser()
config.read('bot.conf') ## Read Bot Config file

updater = Updater(token=config['KEYS']['bot_api']) ## Get updates from Telegram Bot API
dispatcher = updater.dispatcher

# -----------------------------------------------------
#   Normal Commands
# -----------------------------------------------------

def start(bot, update):
    update.message.reply_text("안녕하세요! 여러분의 친구, CityArts Official Bot 입니다.\n"
                              "명령어를 보시려면 /help 를 입력해주시면 감사하겠습니다!\n"
                              "\n"
                              "Hello, It's you're friend, CityArts Official Bot.\n"
                              "If you want see commands, please send /help thanks!")

def stop(bot, update):
    update.message.reply_text("CityArts Official Bot 을 정지합니다.\n"
                              "다시 시작하시려면 /start 를 입력해주시면 감사하겠습니다.\n"
                              "\n"
                              "Stopping CityArts Official Bot.\n"
                              "If you want restart, please enter /start.")

def help(bot, update):
    update.message.reply_text("CityArts Official Bot 은 다음과 같이 사용할 수 있습니다.\n"
                              "/start - CityArts Official Bot 을 시작합니다.\n"
                              "/stop - CityArts Official Bot 를 중지합니다.\n"
                              "/help - CityArts Official Bot 의 도움말을 표시합니다.\n"
                              "/map - CityArts 서버의 지도를 표시합니다.\n"
                              "/trains - CityArts 서버의 철도 노선도를 표시합니다.\n"
                              "/report [문자] - IPA 에 서버의 문제점을 제보합니다.\n"
                              "/status - CityArts 서버의 상태를 표시합니다.\n"
                              "\n"
                              "The CityArts Official Bot can be used as follows.\n"
                              "/start - Start CityArts Official Bot.\n"
                              "/stop - Stop CityArts Official Bot.\n"
                              "/help - Displays help for CityArts Official Bot.\n"
                              "/map - Displays a map of CityArts.\n"
                              "/trains - Displays a railway route map of CityArts.\n"
                              "/report [Text] - Report complaints to IPA.\n"
                              "/status - Displays the status of CityArts.")

def map(bot, update):
    update.message.reply_photo(open("resources/map.jpg", 'rb'), 
                              "다음은 CityArts 의 지도입니다.\n"
                              "실시간 지도 확인은 live.cityarts.ga 에서 하실 수 있습니다.\n"
                              "Here is a map of CityArts.\n"
                              "Real-time map confirmation is available at live.cityarts.ga.")

def trains(bot, update):
    update.message.reply_photo(open("resources/trains_map.jpg", 'rb'), 
                              "다음은 CityArts 의 철도 노선도 입니다.\n"
                              "Here is a railroad map of CityArts.")

def status(bot, update):
    url = 'https://mcapi.us/server/status'

    params = dict(
        ip='cityarts.ga'
    )

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)

    text = ("서버 주소 : cityarts.ga\n"
           "서버 상태 : {}\n"
           "플레이어 : {} / {}\n"
           "서버 버전 : {}\n"
           "\n"
           "Server Address : cityarts.ga\n"
           "Server Status : {}\n"
           "Players : {} / {}\n"
           "Server Version : {}".format(server_status(data["online"]), data["players"]["max"], data["players"]["now"], data["server"]["name"], server_status(data["online"]), data["players"]["max"], data["players"]["now"], data["server"]["name"]))

    update.message.reply_text(text)

def server_status(status):
    if status:
        return "ON ✅"

    return "OFF ❎"

def report(bot, update):
    text = ' '.join(update.message.text.split()[1:])

    if text:
        update.message.reply_text("IPA 로 해당 내용이 전송되었습니다.\n"
                                  "제보해주셔서 감사드립니다.\n"
                                  "\n"
                                  "Your content has been sent to IPA.\n"
                                  "Thank you for reporting.")
        bot.send_message(config['GROUPS']['ipa_group_id'], "여러분께 알립니다.\n"
                         "다음과 같은 제보가 들어왔습니다.\n"
                         "\n"
                         "사용자 이름 : " + update.message.from_user.first_name + " ( @" + update.message.from_user.username + " )\n"
                         "내용 : " + text + "\n"
                         "참고 부탁드리겠습니다 감사합니다.")
    else:
        update.message.reply_text("위 커맨드는 IPA에 제보하기 위한 명령어입니다.\n"
                                  "사용법 : /report [내용]\n"
                                  "\n"
                                  "The above command is a command to report to IPA.\n"
                                  "Usage : /report [Text]")

def welcome(bot, update):
    if int(update.message.chat.id) == int(config['GROUPS']['group_id']):
        update.message.reply_text("안녕하세요! 여러분의 친구, CityArts Official Bot 입니다.\n"
                                  "CityArts 의 서버원이 되신걸 진심으로 환영합니다!\n"
                                  "화이트리스트 등록은 명령어 /add 를 입력해주시면 감사드리겠습니다.\n"
                                  "\n"
                                  "Hello, It's you're friend, CityArts Official Bot.\n"
                                  "Welcome to CityArts!"
                                  "If you want to register whitelist, please enter command /add.")
    if int(update.message.chat.id) == int(config['GROUPS']['ipa_group_id']):
        update.message.reply_text("안녕하세요! 여러분의 친구, CityArts Official Bot 입니다.\n"
                                  "IPA 수사관이 되신것을 진심으로 축하드립니다!\n"
                                  "\n"
                                  "Hello, It's you're friend, CityArts Official Bot.\n"
                                  "Congratulations on being an IPA investigator!")
    if int(update.message.chat.id) == int(config['GROUPS']['public_group_id']):
        update.message.reply_text("안녕하세요! 여러분의 친구, CityArts Official Bot 입니다.\n"
                                  "CityArts 의 서버원이 되신걸 진심으로 환영합니다!\n"
                                  "화이트리스트 등록은 명령어 /add 를 입력해주시면 감사드리겠습니다.\n"
                                  "\n"
                                  "Hello, It's you're friend, CityArts Official Bot.\n"
                                  "Welcome to CityArts!"
                                  "If you want to register whitelist, please enter command /add.")
    
def wiki(bot, update):
    text = ' '.join(update.message.text.split()[1:])
    
    if text:
        url = 'https://wiki.cityarts.ga/search/' + text

        resp = requests.get(url)
        
        if resp.text.find("문서가 없습니다.") == -1:
            update.message.reply_text("wiki.cityarts.ga/w/{} 에서 해당 문서를 보실 수 있습니다.\n"
                                      "You can find this document in wiki.cityarts.ga/w/{}.".format(text, text))
        else:
            update.message.reply_text("죄송합니다. {} 문서를 찾을 수 없습니다."
                                      "Sorry. {} Document not found".format(text, text))
    else:
        update.message.reply_text("위 커맨드는 문서를 검색하기 위한 명령어입니다.\n"
                                  "사용법 : /wiki [내용]\n"
                                  "\n"
                                  "The above command is for searching documents.\n"
                                  "Usage : /wiki [Text]")

def add(bot, update):
    rcon.connect(config['RCON']['server_ip'], int(config['RCON']['server_port']), config['RCON']['server_password'])

    user_list = ['']

    response = rcon.command("whitelist list")
    while True:
        if response:
            response = response.replace('§ePlayers in whitelist.txt: §f', '')
            response = response.replace('§ePlayers in whitelist.txt: §f', '')
            user_list = response.split(', ')
            break

    rcon.disconnect()

# -----------------------------------------------------
#   [Filters.text] Handler
# -----------------------------------------------------

def text(bot, update):
    text = ' '.join(update.message.text.split()[:1])
    isAdmin = False

    for id in config['ADMIN']['id'].split("|"):
        if int(id) == int(update.message.from_user.id):
            isAdmin = True

    if text == "!rcon":
        rcon(bot, update, isAdmin)
    elif text == "!reload":
        reload(bot, update, isAdmin)
    elif text == "!broadcast":
        broadcast(bot, update, isAdmin)
    elif text == "!restart":
        restart(bot, update, isAdmin)

# -----------------------------------------------------
#   Administer ONLY Commands
# -----------------------------------------------------

def rcon(bot, update, isAdmin):
    text = ' '.join(update.message.text.split()[1:])
    command = ' '.join(text.split()[0:])

    if isAdmin:
        if text:
            rcon = mcrcon.MCRcon()
            rcon.connect(config['RCON']['server_ip'], int(config['RCON']['server_port']), config['RCON']['server_password'])
            update.message.reply_text("해당 명령어를 실행중입니다...\n"
                                      "Running this command...")

            response = rcon.command(command)

            update.message.reply_text("성공적으로 실행되었습니다.\n"
                                      "Successfully executed.")

            rcon.disconnect()
        else:
            update.message.reply_text("위 커맨드는 RCON 에서 명령어를 실행하는 명령어입니다.\n"
                                      "사용법 : !rcon [내용]\n"
                                      "\n"
                                      "The above command is a command to execute command on RCON.\n"
                                      "Usage : !rcon [Text]")
    else:
        update.message.reply_text("죄송합니다. 해당 명령어는 관리자만 수행할 수 있습니다.\n"
                                  "Sorry. This command can only be executed by the administrator.")


def reload(bot, update, isAdmin):
    if isAdmin:
        rcon = mcrcon.MCRcon()
        rcon.connect(config['RCON']['server_ip'], int(config['RCON']['server_port']), config['RCON']['server_password'])
        
        update.message.reply_text("해당 명령어를 실행중입니다...\n"
                                  "Running this command...")

        response = rcon.command("reload")
        while True:
            if response:
                update.message.reply_text("성공적으로 실행되었습니다.\n"
                                          "Successfully executed.")
                break
        
        rcon.disconnect()
    else:
        update.message.reply_text("죄송합니다. 해당 명령어는 관리자만 수행할 수 있습니다.\n"
                                  "Sorry. This command can only be executed by the administrator.")

def broadcast(bot, update, isAdmin):
    text = ' '.join(update.message.text.split()[1:])

    if isAdmin:
        rcon = mcrcon.MCRcon()
        rcon.connect(config['RCON']['server_ip'], int(config['RCON']['server_port']), config['RCON']['server_password'])
        update.message.reply_text("해당 명령어를 실행중입니다...\n"
                                  "Running this command...")

        response = rcon.command("broadcast " + text)

        update.message.reply_text("성공적으로 실행되었습니다.\n"
                                  "Successfully executed.")

        rcon.disconnect()
    else:
        update.message.reply_text("죄송합니다. 해당 명령어는 관리자만 수행할 수 있습니다.\n"
                                  "Sorry. This command can only be executed by the administrator.")

def restart(bot, update, isAdmin):
    if isAdmin:
        rcon = mcrcon.MCRcon()
        rcon.connect(config['RCON']['server_ip'], int(config['RCON']['server_port']), config['RCON']['server_password'])
        
        update.message.reply_text("해당 명령어를 실행중입니다...\n"
                                  "Running this command...")

        response = rcon.command("restart")
        while True:
            if response:
                update.message.reply_text("성공적으로 실행되었습니다.\n"
                                          "Successfully executed.")
                break

        rcon.disconnect()
    else:
        update.message.reply_text("죄송합니다. 해당 명령어는 관리자만 수행할 수 있습니다.\n"
                                  "Sorry. This command can only be executed by the administrator.")

# -----------------------------------------------------
#   Command Handler
# -----------------------------------------------------

dispatcher.add_handler(CommandHandler('start', start)) ## /start Command - Start CityArts Bot
dispatcher.add_handler(CommandHandler('stop', stop)) ## /stop Command - Stop CityArts Bot
dispatcher.add_handler(CommandHandler('help', help)) ## /help Command - Show help
dispatcher.add_handler(CommandHandler('map', map)) ## /map Command - Show map
dispatcher.add_handler(CommandHandler('trains', trains)) ## /trains Command - Show Railway route map
dispatcher.add_handler(CommandHandler('status', status)) ## /status Command - Get server status
dispatcher.add_handler(CommandHandler('server', status)) ## /server Command (Redirect to /status)
dispatcher.add_handler(CommandHandler('report', report)) ## /report Command - Report a server problem to IPA
dispatcher.add_handler(CommandHandler('wiki', wiki)) ## /wiki Command - Browse the documentation on the wiki
dispatcher.add_handler(CommandHandler('add', add)) ## /add Command - Whitelist assistant
dispatcher.add_handler(MessageHandler([Filters.text], text)) ## Administer only commands
dispatcher.add_handler(MessageHandler([Filters.status_update.new_chat_members], welcome)) ## Show welcome message

updater.start_polling()
updater.idle()
