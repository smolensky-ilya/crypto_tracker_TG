import configparser
from typing import Any
import os
import textwrap


class Config:
    def __getattr__(self, item) -> Any:
        return super().__getattr__(item)

    def __init__(self, config_file_name='config.ini'):
        self.config_file_name = config_file_name
        if not os.path.exists(config_file_name):
            self.create_default_config()

        config = configparser.ConfigParser()
        config.read(config_file_name)
        self.parse_config(config)
        self.valid_tg = False if self.__dict__['TG_BOT_TOKEN'] == ["***PASTE YOURS***"] else True
        self.valid_config = True if self.__dict__['ETHERSCAN_API_KEY'] != "***PASTE YOURS***" or \
            self.__dict__['BSC_SCAN_API_KEY'] != "***PASTE YOURS***" or \
            self.__dict__['TG_USER_IDS'][0] != "***PASTE YOURS***" else False

    def create_default_config(self):
        config_content = textwrap.dedent("""\
        # API settings
        [API_SETTINGS]
        # These APIs are free. All you need to do is register there.
        ETHERSCAN_API_KEY = ***PASTE YOURS***
        BSC_SCAN_API_KEY = ***PASTE YOURS***
        # USE BOT FATHER ON TELEGRAM TO GET ONE
        TG_BOT_TOKEN = ***PASTE YOURS***
        # SEVERAL IDs are possible, separated by a comma
        # You can find it out by texting your bot after you insert TG_BOT_TOKEN above and run the app***
        TG_USER_IDS = ***PASTE YOURS***
        # SECONDS
        API_SLEEP_TIME = 30
        API_MAX_ATTEMPTS = 10
        USD_STABLE_ID_GECKO = tether
        LOCAL_CURRENCY = rub

        [Addresses]
        ETH_ADDRESS = ***PASTE YOURS***
        AVALANCHE_ADDRESS = ***PASTE YOURS***
        BINANCE_ADDRESS = ***PASTE YOURS***

        # Tracking settings
        [TRACKING_SETTINGS]
        # API ID FROM GECKO
        TOKEN_IDS_TO_TRACK = ethereum,staked-ether,kimbo,coq-inu,avalanche-2,wrapped-bitcoin,binancecoin,the-goat-cz
        # SECONDS
        UPDATE_INTERVAL = 600
        # 0.5%
        PERCENTAGE_CHANGE_NOTIFY = 0.000005
        ETH_TOKEN_CONTRACTS = staked-ether:0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84,wrapped-bitcoin:0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599
        AVALANCHE_TOKEN_CONTRACTS = kimbo:0x184ff13B3EBCB25Be44e860163A5D8391Dd568c1,coq-inu:0x420FcA0121DC28039145009570975747295f2329
        BINANCE_TOKEN_CONTRACTS = the-goat-cz:0xa2C17A6Fd0aFE27afa2630A7528bC673089E6b8d
        SPECIAL_DECIMALS = wrapped-bitcoin:8,the-goat-cz:9

        [MISC]
        DATA_DIRECTORY = data
        INVESTMENTS_FILE_NAME = investments.csv
        NON_APPLICABLE_SIGN = *NA*
        # DEBUG, INFO, WARNING, ERROR, CRITICAL
        LOGGING_LEVEL = INFO
        """)
        with open(self.config_file_name, 'w') as config_file:
            config_file.write(config_content.strip())

    def parse_config(self, config):
        assign_as_tuples = []
        assign_as_lists = ['TG_USER_IDS', 'TG_BOT_TOKEN']
        for section in config.sections():
            for key, value in config.items(section):
                # Check if the value contains ':' indicating a dict
                if key.upper() in assign_as_lists:
                    value = [v.strip() for v in value.split(',')]
                elif key.upper() in assign_as_tuples:
                    value = tuple(value.split(','))
                else:
                    if ':' in value:
                        value_dict = {}
                        for item in value.split(','):
                            k, v = item.split(':')
                            value_dict[k.strip()] = v.strip()
                        value = value_dict
                    elif ',' in value:
                        # It's a list if explicitly mentioned or by default if ',' present and not a dict
                        value = [v.strip() for v in value.split(',')]
                    elif key.upper() in assign_as_tuples:
                        # Assign as tuple if explicitly mentioned
                        value = tuple(value.split(','))
                    else:
                        # Handle single value cases (int, float, string)
                        if value.isdigit():
                            value = int(value)
                        elif self.is_float(value):
                            value = float(value)
                # Assign dynamically
                setattr(self, key.upper(), value)

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False


def main():
    pass


if __name__ == '__main__':
    main()
