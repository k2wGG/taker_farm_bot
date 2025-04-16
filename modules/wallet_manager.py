import os
import random
from web3 import Web3
from dotenv import set_key, load_dotenv
from rich.console import Console
from rich.prompt import IntPrompt

console = Console()
ENV_FILE = '.env'

load_dotenv()

def generate_wallet():
    w3 = Web3()
    acct = w3.eth.account.create()
    return acct.key.hex(), acct.address

def save_wallet_to_env(index, private_key):
    key_name = f"PRIVATE_KEY_{index}"
    set_key(ENV_FILE, key_name, private_key)

def create_wallets_interactive():
    num = IntPrompt.ask("Сколько кошельков вы хотите создать?")
    
    with open("accounts.txt", "a") as f:
        for i in range(1, num + 1):
            private_key, address = generate_wallet()
            save_wallet_to_env(i, private_key)
            f.write(f"Wallet {i}:\nPrivate Key: {private_key}\nAddress: {address}\n{'-'*60}\n")
            console.print(f"[green]✓ Кошелек {i} создан: {address}[/green]")

    console.print(f"\n[yellow]{num} кошельков успешно создано и добавлено в .env[/yellow]")

def load_wallets_from_env():
    wallets = []
    i = 1
    while True:
        key = os.getenv(f"PRIVATE_KEY_{i}")
        if not key:
            break
        w3 = Web3()
        acct = w3.eth.account.from_key(key)
        wallets.append({
            'privateKey': key,
            'address': acct.address
        })
        i += 1
    return wallets

def load_proxies():
    if not os.path.exists('proxies.txt'):
        return []
    with open('proxies.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def assign_random_proxy(wallets):
    proxies = load_proxies()
    for wallet in wallets:
        wallet['proxy'] = random.choice(proxies) if proxies else None
    return wallets