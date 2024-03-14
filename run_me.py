from parsing import Parser
from data_storage import Storage
from TG import TgBot
from config import Config
from time import sleep
import logging


def main():
    # INITIALIZE CONFIG AND LOGGING
    config = Config()
    logging.basicConfig(level=getattr(logging, config.LOGGING_LEVEL.upper(), logging.INFO),
                        format='%(asctime)s: %(message)s')
    # CHECKING IF THE CONFIG OF TG IS VALID
    if not config.valid_tg:
        while True:
            logging.critical("Please configure the TG bot API!")
            sleep(10)
    # INITIALIZE THE TG BOT
    tg = TgBot(config_obj=config, logging=logging)
    # CHECKING IF THE CONFIG
    if not config.valid_config:
        while True:
            logging.critical("Have you finished setting up CONFIG.INI? It seems you haven't. You bot is running so "
                             "you can text it to get your USER ID. Rerun the app after you are done configuring it.")
            tg.check_messages()
            sleep(10)
    # INITIALIZE THE PARSER
    parser = Parser(config_obj=config, logging=logging)
    # INITIALIZE STORAGES
    token_storage = dict()
    for token in config.TOKEN_IDS_TO_TRACK:
        token_storage[token] = Storage(config_obj=config, token=token, logging=logging)
    # PRICE TRACKING INITIATION
    prev_price: dict = dict()

    while True:
        # DO THE PARSING THING
        logging.info(f"Checking markets and balances. I'll do that every {config.UPDATE_INTERVAL/60} minutes.")
        update = parser.get_data_combined()
        logging.debug(update)
        # PROCESSING AND SAVING THE UPDATED DATA
        for token, storage in token_storage.items():
            # COMPARE WITH THE LAST PRICE
            new_price = update[f'token_vs_usd'][token]
            prev_price[token] = prev_price.get(token, storage.data.tail(1)[f'{token}_vs_usdt'].values[0]
                                               if len(storage.data) > 0 else new_price)
            threshold = prev_price[token] * config.PERCENTAGE_CHANGE_NOTIFY
            # NOTIFY IF NEEDED
            if new_price > (prev_price[token] + threshold) or new_price < (prev_price[token] - threshold):
                tg.notification(token=token, update=update, prev_price=prev_price[token], apr=storage.get_arp())
                logging.info(f"Oops! {token} price is now {new_price}. Notified everybody.")
                prev_price[token] = new_price
            # SAVING
            storage.add_info(update)
        sleep(config.UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
