import pandas as pd
from os import path, makedirs
from datetime import datetime, timedelta


class Storage:
    def __init__(self, config_obj, token: str, logging):
        self.config = config_obj
        self.logging = logging
        self.token = token
        self.file_path = f'{self.config.DATA_DIRECTORY}//{self.token}.csv'
        self.data = self.open_data()
        self.logging.debug(f'Storage for {self.token.upper()} initialized!')

    def open_data(self):
        try:
            return pd.read_csv(self.file_path)
        except FileNotFoundError:
            if not path.exists(self.config.DATA_DIRECTORY):
                makedirs(self.config.DATA_DIRECTORY)
            pd.DataFrame().to_csv(self.file_path)
            self.logging.warning(f"The file for {self.token} was successfully created.")
            return pd.DataFrame()

    def save_data(self):
        self.data.to_csv(self.file_path, index=False)

    def add_info(self, update: dict):
        data = {'date_': [datetime.now()],
                'owned_amount': [update['owned'].get(self.token, 0)],
                f'usdt_vs_{self.config.LOCAL_CURRENCY}': [update[f'usdt_vs_{self.config.LOCAL_CURRENCY}']],
                f'{self.token}_vs_usdt': [update[f'token_vs_usd'][self.token]],
                f'{self.token}_vs_{self.config.LOCAL_CURRENCY}':
                    [update[f'token_vs_{self.config.LOCAL_CURRENCY}'][self.token]],
                'total_in_usdt': [update[f'token_vs_usd'][self.token] * update['owned'].get(self.token, 0)],
                f'total_in_{self.config.LOCAL_CURRENCY}':
                    [update[f'token_vs_{self.config.LOCAL_CURRENCY}'][self.token] * update['owned'].get(self.token, 0)]}
        self.data = pd.concat([self.data, pd.DataFrame(data)])
        self.logging.debug(f'New row of {self.token.upper()} saved!')
        self.save_data()

    def get_arp(self):
        try:
            d = self.data.copy()
            d['date_'] = pd.to_datetime(d['date_'])
            prev_start = min(d[d['date_'].dt.date == datetime.now().date() - timedelta(days=1)]['owned_amount'])
            today_start = min(d[d['date_'].dt.date == datetime.now().date()]['owned_amount'])
            today_end = max(d[d['date_'].dt.date == datetime.now().date()]['owned_amount'])
            return f"{round((today_start/prev_start-1)*365*100, 2):,}" if today_start == today_end \
                else f"{round((today_end / today_start - 1) * 365 * 100, 2):,}"
        except (ValueError, ZeroDivisionError):
            return self.config.NON_APPLICABLE_SIGN


class Investments:
    def __init__(self, config_obj, logging):
        self.config = config_obj
        self.logging = logging
        self.filename: str = self.config.INVESTMENTS_FILE_NAME
        self.investment_sums = self.get_info()

    def get_info(self):
        try:
            return pd.read_csv(self.filename).dropna(subset=['token']).groupby('token')[['rub', 'usd']].sum() \
                                             .to_dict(orient='index')
        except FileNotFoundError:
            pd.DataFrame({'token': [], 'date_': [], f'{self.config.LOCAL_CURRENCY}': [], 'usd': [], 'open': []}).\
                to_csv(self.config.INVESTMENTS_FILE_NAME, index=False)
            self.logging.warning(f"Investments file was successfully created.")
            return pd.DataFrame()

    def count_pnl(self, token, new_total, currency: str = 'usd'):
        try:
            return f"{round(new_total / self.investment_sums[token][currency] * 100 - 100, 2):,}"
        except (ZeroDivisionError, KeyError):
            return self.config.NON_APPLICABLE_SIGN

    def get_inv(self, token, currency: str = 'usd'):
        try:
            return f"{self.investment_sums[token][currency]:,}"
        except KeyError:
            return self.config.NON_APPLICABLE_SIGN


def main():
    pass


if __name__ == "__main__":
    main()
