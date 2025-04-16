import os
import questionary
from questionary import Style
from rich import print
from auto_run import auto_run_sowing

from modules.wallet_manager import create_wallets_interactive
from modules.sowing import run_sowing_farm, print_wallet_status, refresh_tokens
from modules.lightmining import start_lightmining_farm

def print_banner():
    print(r"""
[bold cyan]
 _   _           _  _____      
| \ | |         | ||____ |     
|  \| | ___   __| |    / /_ __ 
| . ` |/ _ \ / _` |    \ \ '__|
| |\  | (_) | (_| |.___/ / |   
\_| \_/\___/ \__,_|\____/|_|   

Taker Manager Bot - автоматическое управление LightMining и Sowing
TG: @nod3r
[/bold cyan]
""")

# Настраиваем цвета и стили для questionary
custom_style = Style([
    ("qmark", "fg:#5F819D bold"),
    ("question", "bold fg:yellow"),   # вопрос будет желтым и жирным
    ("answer",   "fg:#FF9D00 bold"),
    ("pointer",  "fg:#FF9D00 bold"),
    ("highlighted", "fg:#FF9D00 bold"),
    ("selected", "fg:#5F819D"),
    ("instruction", ""),  # убираем текст "(Use arrow keys)"
    ("text", ""),
    ("disabled", "fg:#858585 italic"),
])

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()

        choice = questionary.select(
            "Выберите действие:",
            choices=[
                "1. Создать кошельки (только генерация)",
                "2. Запустить фарм LightMining",
                "3. Запустить фарм Sowing",
                "4. Посмотреть статус всех кошельков (Sowing)",
                "5. Обновить токены Sowing",
                "6. Автозапуск Sowing (каждые 3 часа)",
                "7. Выход"
            ],
            style=custom_style,
            instruction=""
        ).ask()

        if not choice:
            break

        if choice.startswith("1"):
            create_wallets_interactive()
        elif choice.startswith("2"):
            start_lightmining_farm()
        elif choice.startswith("3"):
            run_sowing_farm()
        elif choice.startswith("4"):
            print_wallet_status()
        elif choice.startswith("5"):
            refresh_tokens()
        elif choice.startswith("6"):
            auto_run_sowing()  # вызываем функцию автозапуска
        elif choice.startswith("7"):
            break

        input("\nНажмите Enter для возврата в меню...")

if __name__ == "__main__":
    main_menu()
