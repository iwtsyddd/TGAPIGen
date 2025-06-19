# TGAPIGen
# by iwtsyd
# a simple Telegram API generator with proxy support
# this script is not related to Telegram* in any way 
# it is just a tool to generate API ID and API HASH for Telegram applications
# you can use it to create your own Telegram bots or applications
# this script is provided "as is" without any warranty or guarantee of functionality.
# please use it at your own risk.
# uses tgapi by staliox, proxy by geonode, get ip by httpbin.org

import requests
import random
import os
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.progress import Progress
import socket

try:
    import tgapi
except ImportError:
    os.system("pip install requests rich pysocks lxml fake_useragent")
    print("tgapi не установлен. 😔\nзагрузка...")
    response = requests.get("https://raw.githubusercontent.com/staliox/Telegram-API-Generator/main/tgapi.py")
    with open("tgapi.py", "wb") as f:
        f.write(response.content)
    print("tgapi успешно установлен. 😊")
    exit()

console = Console()

LANG = {}
LANGS = {
    "ru": {
        "title": "TGAPIGen 1.0\nby iwtsyd",
        "use_proxy": "Использовать прокси для подключения?",
        "choose_proxy": "Выберите вариант",
        "proxy_auto": "1. Автоматически получить свежие прокси",
        "proxy_manual": "2. Ввести прокси вручную",
        "enter_proxy": "Введите прокси в формате ip:port",
        "socks_set": "✓ SOCKS прокси настроен",
        "http_set": "✓ HTTP прокси настроен",
        "fail_fetch_proxy": "❌ Ошибка при получении прокси:",
        "no_proxy": "Не удалось получить прокси, работаем без них",
        "check_connection": "Проверка подключения...",
        "ip_check_fail": "❌ Не удалось получить IP",
        "tg_connect_success": "✅ Подключение к Telegram успешно",
        "tg_connect_fail": "Telegram недоступен",
        "tg_connect_error": "❌ Не удалось подключиться к Telegram:",
        "continue_without_proxy": "Продолжить без прокси?",
        "start_gen": "Начать генерацию API?",
        "exit": "Выход из приложения...",
        "ask_phone": "Введите номер телефона, привязанный к Telegram",
        "send_code": "Отправляем код подтверждения...",
        "fail_send_code": "Не удалось отправить код подтверждения. Проверь номер или подключение.",
        "enter_code": "Код подтверждения из Telegram",
        "login_success": "Учетная запись успешно авторизована.",
        "login_fail": "Ошибка входа. Возможно, неверный код или аккаунт заблокирован.",
        "checking_app": "Проверка, существует ли уже Telegram API App...",
        "got_app": "Успешно получено",
        "creating_app": "Создаем новое приложение Telegram API...",
        "app_title": "Название приложения",
        "app_short": "Короткое имя",
        "app_url": "URL (оставь пустым если нет)",
        "app_platform": "Платформа",
        "app_desc": "Описание",
        "app_created": "Генерация завершена",
        "fail_app": "Не удалось создать Telegram API App. Проверь данные и попробуй снова.",
        "your_ip": "Ваш IP"
    },
    "en": {
        "title": "TGAPIGen 1.0\nby iwtsyd",
        "use_proxy": "Use proxy for connection?",
        "choose_proxy": "Choose option",
        "proxy_auto": "1. Get fresh proxies automatically",
        "proxy_manual": "2. Enter proxy manually",
        "enter_proxy": "Enter proxy in format ip:port",
        "socks_set": "✓ SOCKS proxy set",
        "http_set": "✓ HTTP proxy set",
        "fail_fetch_proxy": "❌ Error fetching proxy:",
        "no_proxy": "Could not get proxies, continuing without",
        "check_connection": "Checking connection...",
        "ip_check_fail": "❌ Could not get IP",
        "tg_connect_success": "✅ Telegram connection successful",
        "tg_connect_fail": "Telegram unavailable",
        "tg_connect_error": "❌ Could not connect to Telegram:",
        "continue_without_proxy": "Continue without proxy?",
        "start_gen": "Start API generation?",
        "exit": "Exiting app...",
        "ask_phone": "Enter your Telegram phone number",
        "send_code": "Sending confirmation code...",
        "fail_send_code": "Failed to send confirmation code. Check number or connection.",
        "enter_code": "Confirmation code from Telegram",
        "login_success": "Account successfully authorized.",
        "login_fail": "Login error. Wrong code or account is banned.",
        "checking_app": "Checking if Telegram API App exists...",
        "got_app": "Successfully received",
        "creating_app": "Creating new Telegram API App...",
        "app_title": "App title",
        "app_short": "Short name",
        "app_url": "App URL (leave empty if none)",
        "app_platform": "Platform",
        "app_desc": "Description",
        "app_created": "Generation complete",
        "fail_app": "Could not create Telegram API App. Check inputs.",
        "your_ip": "Your IP"
    }
}

def select_language():
    global LANG
    lang = Prompt.ask("Choose language / Выберите язык", choices=["ru", "en"], default="ru")
    LANG = LANGS[lang]

def fetch_proxies():
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Fetching proxies...", total=1)
            response = requests.get(
                "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc",
                timeout=10
            )
            data = response.json()
            proxies = [f"{p['ip']}:{p['port']}" for p in data['data'] if p['protocols']]
            progress.update(task, completed=1)
            return proxies
    except Exception as e:
        console.print(f"[red]{LANG['fail_fetch_proxy']} {e}[/red]")
        return None

