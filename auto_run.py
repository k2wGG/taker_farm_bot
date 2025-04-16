import time
import random
from modules.sowing import run_sowing_farm
from rich.console import Console

console = Console()

def auto_run_sowing():
    """
    Автоматический запуск Sowing-нод каждые 3 часа.
    Каждый цикл запускает фарм, затем засыпает на 3 часа (10800 секунд),
    с дополнительным случайным разбросом ±5 минут для равномерного распределения нагрузки по прокси.
    """
    cycle = 1
    while True:
        console.rule(f"[bold cyan]Запуск Sowing-фарма: Цикл {cycle}[/bold cyan]")
        try:
            run_sowing_farm()
        except Exception as e:
            console.print(f"[red]Ошибка в процессе фарма: {str(e)}[/red]")

        console.print(f"[yellow]Цикл {cycle} завершён. Ожидание 3 часа перед следующим запуском...[/yellow]")
        
        # Добавляем случайный разброс ±5 минут (от -300 до +300 секунд)
        additional_delay = random.randint(-300, 300)
        total_sleep = 10800 + additional_delay  # 10800 секунд = 3 часа
        time.sleep(total_sleep)
        cycle += 1

if __name__ == "__main__":
    auto_run_sowing()
