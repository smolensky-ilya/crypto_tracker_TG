import requests
from json import JSONDecodeError
from time import sleep


class Parser:
    def __init__(self, config_obj, logging):
        self.config = config_obj
        self.token_ids = config_obj.TOKEN_IDS_TO_TRACK
        self.headers = {'Accept': 'application/json'}
        self.logging = logging
        self.logging.debug('Parser initialized!')

    def get_token_price_vs_currency(self, currency: str = 'usd'):
        attempt = 0
        while self.config.API_MAX_ATTEMPTS > attempt:
            try:
                result = requests.get(f'https://api.coingecko.com/api/v3/simple/price'
                                      f'?ids={",".join(self.token_ids + [self.config.USD_STABLE_ID_GECKO])}'
                                      f'&vs_currencies={currency},{self.config.LOCAL_CURRENCY}',
                                      headers=self.headers).json()
                if 'status' not in result:
                    return result
                else:
                    self.logging.warning(f'Gecko API was given {self.config.API_SLEEP_TIME} to rest.')
                    sleep(self.config.API_SLEEP_TIME)
            except (TimeoutError, JSONDecodeError, TypeError) as error:
                self.logging.warning(f"Smth is wrong with the Gecko API. I'll rest for {self.config.API_SLEEP_TIME}"
                                     f"sec. Attempt {attempt}/{self.config.API_MAX_ATTEMPTS}")
                attempt += 1
                sleep(self.config.API_SLEEP_TIME)
                if self.config.API_MAX_ATTEMPTS < attempt:
                    raise Exception(f'Smth went wrong in Gecko API: {error}')

    def get_eth_token_balance(self):
        res_dict, attempt = dict(), 0
        while self.config.API_MAX_ATTEMPTS > attempt:
            try:
                for token_name, contract_address in self.config.ETH_TOKEN_CONTRACTS.items():
                    r = requests.get(f'https://api.etherscan.io/api?module=account&action=tokenbalance'
                                     f'&contractaddress={contract_address}&address={self.config.ETH_ADDRESS}&tag=latest'
                                     f'&apikey={self.config.ETHERSCAN_API_KEY}')
                    res_dict[token_name] = int(r.json()['result']) / (10 ** int(self.config.
                                                                                SPECIAL_DECIMALS.get(token_name, 18)))
                    res_dict['ethereum'] = self.get_coin_balances('ethereum')
                return res_dict
            except (TimeoutError, JSONDecodeError, TypeError) as error:
                self.logging.warning(f"Smth is wrong with the Etherscan API. I'll rest for {self.config.API_SLEEP_TIME}"
                                     f" sec. Attempt {attempt}/{self.config.API_MAX_ATTEMPTS}")
                attempt += 1
                sleep(self.config.API_SLEEP_TIME)
                if self.config.API_MAX_ATTEMPTS < attempt:
                    raise Exception(f'Smth went wrong in Etherscan API: {error}')

    def get_avalanche_token_balance(self):
        res_dict, attempt = dict(), 0
        while self.config.API_MAX_ATTEMPTS > attempt:
            try:
                for token_name, contract_address in self.config.AVALANCHE_TOKEN_CONTRACTS.items():
                    r = requests.get(f'https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api?'
                                     f'module=account&action=tokenbalance&contractaddress={contract_address}'
                                     f'&address={self.config.AVALANCHE_ADDRESS}&tag=latest')
                    res_dict[token_name] = int(r.json()['result']) / (10 ** int(self.config.
                                                                                SPECIAL_DECIMALS.get(token_name, 18)))
                    res_dict['avalanche-2'] = self.get_coin_balances('avalanche-2')
                return res_dict
            except (TimeoutError, JSONDecodeError, TypeError) as error:
                self.logging.warning(f"Smth is wrong with the Avalanche API. I'll rest for {self.config.API_SLEEP_TIME}"
                                     f" sec. Attempt {attempt}/{self.config.API_MAX_ATTEMPTS}")
                attempt += 1
                sleep(self.config.API_SLEEP_TIME)
                if self.config.API_MAX_ATTEMPTS < attempt:
                    raise Exception(f'Smth went wrong in Avalanche API: {error}')

    def get_bsc_token_balance(self):
        res_dict, attempt = dict(), 0
        while self.config.API_MAX_ATTEMPTS > attempt:
            try:
                for token_name, contract_address in self.config.BINANCE_TOKEN_CONTRACTS.items():
                    r = requests.get(f'https://api.bscscan.com/api?module=account&action=tokenbalance'
                                     f'&contractaddress={contract_address}'
                                     f'&address={self.config.BINANCE_ADDRESS}&tag=latest'
                                     f'&apikey={self.config.BSC_SCAN_API_KEY}')
                    res_dict[token_name] = int(r.json()['result']) / (10 ** int(self.config.
                                                                                SPECIAL_DECIMALS.get(token_name, 18)))
                    res_dict['binancecoin'] = self.get_coin_balances('binancecoin')
                return res_dict
            except (TimeoutError, JSONDecodeError, TypeError) as error:
                self.logging.warning(f"Smth is wrong with the BSC API. I'll rest for {self.config.API_SLEEP_TIME}"
                                     f" sec. Attempt {attempt}/{self.config.API_MAX_ATTEMPTS}")
                attempt += 1
                sleep(self.config.API_SLEEP_TIME)
                if self.config.API_MAX_ATTEMPTS < attempt:
                    raise Exception(f'Smth went wrong in Avalanche API: {error}')

    def get_coin_balances(self, coin: str):
        attempt = 0
        while self.config.API_MAX_ATTEMPTS > attempt:
            try:
                if coin == 'avalanche-2':
                    r = requests.get(f'https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api?'
                                     f'module=account&action=balance'
                                     f'&address={self.config.AVALANCHE_ADDRESS}&tag=latest')
                elif coin == 'ethereum':
                    r = requests.get(f'https://api.etherscan.io/api?module=account&action=balance'
                                     f'&address={self.config.ETH_ADDRESS}&tag=latest&apikey='
                                     f'{self.config.ETHERSCAN_API_KEY}')
                elif coin == 'binancecoin':
                    r = requests.get(f'https://api.bscscan.com/api?module=account&action=balance'
                                     f'&address={self.config.BINANCE_ADDRESS}&tag=latest&apikey='
                                     f'{self.config.BSC_SCAN_API_KEY}')
                else:
                    return None
                return int(r.json()['result']) / (10 ** 18)
            except (TimeoutError, JSONDecodeError, TypeError) as error:
                self.logging.warning(f"Smth is wrong with coin balance APIs. I'll rest for {self.config.API_SLEEP_TIME}"
                                     f" sec. Attempt {attempt}/{self.config.API_MAX_ATTEMPTS}")
                attempt += 1
                sleep(self.config.API_SLEEP_TIME)
                if self.config.API_MAX_ATTEMPTS < attempt:
                    raise Exception(f'Smth went wrong in Avalanche or Etherscan API: {error}')

    def get_data_combined(self):
        data = dict()
        gecko_api = self.get_token_price_vs_currency()
        self.logging.debug('Parsed from Gecko')
        data['token_vs_usd'] = {token: prices['usd'] for token, prices in gecko_api.items()
                                if token != self.config.USD_STABLE_ID_GECKO}
        data[f'token_vs_{self.config.LOCAL_CURRENCY}'] = {token: prices[self.config.LOCAL_CURRENCY] for
                                                          token, prices in gecko_api.items()
                                                          if token != self.config.USD_STABLE_ID_GECKO}
        data[f'usdt_vs_{self.config.LOCAL_CURRENCY}'] = gecko_api[self.config.USD_STABLE_ID_GECKO][self.config.
                                                                                                   LOCAL_CURRENCY]
        eth_tokens = self.get_eth_token_balance() if len(self.config.ETH_TOKEN_CONTRACTS.keys()) > 0 else None
        self.logging.debug(f'Parsed ETH tokens')
        avalanche_tokens = self.get_avalanche_token_balance() \
            if len(self.config.AVALANCHE_TOKEN_CONTRACTS.keys()) > 0 else None
        self.logging.debug(f'Parsed AVALANCHE tokens')
        binance_tokens = self.get_bsc_token_balance() if len(self.config.BINANCE_TOKEN_CONTRACTS.keys()) > 0 else None
        self.logging.debug(f'Parsed BINANCE tokens')
        data['owned'] = eth_tokens | avalanche_tokens | binance_tokens
        return data


def main():
    pass


if __name__ == "__main__":
    main()
