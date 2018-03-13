const read = require('read-yaml');
const rp = require('request-promise');
const parseJson = require('parse-json');
import TelegramBot from 'node-telegram-bot-api';

let config: any = read.sync('bot.yml');
let commands: any = read.sync('commands.yml');
const token: string = config['telegram']['token'];
const username: string = config['telegram']['username'];
const server_address: string = config['server']['server_address'];
const wiki_address: string = config['server']['wiki_address'];
const admins: Array<number> = config['telegram']['admin_id'];
const report_group_id: number = config['telegram']['group_id']['report_group_id'];
const request_group_id: number = config['telegram']['group_id']['request_group_id'];
const bot: any = new TelegramBot(token, {polling: true});

class Bot {
    public static main(): number {
        bot.onText(/\/(start|stop|help)(|@cityarts_bot)/, (msg: any, match: any) => {
            const chatId: number = msg.chat.id;
            let command: string = match[0].split(/@| /)[0];
            let reply: string = commands['commands'][command];
          
            bot.sendMessage(chatId, reply, {parse_mode : "HTML"});
        });

        bot.onText(/\/(map|trains)(|@cityarts_bot)/, (msg: any, match: any) => {
            const chatId: number = msg.chat.id;
            let command: string = match[0].split(/@| /)[0];
            let reply: string = commands['commands'][command];
            let photo: string = config['resources'][`${command}_path`];

            bot.sendPhoto(chatId, photo, {caption: reply, parse_mode : "HTML"});
        });

        bot.onText(/\/(report|request)(|@cityarts_bot)(.+)/, (msg: any, match: any) => {
            const chatId: number = msg.chat.id;
            let resp: string = match[3];
            let command: string = match[0].split(/@| /)[0];
            const target_group_id: number = this.checkReportCommand(command);
            let reply = undefined;
            let report_msg = undefined;

            if (resp == "" || resp == `@${username}`) {
                reply = commands['commands'][`${command}_no_match`];
            } else {
                reply = commands['commands'][command];
                report_msg = commands['commands'][`${command}_group`]
                    .replace(/msg.from.first_name/g, msg.from.first_name)
                    .replace(/msg.from.username/g, msg.from.username)
                    .replace(/resp/g, resp);

                bot.sendMessage(target_group_id, report_msg, {parse_mode : "HTML"});
            }
          
            bot.sendMessage(chatId, reply, {parse_mode : "HTML"});
        });

        bot.onText(/\/(status|server)(|@cityarts_bot)/, (msg: any, match: any) => {
            const chatId: number = msg.chat.id;
            let command: string = match[0].split(/@| /)[0];
            let reply: any = undefined;

            rp(`https://mcapi.us/server/status?ip=${server_address}`)
                .then(function (data: any) {
                    let json: any = parseJson(data);
                    let online: string = String(json['online'])
                        .replace(/true/g, "✅")
                        .replace(/false/g, "❎");
                    reply = commands['commands'][command]
                        .replace(/online/g, online)
                        .replace(/players_max/g, json['players']['max'])
                        .replace(/players_now/g, json['players']['now'])
                        .replace(/server_name/g, json['server']['name']);
                })
                .catch(function (err: any) {
                    reply = commands['commands']['err']
                                .replace(/err/g, err);
                })
                .finally(function () {
                    bot.sendMessage(chatId, reply, {parse_mode : "HTML"});
                });
        });

        bot.onText(/\/wiki(|@cityarts_bot)(.+)/, (msg: any, match: any) => {
            const chatId: number = msg.chat.id;
            let command: string = match[0].split(/@| /)[0];
            let search: string = match[2].split(/ /)[1];
            let reply: any = undefined;

            if (search == "") {
                reply = commands['commands'][`${command}_no_match`];
                bot.sendMessage(chatId, reply, {parse_mode : "HTML"});
            } else {
                // TODO: Fix 400 Error
                rp(`https://${wiki_address}/search/${search}`)
                .then(function (data: any) {
                    if (data.indexOf('문서가 없습니다.')) {
                        reply = commands['commands'][`${command}_no_find`]
                            .replace(/search/g, search);
                    } else {
                        reply = commands['commands'][command]
                            .replace(/link/g, `https://${wiki_address}/w/${search}`);
                    }
                })
                .catch(function (err: any) {
                    reply = commands['commands']['err']
                                .replace(/err/g, err);
                })
                .finally(function () {
                    bot.sendMessage(chatId, reply);
                });
            }
        });

        return 0;
    }

    static checkReportCommand(command: string): number {
        if (command == "/report") {
            return report_group_id;
        } else if (command == "/request") {
            return request_group_id;
        }

        return 0;
    }
}

Bot.main();
