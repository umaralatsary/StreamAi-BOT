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

    async def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy_counts = {}
            for used_proxy in self.account_proxies.values():
                proxy_counts[used_proxy] = proxy_counts.get(used_proxy, 0) + 1
            
            available_proxies = self.proxies.copy()
            available_proxies.sort(key=lambda x: proxy_counts.get(self.check_proxy_schemes(x), 0))
            proxy = self.check_proxy_schemes(available_proxies[0])
            
            self.account_proxies[account] = proxy
        return self.account_proxies[account]

    async def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def generate_edge_id(self):
        hex_chars = '0123456789abcdefghijklmnopqrstuvwxyz'
        edge_id = ''.join(random.choice(hex_chars) for _ in range(32))
        return edge_id

    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

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
        try:
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
        except asyncio.CancelledError:
            return

    def print_question(self):
        while True:
            try:
                print("1. Use Exiting Edge Ids")
                print("2. Create New Edge Ids")
                connection_choice = int(input("Choose [1/2] -> ").strip())
                if connection_choice in [1, 2]:
                    break
                else:
                    print(f"{Fore.RED+Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")
        
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
                    print(f"{Fore.YELLOW}Recommended: 1-3 nodes per account for stable CPU usage{Style.RESET_ALL}")
                    nodes_count = int(input("How Many Edge Ids Do You Want to Run For Each Account? -> ").strip())
                    if nodes_count > 0:
                        if nodes_count > 3:
                            print(f"{Fore.YELLOW}Warning: High node count may cause high CPU usage{Style.RESET_ALL}")
                            confirm = input("Continue anyway? (y/n): ").strip().lower()
                            if confirm != 'y':
                                continue
                        break
                    else:
                        print(f"{Fore.RED+Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
    
        while True:
            try:
                print(f"{Fore.YELLOW}Enter 0 if you don't want to use batch processing{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Recommended: 5-10 accounts per batch for stable performance{Style.RESET_ALL}")
                batch_size = int(input("How Many Accounts Do You Want to Process Per Batch? -> ").strip())
                if batch_size >= 0:
                    if batch_size > 10:
                        print(f"{Fore.YELLOW}Warning: Large batch size may affect stability{Style.RESET_ALL}")
                        confirm = input("Continue anyway? (y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    break
                else:
                    print(f"{Fore.RED+Style.BRIGHT}Please enter a non-negative number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
        
        return nodes_count, proxy_choice, connection_choice, batch_size

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

    async def user_login(self, email: str, password: str, proxy=None):
        url = "https://api.minionlab.ai/web/v1/auth/emailLogin"
        data = json.dumps({"email":email, "code":"", "password":password, "referralCode":"zwYPzVWI"})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        try:
            response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=30, impersonate="safari15_5")
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
                return result['data']
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
        send_ping = None
        session = None
        retry_count = 0
        max_retries = 5
    
        while True and retry_count < max_retries:
            try:
                if session:
                    await session.close()
                
                proxy = await self.get_next_proxy_for_account(edge_id) if use_proxy else None
                connector = ProxyConnector.from_url(proxy) if proxy else None
                timeout = ClientTimeout(total=60, connect=60, sock_connect=60)
                session = ClientSession(connector=connector, timeout=timeout)
    
                async with session.ws_connect(wss_url, headers=headers, heartbeat=20) as wss:
                    async def send_ping_message():
                        try:
                            while True:
                                await wss.send_json({"type":"ping"})
                                self.print_message(email, proxy, Fore.WHITE,
                                    f"Edge ID {edge_id}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}PING Success{Style.RESET_ALL}"
                                )
                                await asyncio.sleep(20)
                        except asyncio.CancelledError:
                            return
                        except Exception:
                            return
    
                    if not connected:
                        await wss.send_json({"type":"register", "user":user_id, "dev":edge_id})
                        self.print_message(email, proxy, Fore.WHITE,
                            f"Edge ID {edge_id}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                        )
                        self.edge_estabilished += 1
                        connected = True
                        ready_to_ping = False
    
                    while connected:
                        if send_ping is None and ready_to_ping:
                            send_ping = asyncio.create_task(send_ping_message())
                        try:
                            response = await wss.receive()
                            try:
                                response_data = json.loads(response.data)
                            except (json.JSONDecodeError, TypeError):
                                response_data = response.data
    
                            if isinstance(response_data, dict):
                                if response_data.get("type") == "request":
                                    url = response_data.get("data", {}).get("url")
                                    task_id = response_data.get("taskid")
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
                                            f"Edge ID {edge_id}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.GREEN + Style.BRIGHT}Create Connection Success{Style.RESET_ALL}"
                                        )
                                        ready_to_ping = True
    
                                    else:
                                        self.print_message(email, proxy, Fore.WHITE,
                                            f"Edge ID {edge_id}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.YELLOW + Style.BRIGHT}Create Connection Failed{Style.RESET_ALL}"
                                        )
    
                                elif response_data.get("type") == "cancel":
                                    self.print_message(email, proxy, Fore.WHITE,
                                        f"Edge ID {edge_id}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Connection Cancelled{Style.RESET_ALL}"
                                    )
    
                            elif isinstance(response_data, str) and response_data.strip().lower() == "pong":
                                self.print_message(email, proxy, Fore.WHITE,
                                    f"Edge ID {edge_id}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.BLUE + Style.BRIGHT}PONG Received{Style.RESET_ALL}"
                                )
    
                        except Exception as e:
                            if send_ping and not send_ping.done():
                                send_ping.cancel()
                                try:
                                    await send_ping
                                except asyncio.CancelledError:
                                    pass
                                except Exception:
                                    pass
                                send_ping = None
    
                            self.print_message(email, proxy, Fore.WHITE,
                                f"Edge ID {edge_id} "
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Websocket Connection Closed: {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                            )
                            await asyncio.sleep(5)
                            self.edge_estabilished -= 1
                            connected = False
                            break
    
            except Exception as e:
                retry_count += 1
                if session:
                    await session.close()
                session = None
                
                if use_proxy and retry_count < max_retries:
                    self.account_proxies.pop(edge_id, None)
                    await asyncio.sleep(5)
                
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Edge ID {edge_id} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Websocket Not Connected: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                if retry_count >= max_retries:
                    break
                await asyncio.sleep(5)
    
            except asyncio.CancelledError:
                if send_ping and not send_ping.done():
                    send_ping.cancel()
                    try:
                        await send_ping
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass
                    send_ping = None
    
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Edge ID {edge_id}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                )
                break
    
            finally:
                if send_ping and not send_ping.done():
                    send_ping.cancel()
                    try:
                        await send_ping
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass
                if session:
                    await session.close()

    async def process_user_login(self, email: str, password: str, use_proxy: bool):
        proxy = await self.get_next_proxy_for_account(email) if use_proxy else None
        user = None
        while user is None:
            user = await self.user_login(email, password, proxy)
            if not user:
                proxy = await self.rotate_proxy_for_account(email) if use_proxy else None
                await asyncio.sleep(5)
                continue

            token = user.get("token")
            user_id = user.get("user", {}).get("uuid")

            self.print_message(email, proxy, Fore.GREEN, "Login Success")

            return token, user_id

    async def process_user_devices(self, email: str, token: str, nodes_count: int, use_proxy: bool, connection_choice: int):
        proxy = await self.get_next_proxy_for_account(email) if use_proxy else None
        devices = []
        if connection_choice == 1:
            device_lists = None
            while device_lists is None:
                device_lists = await self.user_devices(email, token, proxy)
                if not device_lists:
                    proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                exciting_devices = device_lists.get("rows", [])
                if use_proxy:
                    if isinstance(exciting_devices, list) and len(exciting_devices) == 0:
                        for _ in range(nodes_count):
                            edge_id = self.generate_edge_id()
                            devices.append({"EdgeId":edge_id})
                        return devices

                    for device in exciting_devices[:nodes_count]:
                        if device:
                            edge_id = device.get("name")
                            devices.append({"EdgeId":edge_id})
                    return devices

                for device in exciting_devices[:1]:
                    if device:
                        edge_id = device.get("name")
                        devices.append({"EdgeId":edge_id})
                return devices

        if use_proxy:
            for _ in range(nodes_count):
                edge_id = self.generate_edge_id()
                devices.append({"EdgeId":edge_id})
            return devices

        edge_id = self.generate_edge_id()
        devices.append({"EdgeId":edge_id})
        return devices

    async def process_accounts(self, email: str, password: str, nodes_count: int, use_proxy: bool, connection_choice: int):
        token, user_id = await self.process_user_login(email, password, use_proxy)
        if token and user_id:
            devices = await self.process_user_devices(email, token, nodes_count, use_proxy, connection_choice)
            if devices:
                tasks = []
                for device in devices:
                    if device:
                        edge_id = device.get("EdgeId")
                        tasks.append(asyncio.create_task(self.connect_websocket(email, user_id, edge_id, use_proxy)))
                        self.total_edge += 1

                await asyncio.gather(*tasks)

    async def process_batch(self, batch_accounts, nodes_count: int, use_proxy: bool, connection_choice: int):
        tasks = []
        for account in batch_accounts:
            if account:
                email = account.get("Email")
                password = account.get("Password")
                if "@" in email and password:
                    tasks.append(asyncio.create_task(
                        self.process_accounts(email, password, nodes_count, use_proxy, connection_choice)
                    ))
        return tasks
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
    
            nodes_count, proxy_choice, connection_choice, batch_size = self.print_question()
    
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
    
            if batch_size == 0:
                try:
                    current_batch_tasks = await self.process_batch(accounts, nodes_count, use_proxy, connection_choice)
                    monitor_task = asyncio.create_task(self.print_edge_ids_estabilished())
                    
                    batch_future = asyncio.gather(*current_batch_tasks, return_exceptions=True)
                    shielded_batch = asyncio.shield(batch_future)
                    
                    try:
                        await asyncio.gather(monitor_task, shielded_batch)
                    except Exception as e:
                        monitor_task.cancel()
                        try:
                            await monitor_task
                        except asyncio.CancelledError:
                            pass
                        
                        for task in current_batch_tasks:
                            if not task.done():
                                task.cancel()
                        
                        await asyncio.gather(*current_batch_tasks, return_exceptions=True)
                    
                    if use_proxy:
                        self.account_proxies.clear()
                    
                except Exception as e:
                    self.log(f"{Fore.RED+Style.BRIGHT}Process Error: {e}{Style.RESET_ALL}")
                    await asyncio.sleep(5)
    
            else:
                batches = [accounts[i:i + batch_size] for i in range(0, len(accounts), batch_size)]
                
                while True:
                    for batch_index, batch in enumerate(batches):
                        self.log(
                            f"{Fore.GREEN + Style.BRIGHT}Processing Batch {batch_index + 1} "
                            f"(Accounts {batch_index * batch_size + 1}-{min((batch_index + 1) * batch_size, len(accounts))})"
                            f"{Style.RESET_ALL}"
                        )
    
                        try:
                            import gc
                            gc.collect()
                            
                            current_batch_tasks = await self.process_batch(batch, nodes_count, use_proxy, connection_choice)
                            monitor_task = asyncio.create_task(self.print_edge_ids_estabilished())
                            
                            batch_future = asyncio.gather(*current_batch_tasks, return_exceptions=True)
                            shielded_batch = asyncio.shield(batch_future)
                            
                            try:
                                await asyncio.wait_for(
                                    asyncio.gather(monitor_task, shielded_batch),
                                    timeout=300 # 5 minutes per batch
                                )
                            except asyncio.TimeoutError:
                                monitor_task.cancel()
                                try:
                                    await monitor_task
                                except asyncio.CancelledError:
                                    pass
                                
                                for task in current_batch_tasks:
                                    if not task.done():
                                        task.cancel()
                                
                                await asyncio.gather(*current_batch_tasks, return_exceptions=True)
                            
                            self.log(
                                f"{Fore.YELLOW + Style.BRIGHT}Batch {batch_index + 1} completed. "
                                f"Moving to next batch...{Style.RESET_ALL}"
                            )
    
                            self.edge_estabilished = 0
                            self.total_edge = 0
                            
                            if use_proxy:
                                self.account_proxies.clear()
                            
                            await asyncio.sleep(10)
                        
                        except Exception as e:
                            self.log(f"{Fore.RED+Style.BRIGHT}Batch Error: {e}{Style.RESET_ALL}")
                            await asyncio.sleep(5)
                            continue
    
                    await asyncio.sleep(30)
                    gc.collect()
    
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
