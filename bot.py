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
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'manual_proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
    
    def generate_edge_id(self):
        hex_chars = '0123456789abcdef'
        edge_id = ''.join(random.choice(hex_chars) for _ in range(32))
        return edge_id
    
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    async def handle_tasks(self, url, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=url, headers={}) as response:
                    if response.status == 200:
                        result = await response.text()
                        return result, response.status
        except (Exception, ClientResponseError) as e:
            return None, None
        
    async def connect_websocket(self, user_id, edge_id: str, proxy=None):
        wss_url = "wss://gw0.streamapp365.com/connect"
        connected = False

        register_message = {
            "type":"register", 
            "user":user_id, 
            "dev":edge_id
        }

        while True:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=30))
            try:
                async with session.ws_connect(wss_url, headers=self.headers) as wss:
                    if not connected:
                        await wss.send_json(register_message)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                        connected = True

                    if connected:
                        async def send_ping():
                            while not wss.closed:
                                try:
                                    await wss.send_json({"type":"ping"})
                                    self.log(
                                        f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                                        f"{Fore.GREEN + Style.BRIGHT}PING{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                                    )
                                except Exception as e:
                                    break

                                await asyncio.sleep(20)

                        try:
                            async for msg in wss:
                                if msg.data == "pong":
                                    self.log(
                                        f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT}PONG{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                                    )
                                else:
                                    try:
                                        message = json.loads(msg.data)
                                        if message.get("type") == "request":
                                            task_id = message.get("taskid")
                                            url = message.get("data", {}).get("url")
                                            data, status_code = await self.handle_tasks(url, proxy)
                                            if data is not None or status_code is not None:
                                                response_message = {
                                                    "type":"response",
                                                    "taskid":task_id,
                                                    "result":{
                                                        "parsed":"",
                                                        "html":b64encode((quote(data)).encode('utf-8')).decode('utf-8'),
                                                        "rawStatus":status_code
                                                    }
                                                }
                                                await wss.send_json(response_message)
                                                self.log(
                                                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                    f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                                    f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                    f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                                                    f"{Fore.GREEN + Style.BRIGHT}Create Connection Success{Style.RESET_ALL}"
                                                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                                                )
                                                ping = asyncio.create_task(send_ping())

                                            else:
                                                connected = False
                                                break

                                        elif message.get("type") == "cancel":
                                            self.log(
                                                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                                f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                                                f"{Fore.YELLOW + Style.BRIGHT}Connection Cancelled{Style.RESET_ALL}"
                                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                                            )
                                            connected = False
                                            break

                                        else:
                                            connected = False
                                            break

                                    except Exception as e:
                                        connected = False
                                        break

                        except Exception as e:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}Websocket Connection Closed{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                            connected = False

                        finally:
                            if not wss.closed:
                                await wss.close()

                            ping.cancel()

                            try:
                                await ping
                            except asyncio.CancelledError:
                                pass

            except Exception as e:    
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Websocket Not Connected{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                connected = False
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Edge-ID:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(edge_id)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()
        
    async def question(self):
        while True:
            try:
                print("1. Run With Auto Proxy")
                print("2. Run With Manual Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto Proxy" if choose == 1 else 
                        "With Manual Proxy" if choose == 2 else 
                        "Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def process_accounts(self, user_id: str, proxy_count: int, use_proxy: bool):
        proxy = None
        tasks = []

        if use_proxy:
            max_connections = 20 # U can Change it
            connections_to_create = min(proxy_count, max_connections)

            for i in range(connections_to_create):
                if proxy_count > 0:
                    proxy = self.get_next_proxy()
                    proxy_count -= 1
                    edge_id = self.generate_edge_id()
                    task = asyncio.create_task(self.connect_websocket(user_id, edge_id, proxy))
                    tasks.append(task)
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(user_id)} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}No Availabe Proxies{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}] {Style.RESET_ALL}"
                    )
                    break

        else:
            edge_id = self.generate_edge_id()
            task = asyncio.create_task(self.connect_websocket(user_id, edge_id, proxy))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('userids.txt', 'r') as file:
                user_ids = [line.strip() for line in file if line.strip()]

            use_proxy_choice = await self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(user_ids)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy_choice == 2:
                await self.load_manual_proxy()

            proxy_count = len(self.proxies)

            while True:
                tasks = []
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