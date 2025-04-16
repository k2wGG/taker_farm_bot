import time
import requests
from web3 import Web3
from eth_account.messages import encode_defunct
from modules.wallet_manager import load_wallets_from_env, assign_random_proxy
from rich.console import Console
from rich.table import Table

console = Console()
BASE_URL = 'https://sowing-api.taker.xyz'
TOKENS = {}

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://sowing.taker.xyz',
    'referer': 'https://sowing.taker.xyz/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36'
}

def sign_message(private_key, message):
    w3 = Web3()
    message_hash = encode_defunct(text=message)
    signed = w3.eth.account.sign_message(message_hash, private_key)
    return signed.signature.hex()

def retry_request(request_func, retries=3, delay=300, cooldown=600):
    for attempt in range(retries):
        try:
            return request_func()
        except requests.exceptions.RequestException as e:
            if any(code in str(e) for code in ['502', '503', '504']):
                console.print(f"[yellow]Попытка {attempt+1}/{retries} неудачна: {e}\nОжидание {delay // 60} минут перед повтором...[/yellow]")
                time.sleep(delay)
            else:
                raise
    console.print(f"[red]Достигнут лимит повторов. Отдых 10 минут...[/red]")
    time.sleep(cooldown)
    return None

def api_post(url, data=None, token=None, proxy=None):
    headers = HEADERS.copy()
    if token:
        headers['authorization'] = f"Bearer {token}"
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    def make_request():
        response = requests.post(f"{BASE_URL}{url}", json=data, headers=headers, proxies=proxies, timeout=15)
        response.raise_for_status()
        return response.json()

    return retry_request(make_request)

def api_get(url, token=None, proxy=None):
    headers = HEADERS.copy()
    if token:
        headers['authorization'] = f"Bearer {token}"
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    def make_request():
        response = requests.get(f"{BASE_URL}{url}", headers=headers, proxies=proxies, timeout=15)
        response.raise_for_status()
        return response.json()

    return retry_request(make_request)

def login(wallet):
    try:
        nonce_resp = api_post("/wallet/generateNonce", {"walletAddress": wallet['address']}, proxy=wallet.get('proxy'))
        if not nonce_resp:
            return None
        nonce = nonce_resp.get('result', {}).get('nonce')
        if not nonce:
            console.print(f"[yellow]Не удалось получить nonce для {wallet['address']}[/yellow]")
            return None

        message = f"Taker quest needs to verify your identity to prevent unauthorized access. Please confirm your sign-in details below:\n\naddress: {wallet['address']}\n\nNonce: {nonce}"
        signature = sign_message(wallet['privateKey'], message)

        login_resp = api_post("/wallet/login", {
            "address": wallet['address'],
            "signature": signature,
            "message": message
        }, proxy=wallet.get('proxy'))

        if not login_resp:
            return None

        token = login_resp.get('result', {}).get('token')
        return token
    except Exception as e:
        console.print(f"[red]Ошибка входа для {wallet['address']}: {str(e)}[/red]")
        return None

def perform_signin(wallet, token):
    try:
        resp = api_get("/task/signIn?status=true", token, wallet.get('proxy'))
        if resp and resp.get('code') == 200:
            console.print(f"[green]✓ Фарм выполнен: {wallet['address']}[/green]")
            return True
        else:
            console.print(f"[yellow]! Ошибка фарма: {wallet['address']} - {resp.get('message')}[/yellow]")
    except Exception as e:
        console.print(f"[red]Ошибка при фарме {wallet['address']}: {str(e)}[/red]")
    return False

def get_user_info(wallet, token):
    try:
        resp = api_get("/user/info", token, wallet.get('proxy'))
        return resp.get('result', {}) if resp else {}
    except Exception as e:
        console.print(f"[red]Ошибка получения информации по {wallet['address']}: {str(e)}[/red]")
        return {}

def run_sowing_farm():
    wallets = assign_random_proxy(load_wallets_from_env())
    for wallet in wallets:
        token = login(wallet)
        if token:
            TOKENS[wallet['address']] = token
            perform_signin(wallet, token)
            time.sleep(1)

def print_wallet_status():
    wallets = assign_random_proxy(load_wallets_from_env())
    table = Table(title="Статус кошельков Sowing")
    table.add_column("Кошелек")
    table.add_column("Очки")
    table.add_column("Фарм подряд")
    table.add_column("Награды")

    for wallet in wallets:
        token = TOKENS.get(wallet['address']) or login(wallet)
        if token:
            info = get_user_info(wallet, token)
            table.add_row(
                wallet['address'],
                str(info.get('takerPoints', '—')),
                str(info.get('consecutiveSignInCount', '—')),
                str(info.get('rewardCount', '—')),
            )
            TOKENS[wallet['address']] = token
        else:
            table.add_row(wallet['address'], "Ошибка", "-", "-")
        time.sleep(0.5)
    console.print(table)

def refresh_tokens():
    wallets = assign_random_proxy(load_wallets_from_env())
    for wallet in wallets:
        token = login(wallet)
        if token:
            TOKENS[wallet['address']] = token
            console.print(f"[green]Токен обновлён для {wallet['address']}[/green]")
        else:
            console.print(f"[red]Не удалось обновить токен: {wallet['address']}[/red]")
