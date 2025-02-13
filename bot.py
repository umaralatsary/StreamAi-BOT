from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from curl_cffi import requests
from base64 import b64encode
from urllib.parse import quote
from datetime import datetime
from colorama import *
import asyncio, random, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MinionLab:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json",
            "Accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-control": "no-cache",
            "Expires": "0",
            "Origin": "https://app.minionlab.ai",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://app.minionlab.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.edge_estabilished = 0
        self.total_edge = 0

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
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
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
        if "@" in account:
            local, domain = account.split("@", 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}{domain}"

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

    async def print_edge_ids_estabilished(self):
        while True:
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}{self.edge_estabilished}{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} of {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}{self.total_edge}{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Edge Ids Connection Estabilished... {Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(10)

    def print_question(self):
        while True:
            try:
                print("1. Use Exiting Edge Ids")
                print("2. Create New Edge Ids")
                connection_choice = int(input("Choose [1/2/3] -> ").strip())
                if connection_choice in [1, 2, 3]:
                    break
                else:
                    print(f"{Fore.RED+Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                proxy_choice = int(input("Choose [1/2/3] -> ").strip())

                if proxy_choice in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if proxy_choice == 1 else 
                        "Run With Private Proxy" if proxy_choice == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        nodes_count = 0
        if proxy_choice in [1, 2]:
            while True:
                try:
                    nodes_count = int(input("How Many Edge Ids Do You Want to Run For Each Account? -> ").strip())
                    if nodes_count > 0:
                        break
                    else:
                        print(f"{Fore.RED+Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        return nodes_count, proxy_choice, connection_choice

    async def handle_tasks(self, url, proxy=None, retries=5):
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url) as response:
                        if response.status == 200:
                            return await response.text()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
            
    async def user_login(self, email: str, password: str, proxy=None, retries=5):
        url = "https://api.minionlab.ai/web/v1/auth/emailLogin"
        data = json.dumps({"email":email, "code":"", "password":password, "referralCode":"zwYPzVWI"})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        try:
            response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="safari15_5")
            response.raise_for_status()
            result = response.json()
            return result['data']
        except Exception as e:
            return self.print_message(email, proxy, Fore.RED, f"Login Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
                  
    async def user_devices(self, email: str, token: str, proxy=None, retries=5):
        url = "https://api.minionlab.ai/web/v1/dashBoard/device/list"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")
                response.raise_for_status()
                result = response.json()
                return result['data']['rows']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET Device Lists Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
        
    async def connect_websocket(self, email: str, user_id: str, edge_id: str, use_proxy: bool):
        wss_url = "wss://gw0.streamapp365.com/connect"
        headers = {
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
        connected = False

        while True:
            proxy = self.get_next_proxy_for_account(edge_id) if use_proxy else None
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=60))
            try:
                async with session.ws_connect(wss_url, headers=headers) as wss:

                    async def send_ping_message():
                        while True:
                            await wss.send_json({"type":"ping"})
                            self.print_message(email, proxy, Fore.WHITE,
                                f"Edge ID {self.mask_account(edge_id)}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}PING Success{Style.RESET_ALL}"
                            )
                            await asyncio.sleep(20)

                    if not connected:
                        await wss.send_json({"type":"register", "user":user_id, "dev":edge_id})
                        self.print_message(email, proxy, Fore.WHITE,
                            f"Edge ID {self.mask_account(edge_id)}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                        )
                        self.edge_estabilished += 1
                        connected = True
                        send_ping = None
                        ready_to_ping = False

                    while connected:
                        if send_ping is None and ready_to_ping:
                            send_ping = asyncio.create_task(send_ping_message())

                        try:
                            response = await wss.receive_json()
                            if response.get("type") == "request":
                                url = response.get("data", {}).get("url")
                                task_id = response.get("taskid")
                                data = await self.handle_tasks(url, proxy)
                                if data:
                                    task_message = {
                                        "type":"response",
                                        "taskid":task_id,
                                        "result": {
                                            "parsed":"",
                                            "html":b64encode(quote(data).encode('utf-8')).decode('utf-8'),
                                            "rawStatus":200
                                        }
                                    }
                                    await wss.send_json(task_message)
                                    self.print_message(email, proxy, Fore.WHITE,
                                        f"Edge ID {self.mask_account(edge_id)}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.GREEN + Style.BRIGHT}Create Connection Success{Style.RESET_ALL}"
                                    )
                                    ready_to_ping = True
                                        
                                else:
                                    self.print_message(email, proxy, Fore.WHITE,
                                        f"Edge ID {self.mask_account(edge_id)}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Create Connection Failed{Style.RESET_ALL}"
                                    )

                            elif response.get("type") == "cancel":
                                self.print_message(email, proxy, Fore.WHITE,
                                    f"Edge ID {self.mask_account(edge_id)}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}Connection Cancelled{Style.RESET_ALL}"
                                )

                        except json.JSONDecodeError:
                            response = await wss.receive_str()
                            if response.strip() == "pong":
                                self.print_message(email, proxy, Fore.WHITE,
                                    f"Edge ID {self.mask_account(edge_id)}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.BLUE + Style.BRIGHT}PONG Received{Style.RESET_ALL}"
                                )
                        except Exception as e:
                            self.print_message(email, proxy, Fore.WHITE,
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
                                    self.print_message(email, proxy, Fore.WHITE, 
                                        f"Edge ID {self.mask_account(edge_id)}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Send Ping Cancelled{Style.RESET_ALL}"
                                    )

                            await asyncio.sleep(5)
                            self.edge_estabilished -= 1
                            connected = False
                            break

            except Exception as e:
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Edge ID {self.mask_account(edge_id)} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Websocket Not Connected: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Edge ID {self.mask_account(edge_id)}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()

    async def process_user_login(self, email: str, password: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        user = None
        while user is None:
            user = await self.user_login(email, password, proxy)
            if not user:
                proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                await asyncio.sleep(5)
                continue

            token = user.get("token")
            user_id = user.get("user", {}).get("uuid")

            self.print_message(email, proxy, Fore.GREEN, "Login Success")

            return token, user_id
        
    async def process_user_devices(self, email: str, token: str, nodes_count: int, use_proxy: bool, connection_choice: int):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        devices = []

        if connection_choice == 1:
            device_lists = await self.user_devices(email, token, proxy)
            if not device_lists:
                edge_id = self.generate_edge_id()
                return devices.append({"EdgeId":edge_id})
            
            for device in device_lists[:nodes_count]:
                if device:
                    edge_id = device.get("name")
                    devices.append({"EdgeId":edge_id})

            return devices

        else:
            for i in range(nodes_count):
                edge_id = self.generate_edge_id()
                devices.append({"EdgeId":edge_id})

            return devices

    async def process_accounts(self, email: str, password: str, nodes_count: int, use_proxy: bool, connection_choice: int):
        token, user_id = await self.process_user_login(email, password, use_proxy)
        if token and user_id:

            tasks = []
            if use_proxy:
                devices = await self.process_user_devices(email, token, nodes_count, use_proxy, connection_choice)
                for device in devices:
                    if device:
                        edge_id = device.get("EdgeId")
                        tasks.append(asyncio.create_task(self.connect_websocket(email, user_id, edge_id, use_proxy)))
                        self.total_edge += 1
            else:
                edge_id = self.generate_edge_id()
                tasks.append(asyncio.create_task(self.connect_websocket(email, user_id, edge_id, use_proxy)))
                self.total_edge += 1

            await asyncio.gather(*tasks)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                return

            nodes_count, proxy_choice, connection_choice = self.print_question()

            use_proxy = False
            if proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        email = account.get("Email")
                        password = account.get("Password")

                        if "@" in email and password:
                            tasks.append(asyncio.create_task(self.process_accounts(email, password, nodes_count, use_proxy, connection_choice)))

                tasks.append(self.print_edge_ids_estabilished())
                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise

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