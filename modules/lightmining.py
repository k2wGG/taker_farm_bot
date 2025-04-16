import time
import random
import requests
from web3 import Web3
from eth_account.messages import encode_defunct
from modules.wallet_manager import load_wallets_from_env, assign_random_proxy
from rich.console import Console

console = Console()

BASE_URL = 'https://lightmining-api.taker.xyz'

def get_headers():
    return {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://earn.taker.xyz',
        'Referer': 'https://earn.taker.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36'
    }

def sign_message(private_key, message):
    w3 = Web3()
    message_hash = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(message_hash, private_key)
    return signed_message.signature.hex()

def perform_tasks(session, token, headers):
    tasks = [4, 5, 6, 13, 15]
    completed = 0

    for task_id in tasks:
        try:
            res = session.post(f"{BASE_URL}/assignment/do",
                json={"assignmentId": task_id},
                headers=headers
            ).json()
            if res.get('code') == 200:
                console.print(f"[green]✓ Задание {task_id} выполнено[/green]")
                completed += 1
            else:
                console.print(f"[yellow]! Ошибка в задании {task_id}: {res.get('message')}[/yellow]")
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            console.print(f"[red]Ошибка при выполнении задания {task_id}: {str(e)}[/red]")
    return completed

def is_mining_ready(session, headers):
    try:
        res = session.get(f"{BASE_URL}/user/info", headers=headers).json()
        data = res.get('data', {})
        if data.get('connectedTwitter') and data.get('canStartMining', True):
            return True
        else:
            console.print(f"[yellow]⚠️ Кошелек не готов к майнингу. Подключите Twitter и выполните задания вручную.[/yellow]")
            return False
    except Exception as e:
        console.print(f"[red]Ошибка при проверке статуса майнинга: {str(e)}[/red]")
        return False

def start_lightmining_farm():
    wallets = assign_random_proxy(load_wallets_from_env())

    for index, wallet in enumerate(wallets, start=1):
        console.rule(f"Кошелек {index}: {wallet['address']}")
        try:
            session = requests.Session()
            headers = get_headers()

            proxy = wallet.get('proxy')
            if proxy:
                session.proxies = {'http': proxy, 'https': proxy}

            res = session.post(f"{BASE_URL}/wallet/generateNonce",
                json={"walletAddress": wallet['address']},
                headers=headers
            )

            nonce = res.json().get('data', {}).get('nonce')
            if not nonce:
                console.print("[red]Не удалось получить nonce[/red]")
                continue

            signature = sign_message(wallet['privateKey'], nonce)

            login_res = session.post(f"{BASE_URL}/wallet/login",
                json={
                    "address": wallet['address'],
                    "signature": signature,
                    "message": nonce
                },
                headers=headers
            ).json()

            token = login_res.get('data', {}).get('token')
            if not token:
                console.print("[red]Не удалось авторизоваться[/red]")
                continue

            headers['Authorization'] = f"Bearer {token}"

            if is_mining_ready(session, headers):
                completed = perform_tasks(session, token, headers)

                mining_res = session.post(f"{BASE_URL}/assignment/startMining", headers=headers).json()
                if mining_res.get('code') == 200:
                    console.print(f"[cyan]Майнинг запущен успешно[/cyan]")
                else:
                    console.print(f"[yellow]Не удалось запустить майнинг: {mining_res.get('message')}[/yellow]")

        except Exception as e:
            console.print(f"[red]Ошибка с кошельком {wallet['address']}: {str(e)}[/red]")

        time.sleep(random.uniform(1, 2))