def setup_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geek) Chrome/91.0.4472.124 Safari/537.36'
    })

    use_proxy = Confirm.ask(f"\n[bold]{LANG['use_proxy']}[/bold]", default=True)

    if use_proxy:
        console.print(f"\n[bold]{LANG['proxy_auto']}[/bold]\n[bold]{LANG['proxy_manual']}[/bold]")
        choice = Prompt.ask(LANG['choose_proxy'], choices=["1", "2"], default="1")

        if choice == "1":
            proxies = fetch_proxies()
            if proxies:
                proxy = random.choice(proxies)
                console.print(f"\n[green]Random proxy selected: {proxy}[/green]")
            else:
                console.print(f"\n[yellow]{LANG['no_proxy']}[/yellow]")
                return session
        else:
            proxy = Prompt.ask(f"\n{LANG['enter_proxy']}")

        if proxy.startswith(('socks4', 'socks5')):
            try:
                import socks
                proxy_type = socks.SOCKS5 if 'socks5' in proxy else socks.SOCKS4
                ip, port = proxy.replace('socks4://', '').replace('socks5://', '').split(':')
                socks.set_default_proxy(proxy_type, ip, int(port))
                socket.socket = socks.socksocket
                console.print(f"[green]{LANG['socks_set']}[/green]")
            except ImportError:
                console.print("[red]PySocks not installed. pip install pysocks[/red]")
                return None
        else:
            session.proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            console.print(f"[green]{LANG['http_set']}[/green]")

    return session

def check_proxy(session):
    try:
        console.print(f"\n[bold]{LANG['check_connection']}[/bold]")
        console.print(" ")
        response = session.get("http://httpbin.org/ip", timeout=10)
        if response.status_code == 200:
            ip = response.json().get('origin', 'unknown')
            console.print(Panel.fit(
                f"🌍 {LANG['your_ip']}: [bold green]{ip}[/bold green]",
                title="IP",
                border_style="green"
            ))
        else:
            console.print(f"[red]{LANG['ip_check_fail']}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]{LANG['ip_check_fail']} {e}[/red]")
        return False

    try:
        response = session.get("https://my.telegram.org", timeout=10)
        if response.status_code == 200:
            console.print(Panel.fit(
                f"[bold green]{LANG['tg_connect_success']}[/bold green]",
                title="Telegram",
                border_style="green"
            ))
            return True
        else:
            console.print(Panel.fit(
                f"[bold red]{LANG['tg_connect_fail']} ({response.status_code})[/bold red]",
                title="Telegram",
                border_style="red"
            ))
            return False
    except Exception as e:
        console.print(f"[red]{LANG['tg_connect_error']} {e}[/red]")
        return False

def start_gen():
    console.print(f"\n[bold]{LANG['ask_phone']}[/bold]")
    phone = Prompt.ask("[bold cyan]Phone[/bold cyan]")

    console.print(f"\n[bold]{LANG['send_code']}[/bold]")
    app = tgapi.TelegramApplication(phone_number=phone)

    if not app.send_password():
        console.print(f"[red]{LANG['fail_send_code']}[/red]")
        return

    password = Prompt.ask(f"\n[bold cyan]{LANG['enter_code']}[/bold cyan]")

    if not app.auth_login(password):
        console.print(f"[red]{LANG['login_fail']}[/red]")
        return

    console.print(f"\n[bold green]{LANG['login_success']}[/bold green]")
    console.print(f"\n[bold]{LANG['checking_app']}[/bold]")
    result = app.auth_app()

    if result:
        api_id, api_hash = result
        console.print(Panel.fit(
            f"[bold green]API ID:[/bold green] {api_id}\n[bold green]API HASH:[/bold green] {api_hash}",
            title=LANG['got_app'],
            border_style="green"
        ))
    else:
        console.print(f"[bold yellow]{LANG['creating_app']}[/bold yellow]")
        app.app_title = Prompt.ask(LANG['app_title'])
        app.app_shortname = Prompt.ask(LANG['app_short'])
        app.app_url = Prompt.ask(LANG['app_url'], default="")
        app.app_platform = Prompt.ask(LANG['app_platform'], default="desktop")
        app.app_desc = Prompt.ask(LANG['app_desc'], default="")

        result = app.auth_app()
        if result:
            api_id, api_hash = result
            console.print(Panel.fit(
                f"[bold green]API ID:[/bold green] {api_id}\n[bold green]API HASH:[/bold green] {api_hash}",
                title=LANG['app_created'],
                border_style="green"
            ))
        else:
            console.print(f"[red]{LANG['fail_app']}[/red]")

def main():
    select_language()
    console.print(Panel.fit(f"[bold]{LANG['title']}[/bold]", style="bold blue", border_style="blue"))
    session = setup_session()
    if not session:
        return
    if not check_proxy(session):
        if not Confirm.ask(f"\n[red]{LANG['continue_without_proxy']}[/red]"):
            return
        session = requests.Session()
    start_app = Confirm.ask(f"\n[bold]{LANG['start_gen']}[/bold]", default=True)
    if not start_app:
        console.print(f"[bold red]{LANG['exit']}[/bold red]")
        return
    start_gen()

if __name__ == "__main__":
    main()