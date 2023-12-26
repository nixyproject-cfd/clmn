import re
import os
import sys
import json
import html
import base64
import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from json.decoder import JSONDecodeError
from random import randint, choice, uniform
from colorama import Fore, Back, Style, init
from requests.exceptions import RequestException, ConnectionError, Timeout
from http.cookies import SimpleCookie

s = requests.Session()

init(autoreset=True)

sc_ver = "FAUCET EARNER v3"
host = 'faucetearner.org'

end = "\033[K"
res = Style.RESET_ALL
red = Style.BRIGHT+Fore.RED
bg_red = Back.RED
white = Style.BRIGHT+Fore.WHITE
green = Style.BRIGHT+Fore.GREEN
yellow = Style.BRIGHT+Fore.YELLOW
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

def clean_screen():
    os.system("clear" if os.name == "posix" else "cls")

class Bot:
    
    def __init__(self):
        self.best_claim = 0
        self.streak = 0

    def curl(self, method, url, data=None):
        headers = {'user-agent': self.user_agent}
        while True:
            try:
                r = s.request(method, url, headers=headers, data=data, timeout=10)
                if r.status_code == 200:
                    return r
                elif r.status_code == 403:
                    self.carousel_msg("Access denied")
                    return None
                elif 500 <= r.status_code < 600:
                    self.carousel_msg(f"Server {host} down.")
                else:
                    self.carousel_msg(f"Unexpected response code: {r.status_code}")
                    return None
            except ConnectionError:
                self.carousel_msg(f"Reconnecting to {host}")
            except Timeout:
                self.carousel_msg("Too many requests")
            self.wait(10)

    def wait(self, x):
        for i in range(x, -1, -1):
            col = yellow if i%2 == 0 else white
            animation = "⫸" if i%2 == 0 else "⫸⫸"
            m, s = divmod(i, 60)
            t = f"[00:{m:02}:{s:02}]"
            sys.stdout.write(f"\r  {white}Please wait {col}{t} {animation}{res}{end}\r")
            sys.stdout.flush()
            sleep(1)

    def carousel_msg(self, message):
        def first_part(message, wait):
            animated_message = message.center(48)
            msg_effect = ""
            for i in range(len(animated_message) - 1):
                msg_effect += animated_message[i]
                sys.stdout.write(f"\r {msg_effect}{res} {end}")
                sys.stdout.flush()
                sleep(0.03)
            if wait:
                sleep(1)

        msg_effect = message[:47]
        wait = True if len(message) <= 47 else False
        first_part(msg_effect, wait)
        if len(message) > 47:
            for i in range(50, len(message)):
                msg_effect = msg_effect[1:] + message[i]
                if i > 1:
                    sys.stdout.write(f"\r {msg_effect} {res}{end}")
                    sys.stdout.flush()
                sleep(0.1)
        sleep(1)
        sys.stdout.write(f"\r{res}{end}\r")
        sys.stdout.flush()

    def msg_line(self):
        print(f"{green}{'━' * 50}")

    def msg_action(self, action):
        now = datetime.now()
        now = now.strftime("%d/%b/%Y %H:%M:%S")
        total_length = len(action) + len(now) + 5
        space_count = 50 - total_length
        msg = f"[{action.upper()}] {now}{' ' * space_count}"
        print(f"{bg_red} {white}{msg}{res}{red}⫸{res}{end}")

    def claim(self):
        def claim_faucet():
            self.carousel_msg("Go to faucet section")
            while True:
                r =  self.curl('POST', f"https://{host}/api.php?act=faucet")
                if r:
                    r = json.loads(r.text)
                    if r['message']:
                        v = self.data_account()
                        match = re.search(r'(\d+\.\d+) XRP', r['message'])
                        if match:
                            earn = match.group(1)
                        else:
                            earn = 0
                        earn = "{:.8f}".format(float(earn))
                        if float(earn) > self.best_claim:
                            self.streak = 1
                            self.best_claim = float(earn)
                        elif float(earn) == self.best_claim:
                            self.streak += 1
                        best_claim = "{:.8f}".format(self.best_claim)
                        self.msg_action("FAUCET")
                        print(f" {red}# {white}Reward: {green}{earn}{res} XRP{end}")
                        print(f" {red}# {white}Balance: {green}{v['total_bal']}{res} XRP{end}")
                        print(f" {red}# {white}Highest Reward: {green}{best_claim}    -    {white}Streak: {yellow}{self.streak}{res}{end}")
                        self.msg_line()
                    return
                        
        v = self.data_account()
        print(f"\n{bg_red}{white} ๏ {res} {yellow}〔 USERNAME 〕............: {res}{v['username']}{end}")
        print(f"{bg_red}{white} ๏ {res} {yellow}〔 TOTAL BALANCE 〕.......: {res}{v['total_bal']} XRP{end}")
        print(f"{bg_red}{white} ๏ {res} {yellow}〔 FAUCET EARNINGS 〕.....: {res}{v['faucet_earn']} XRP{end}")
        print(f"{bg_red}{white} ๏ {res} {yellow}〔 PTC EARNINGS 〕........: {res}{v['ptc_earn']} XRP {end}")
        print(f"{bg_red}{white} ๏ {res} {yellow}〔 INVESTMENT EARNINGS 〕.: {res}{v['invest_earn']} XRP {end}")
        print(f"{bg_red}{white} ๏ {res} {yellow}〔 REFFERALS EARNINGS〕...: {res}{v['reff_earn']} XRP{end}")
        print(f"{res}{end}")
        self.msg_line()
        
        while True:
            sleep(2)
            self.wait(10 * 60)
            claim_faucet()

    def write_file(self, data):
        with open('config.json', 'w') as f:
            json.dump(data, f, indent=4)

    def data_account(self):
        self.carousel_msg("Getting user info")
        while True:
            url = f"https://{host}/dashboard.php"
            r = self.curl('GET', url)
            v = {}
            soup = BeautifulSoup(r.text, 'html.parser')
            username = soup.find('p', {'style': 'max-width: 130px;overflow: hidden;text-wrap: nowrap;text-overflow: ellipsis;'})
            v['username'] = username.text.strip() if username else None
    
            keywords = {
                'total_bal': 'Total Balance:',
                'faucet_earn': 'Faucet Earnings:',
                'ptc_earn': 'PTC Earnings:',
                'invest_earn': 'Investment Earnings:',
                'reff_earn': 'Referrals Earnings:'
            }
            
            for key, value in keywords.items():
                element = soup.find('div', string=lambda text: text and value in text).find_next('b', {'translate': 'no'})
                v[key] = element.text.split(' ')[0].strip() if element else None
                if v[key] is not None:
                    v[key] = "{:.8f}".format(float(v[key]))
    
            if any(value is None or len(value) < 5 for value in v.values()):
                continue
            else:
                break
        return v
            
    def config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
        except json.JSONDecodeError:
            print(f"{red}Check your config file")
            exit()

        keywords = ['Cookies', 'User-Agent']

        for key in keywords:
            while key not in config or len(config[key]) < 5:
                config[key] = input(f"\n{yellow}{key}{red}:{res} ")

        self.write_file(config)
        self.user_agent = config['User-Agent']
        
        cookies_str = config['Cookies']

        cookie_obj = SimpleCookie()
        cookie_obj.load(cookies_str)
        
        cookie_jar = requests.cookies.RequestsCookieJar()
        for morsel in cookie_obj.values():
            cookie_jar.set(morsel.key, morsel.value)
        
        s.cookies = cookie_jar


os.system("git pull")


bot = Bot()
bot.config()

clean_screen()
bot.msg_line()
print(f"{green}{sc_ver.center(50, ' ')}")
bot.msg_line()

bot.claim()
