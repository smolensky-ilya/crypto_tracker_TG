from data_storage import Investments
from telebot import TeleBot
import requests


class TgBot:
    def __init__(self, config_obj, logging):
        self.config = config_obj
        self.logging = logging
        self.TG_token = self.config.TG_BOT_TOKEN[0]
        self.bot = TeleBot(self.TG_token)
        self.chat_ids_to_notify: list = self.config.TG_USER_IDS
        if self.config.TG_USER_IDS[0] != '***PASTE YOURS***':
            self.send_alert('I am up!')
        self.check_messages()

    def send_alert(self, message: str):
        for each in self.chat_ids_to_notify:
            self.bot.send_message(each, message, parse_mode='HTML')

    def check_messages(self, last_notification: str = 'notification!'):
        response = requests.get(url := f'https://api.telegram.org/bot{self.TG_token}/getUpdates').json()
        if response['ok'] and response['result']:
            self.logging.info(f"Got {len(response['result'])} new message(s).")
            for mes in response['result']:
                self.logging.info(f"Message: {mes}")
                if str(chat_id := mes['message']['from']['id']) not in self.chat_ids_to_notify:
                    reply = f"You aren't registered. \nYour TG ID is {chat_id}"
                    self.bot.send_message(chat_id, reply, parse_mode='HTML')
                else:
                    self.send_alert(last_notification)
            # Acknowledge updates by setting offset to highest_update_id + 1
            requests.get(url, params={'offset': max(update['update_id'] for update in response['result']) + 1})

    def notification(self, token: str, update: dict, prev_price: float, apr: float):
        # INITIALIZING INVESTMENTS CHECKER
        inv = Investments(self.config, logging=self.logging)
        # IN CASE IT'S IN SCIENTIFIC NOTATION
        price = "{:,.10f}".format(update[f'token_vs_usd'][token]).rstrip('0').rstrip('.') \
            if 'e' in str(update[f'token_vs_usd'][token]).lower() else f"{update[f'token_vs_usd'][token]:,}"
        # VARIOUS STUFF
        price_difference = round(((update[f'token_vs_usd'][token] - prev_price) / prev_price * 100), 2)
        total_in_usd = round(update[f'token_vs_usd'][token] * update['owned'].get(token, 0), 2)
        total_in_local = \
            round(update[f'token_vs_{self.config.LOCAL_CURRENCY}'][token] * update['owned'].get(token, 0), 2)
        # THE MESSAGE ITSELF
        mes = f"<b>{token.upper()}</b>: <u>{price_difference:,}%</u> // ${price} // " \
              f"{update[f'token_vs_{self.config.LOCAL_CURRENCY}'][token]:,} {self.config.LOCAL_CURRENCY.upper()} \n" \
              f"<b>PnL</b>: <u>{inv.count_pnl(token, total_in_usd)}%</u> // " \
              f"<u>{inv.count_pnl(token, total_in_local, self.config.LOCAL_CURRENCY)}%</u>\n" \
              f"<b>Total</b>: ${total_in_usd:,} // {total_in_local:,} {self.config.LOCAL_CURRENCY.upper()}\n" \
              f"<b>Invested</b>: ${inv.get_inv(token)} // {inv.get_inv(token, self.config.LOCAL_CURRENCY)}" \
              f" {self.config.LOCAL_CURRENCY.upper()}\n" \
              f"<b>Bal</b>: {update['owned'].get(token, 'IDK?')}\n" \
              f"<b>USD</b>: {update[f'usdt_vs_{self.config.LOCAL_CURRENCY}']:,} {self.config.LOCAL_CURRENCY.upper()}\n"\
              f"<b>APR</b>: {apr}%"
        self.send_alert(mes)


def main():
    pass


if __name__ == "__main__":
    main()
