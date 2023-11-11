from configparser import ConfigParser
import pandas as pd
import psycopg2
from db_scr.DBManage import DBManage

from colorama import init, Fore

# Для WIN10+
init(autoreset=True)


class WelcomeMessage:
    """Класс вывода приветствия в стиле псевдографики"""

    def __init__(self, message):
        self.message = message

    def create_border(self, width, height):
        """Создание рамки"""
        border = "+" + "-" * (width + 1) + "+\n"
        return border * (height - 4) + border

    def create_welcome_message(self):
        """Создание сообщения"""
        width = len(self.message) + 3
        height = 3
        border = self.create_border(width, height)
        welcome = f"|  {self.message}  |\n"
        return border + welcome + border

    def __str__(self):
        return self.create_welcome_message()


def interact_with_user():
    """Функция для взаимодействия с пользователем."""
    # Инициируем объекты классов для работы
    params = config()

    name_db = "testing"
    try:
        db_manager = DBManage(name_db, params)
    except psycopg2.OperationalError:
        # Проверка подключения и наличие БД
        print(Fore.RED + "Ошибка подключения к базе данных")
        print(f"Пытаемся создать БД с названием {name_db}")
        try:
            create_database(params)
            print(Fore.RED + "Перезапустите программу")
        except psycopg2.OperationalError:
            print(Fore.RED + "Проверьте фаервол")

    else:
        while True:
            # Запускаем бесконечный цикл для работы меню
            print(Fore.GREEN + "Выберите действие:")

            print(
                Fore.BLUE
                + "1 - Пересоздание базы данных и таблиц (Осторожно, старая БД будет удалена!"
            )
            print(Fore.BLUE + "2 - Заполняем таблицу БД данными из cvs файла")
            print(Fore.GREEN + "3 - Прогнозирование цен методом линейной регрессии")
            print(Fore.GREEN + "4 - Прогнозирование цен методом случайных деревьев")
            print(
                Fore.GREEN
                + "5 - Прогнозирование цен самым простым методом, подсчета средней цены"
            )
            print(
                Fore.CYAN
                + "6 - Вывод  максимальной и минимальной цены по каждому товару "
            )
            print(Fore.CYAN + "7 - Вывод  количества записей для каждого продукта")
            print(
                Fore.CYAN
                + "8 -  Вывод краткой справки о методах прогноза цен (Справка)"
            )
            print(Fore.MAGENTA + "9 - Выйти")
            choice = input(Fore.GREEN + "Введите значение---")

            # Непосредственно работы меню выбора
            if choice == "1":
                db_manager.create_tables()
                print(f"База данных {name_db} и таблицы  созданы")
            elif choice == "2":
                try:
                    csv_filename = "csv_data.csv"
                    df = pd.read_csv(csv_filename)
                except FileNotFoundError:
                    print(Fore.RED + "Нет файла, загрузите файл")
                else:
                    try:
                        db_manager.error_table()
                    except psycopg2.errors.UndefinedTable:
                        # Проверка наличие таблицы
                        print(Fore.RED + "Нет таблиц, создайте - пункт 1")
                    else:
                        print(
                            Fore.GREEN
                            + "Таблица заполняется. требуется много времени(несколько минут)"
                        )
                        print(Fore.GREEN + f"Всего в базе {len(df)} элементов")
                        db_manager.insert_table(csv_filename)
                        print("Таблицы заполнены")
            elif choice == "3":
                try:
                    db_manager.load_data()
                    db_manager.train_models()
                    # Прогнозирование цен для всех продуктов
                    all_predictions = db_manager.predict_prices_for_all_products()
                    if all_predictions == {}:
                        print(Fore.RED + "Ошибка - Заполните таблицу данными")
                    # Вывод результатов
                    for product, price in all_predictions.items():
                        mse = (
                            db_manager.mse_scores.get(product, None) / db_manager.number
                        )
                        print(
                            Fore.WHITE + f"Прогнозируемая цена на {product}: {price}, "
                            f"среднее отклонение {round((mse / price) * 100, 2)} процентов"
                        )
                except psycopg2.errors.UndefinedTable:
                    print(Fore.RED + "Ошибка - Создайте таблицу")
                except psycopg2.errors.InFailedSqlTransaction:
                    print(Fore.RED + "Ошибка - Создайте таблицу")

            elif choice == "4":
                try:
                    db_manager.load_data()
                    db_manager.train_models__not_line()
                    # Прогнозирование цен для всех продуктов
                    all_predictions = db_manager.predict_prices_for_all_products()
                    if all_predictions == {}:
                        print(Fore.RED + "Ошибка - Заполните таблицу данными")
                    # Вывод результатов
                    for product, price in all_predictions.items():
                        mse = (
                            db_manager.mse_scores.get(product, None)
                            / db_manager.number_not_line
                        )
                        print(
                            Fore.WHITE + f"Прогнозируемая цена на {product}: {price}, "
                            f"среднее отклонение {round((mse / price) * 100, 2)} процентов"
                        )
                except psycopg2.errors.UndefinedTable:
                    print(Fore.RED + "Ошибка - Создайте таблицу")
                except psycopg2.errors.InFailedSqlTransaction:
                    print(Fore.RED + "Ошибка - Создайте таблицу")

            elif choice == "5":
                try:
                    db_manager.load_data()
                    average_prices = db_manager.get_average_prices_for_each_product()
                    if average_prices == {}:
                        print(Fore.RED + "Ошибка - Заполните таблицу данными")
                    print(Fore.WHITE + "Вывод средних цен")
                    for key, value in average_prices.items():
                        print(Fore.WHITE + f"{key}:{value}")
                except psycopg2.errors.UndefinedTable:
                    print(Fore.RED + "Ошибка - Создайте таблицу")
                except psycopg2.errors.InFailedSqlTransaction:
                    print(Fore.RED + "Ошибка - Создайте таблицу")

            elif choice == "6":
                try:
                    db_manager.load_data()
                    max_min_prices = db_manager.get_max_min_price_for_each_product()
                    if max_min_prices == {}:
                        print(Fore.RED + "Ошибка - Заполните таблицу данными")
                    for product, prices in max_min_prices.items():
                        print(Fore.WHITE + f"Product: {product}")
                        print(Fore.WHITE + f"Максимальная цена: {prices['max_price']}")
                        print(Fore.WHITE + f"MМинимальная цена: {prices['min_price']}")
                except psycopg2.errors.UndefinedTable:
                    print(Fore.RED + "Ошибка - Создайте таблицу")
                except psycopg2.errors.InFailedSqlTransaction:
                    print(Fore.RED + "Ошибка - Создайте таблицу")

            elif choice == "7":
                try:
                    db_manager.load_data()
                    record_counts = db_manager.get_record_count_for_each_product()
                    for product, prices in record_counts.items():
                        print(Fore.WHITE + f"Продукт: {product}")
                        print(
                            Fore.WHITE
                            + f"Количество записей в БД: {record_counts[product]}\n"
                        )
                except psycopg2.errors.UndefinedTable:
                    print(Fore.RED + "Ошибка - Создайте таблицу")
                except psycopg2.errors.InFailedSqlTransaction:
                    print(Fore.RED + "Ошибка - Создайте таблицу")
                except UnboundLocalError:
                    print(Fore.RED + "Ошибка - трассировка")

            elif choice == "8":
                print(
                    "Линейная регрессия (англ. Linear regression) — используемая в статистике регрессионная "
                    "модель зависимости одной (объясняемой, зависимой) переменной y от другой "
                    "или нескольких других переменных (факторов, регрессоров, "
                    "независимых переменных) x с линейной функцией зависимости."
                )
                print(
                    "Подробнее https://ru.wikipedia.org/wiki/%D0%9B%D0%B8%D0%BD%D0%B5%D0%B9%D0%BD%D0%B0%D1%8F"
                    "_%D1%80%D0%B5%D0%B3%D1%80%D0%B5%D1%81%D1%81%D0%B8%D1%8F"
                )
                print(
                    "Метод случайного леса (RandomForestRegressor)"
                    " - алгоритм предсказания использующим модели случайных деревьев"
                )
                print(
                    "Подробнее https://ru.wikipedia.org/wiki/"
                    "%D0%9C%D0%B5%D1%82%D0%BE%D0%B4_%D1%81%D0%BB%D1%83%D1%87%D0%B0%D0%B9%"
                    "D0%BD%D0%BE%D0%B3%D0%BE_%D0%BB%D0%B5%D1%81%D0%B0"
                )
            elif choice == "9":
                # Выход
                db_manager.close_connection()
                print(Fore.MAGENTA + "--------------")
                print(Fore.MAGENTA + "Спасибо за обращение\n" "Конец работы!")
                print(Fore.MAGENTA + "--------------")
                break


def config(filename="database.ini", section="postgresql"):
    """Функция с данными для подключения к БД"""
    # создаем парсер
    parser = ConfigParser()
    # читаем конфиг файл
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} is not found in the {1} file.".format(section, filename)
        )
    return db


def create_database(params: dict):
    """Для первичного создания БД"""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("CREATE DATABASE testing")
    cur.close()
    conn.close()