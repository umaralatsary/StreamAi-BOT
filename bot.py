from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from base64 import b64encode
from urllib.parse import quote
from datetime import datetime
from colorama import *
import asyncio, random, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MinionLab:
    def __init__(self) -> None:
        self.headers = {
            "Accept-encoding": "gzip, deflate, br, zstd",
            "Accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-control": "no-cache",
            "Connection": "Upgrade",
            "Host": "gw0.streamapp365.com",
            "Origin": "chrome-extension://fgamijdhamopilihagheoalbifagafka",
            "Pragma": "no-cache",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": "KBUtPHAWNI9Dz/dhkLUiOw==",
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Minion Lab - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_edge_id(self):
        hex_chars = '0123456789abcdef'
        edge_id = ''.join(random.choice(hex_chars) for _ in range(32))
        return edge_id
    
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def handle_tasks(self, url, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                async with session.get(url=url, headers={}) as response:
                    if response.status == 200:
                        result = await response.text()
                        return result, response.status
        except (Exception, ClientResponseError) as e:
            return None, None
        
    async def connect_websocket(self, user_id, edge_id: str, use_proxy: bool, proxy=None):
        wss_url = "wss://gw0.streamapp365.com/connect"
        connected = False
        send_ping = None

        while True:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=120))
            try:
                async with session:
                    async with session.ws_connect(wss_url, headers=self.headers) as wss:

                        async def send_ping_message():
                            while True:
                                await wss.send_json({"type":"ping"})
                                self.print_message(user_id, proxy, Fore.WHITE, 
                                    f"Edge ID {self.mask_account(edge_id)}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}PING Success{Style.RESET_ALL}"
                                )
                                await asyncio.sleep(20)

                        if not connected:
                            await wss.send_json({"type":"register", "user":user_id, "dev":edge_id})
                            self.print_message(user_id, proxy, Fore.WHITE, 
                                f"Edge ID {self.mask_account(edge_id)}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Webscoket Is Connected{Style.RESET_ALL}"
                            )
                            connected = True

                        if connected:
                            try:
                                async for msg in wss:
                                    if msg.data == "pong":
                                        self.print_message(user_id, proxy, Fore.WHITE, 
                                            f"Edge ID {self.mask_account(edge_id)}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.BLUE + Style.BRIGHT}PONG Received{Style.RESET_ALL}"
                                        )
                                    else:
                                        response = json.loads(msg.data)
                                        if response.get("type") == "request":
                                            task_id = response.get("taskid")
                                            url = response.get("data", {}).get("url")
                                            data, status_code = await self.handle_tasks(url, proxy)
                                            if data and status_code:
                                                task_data = {
                                                    "type":"response",
                                                    "taskid":task_id,
                                                    "result":{
                                                        "parsed":"",
                                                        "html":b64encode((quote(data)).encode('utf-8')).decode('utf-8'),
                                                        "rawStatus":status_code
                                                    }
                                                }
                                                await wss.send_json(task_data)
                                                self.print_message(user_id, proxy, Fore.WHITE, 
                                                    f"Edge ID {self.mask_account(edge_id)}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                                    f"{Fore.GREEN + Style.BRIGHT}Create Connection Success{Style.RESET_ALL}"
                                                )
                                                if not send_ping:
                                                    send_ping = asyncio.create_task(send_ping_message())

                                            else:
                                                self.print_message(user_id, proxy, Fore.WHITE, 
                                                    f"Edge ID {self.mask_account(edge_id)}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                                    f"{Fore.RED + Style.BRIGHT}Create Connection Failed{Style.RESET_ALL}"
                                                )
                                                connected = False
                                                break

                                        elif response.get("type") == "cancel":
                                            await wss.send_json({"type":"register", "user":user_id, "dev":edge_id})
                                            self.print_message(user_id, proxy, Fore.WHITE, 
                                                f"Edge ID {self.mask_account(edge_id)}"
                                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                                f"{Fore.YELLOW + Style.BRIGHT}Connection Cancelled{Style.RESET_ALL}"
                                            )
                                            connected = False
                                            break

                            except Exception as e:
                                self.print_message(user_id, proxy, Fore.WHITE, 
                                    f"Edge ID {self.mask_account(edge_id)} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT} Websocket Connection Closed: {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                                )
                                if send_ping:
                                    send_ping.cancel()
                                    try:
                                        await send_ping
                                    except asyncio.CancelledError:
                                        self.print_message(user_id, proxy, Fore.WHITE, 
                                            f"Edge ID {self.mask_account(edge_id)}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.YELLOW + Style.BRIGHT}Send Ping Cancelled{Style.RESET_ALL}"
                                        )

                                connected = False

            except Exception as e:
                self.print_message(user_id, proxy, Fore.WHITE, 
                    f"Edge ID {self.mask_account(edge_id)} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Websocket Not Connected: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                # proxy = self.rotate_proxy_for_account(user_id) if use_proxy else None
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.print_message(user_id, proxy, Fore.WHITE, 
                    f"Edge ID {self.mask_account(edge_id)}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()

    async def process_accounts(self, user_id: str, proxy_count: int, use_proxy: bool):
        proxy = None
        tasks = []

        if use_proxy:
            max_connections = 20 # U Can Change it
            connections_to_create = min(proxy_count, max_connections)

            for i in range(connections_to_create):
                proxy_count -= 1
                edge_id = self.generate_edge_id()
                proxy = self.rotate_proxy_for_account(user_id)
                tasks.append(self.connect_websocket(user_id, edge_id, use_proxy, proxy))

        else:
            edge_id = self.generate_edge_id()
            tasks.append(self.connect_websocket(user_id, edge_id, use_proxy, proxy))

        await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('userids.txt', 'r') as file:
                user_ids = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(user_ids)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                proxy_count = len(self.proxies)
                for user_id in user_ids:
                    user_id = user_id.strip()
                    if user_id:
                        tasks.append(self.process_accounts(user_id, proxy_count, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'userids.txt' tidak ditemukan.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = MinionLab()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Minion Lab - BOT{Style.RESET_ALL}                                       "                              
        )