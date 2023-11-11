from func.utils import WelcomeMessage, interact_with_user
from colorama import init, Fore


init(autoreset=True)

if __name__ == "__main__":
    print(Fore.GREEN + "Введите ваше имя")
    user_name = input()
    welcome_message = (
        f"{user_name}  - добро пожаловать в программу прогнозирования цен на продукты"
    )
    welcome = WelcomeMessage(welcome_message)
    print(Fore.GREEN + f"{welcome}")

    # Запуск контекстного меню
    interact_with_user()