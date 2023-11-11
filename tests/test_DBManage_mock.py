from unittest import mock
import re
import pytest
import pandas as pd
from unittest.mock import MagicMock
from db_scr.DBManage import DBManage


@pytest.fixture
def mock_db_manage(mocker):
    # Создаем фиктивный объект DBManage для тестирования
    return DBManage(
        database_name="test_db1", params={"user": "postgres", "password": "12345"}
    )


def test_connect_to_database(mock_db_manage, mocker):
    """Тест соединения к БД"""
    # Создаем мок-объект для psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    # Вызываем метод connect_to_database
    mock_db_manage.connect_to_database()

    # Убеждаемся, что connect вызывается с правильными аргументами
    mock_connect.assert_called_once_with(
        dbname="test_db1", user="postgres", password="12345"
    )


def test_create_database(mock_db_manage, mocker):
    """Создание БД, тест"""
    # Создаем мок-объект для psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Создаем мок-объект для psycopg2.cursor
    mock_cursor = mock_conn.cursor.return_value
    # Вызываем метод create_database
    mock_db_manage.create_database()
    # Убеждаемся, что методы для создания и удаления базы данных вызываются
    mock_cursor.execute.assert_any_call("DROP DATABASE IF EXISTS test_db1")
    mock_cursor.execute.assert_any_call("CREATE DATABASE test_db1")


#
def test_create_tables(mock_db_manage, mocker):
    """Тест создания таблиц"""
    # Создаем мок-объект для psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Создаем мок-объект для psycopg2.cursor
    mock_cursor = mock_conn.cursor.return_value
    # Вызываем метод create_tables
    mock_db_manage.create_tables()
    # Убеждаемся, что метод создания таблицы и индекса вызываются
    mock_cursor.execute.assert_any_call(
        "CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, price float, count float,"
        " add_cost float, product VARCHAR(25), company VARCHAR(25))"
    )
    mock_cursor.execute.assert_any_call(
        "SELECT indexname FROM pg_indexes WHERE tablename = 'products' AND indexname = 'product_index';"
    )


def test_insert_table(mock_db_manage, mocker):
    """Тест заполнения таблиц"""
    # Создаем мок-объект для psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Создаем мок-объект для psycopg2.cursor
    mock_cursor = mock_conn.cursor.return_value
    # Вызываем метод insert_table
    #csv_file = "../csv_data_test.csv"  # Замените на путь к вашему тестовому файлу CSV
    csv_file = "test_data.csv"  # Замените на путь к вашему тестовому файлу CSV
    mock_db_manage.insert_table(csv_file)
    # Убеждаемся, что метод copy_expert вызывается с правильными аргументами
    mock_cursor.copy_expert.assert_called_once_with(
        "COPY products(price, count, add_cost, company, product) FROM STDIN WITH CSV HEADER",
        mocker.ANY,
    )


def test_train_models(mock_db_manage):
    """Тест обучения модели"""
    # Подготовим фейковые данные для теста
    mock_db_manage.data = pd.DataFrame(
        {
            "count": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            "add_cost": [10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50],
            "price": [20, 40, 60, 80, 100, 20, 40, 60, 80, 100, 20, 40, 60, 80, 100],
            "product": [
                "A",
                "A",
                "B",
                "B",
                "C",
                "A",
                "A",
                "B",
                "B",
                "C",
                "A",
                "A",
                "B",
                "B",
                "C",
            ],
        }
    )

    # Вызываем метод train_models
    mock_db_manage.train_models()
    # Проверяем, что модели были обучены и добавлены в словарь models
    assert len(mock_db_manage.models) == 3
    assert "A" in mock_db_manage.models
    assert "B" in mock_db_manage.models
    assert "C" in mock_db_manage.models


def test_train_models_not_line(mock_db_manage):
    """Тест обучения модели"""
    # Подготовим фейковые данные для теста
    mock_db_manage.data = pd.DataFrame(
        {
            "count": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            "add_cost": [10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50],
            "price": [20, 40, 60, 80, 100, 20, 40, 60, 80, 100, 20, 40, 60, 80, 100],
            "product": [
                "A",
                "A",
                "B",
                "B",
                "C",
                "A",
                "A",
                "B",
                "B",
                "C",
                "A",
                "A",
                "B",
                "B",
                "C",
            ],
        }
    )
    # Вызываем метод train_models_not_line
    mock_db_manage.train_models__not_line()
    # Проверяем, что модели были обучены и добавлены в словарь models
    assert len(mock_db_manage.models) == 3
    assert "A" in mock_db_manage.models
    assert "B" in mock_db_manage.models
    assert "C" in mock_db_manage.models


def test_get_average_prices_for_each_product(mock_db_manage):
    """Тест средней цены"""
    # Подготовим фейковые данные для теста
    mock_db_manage.data = pd.DataFrame(
        {
            "count": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            "add_cost": [10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50],
            "price": [20, 40, 60, 80, 100, 20, 40, 60, 80, 100, 20, 40, 60, 80, 100],
            "product": [
                "A",
                "A",
                "B",
                "B",
                "C",
                "A",
                "A",
                "B",
                "B",
                "C",
                "A",
                "A",
                "B",
                "B",
                "C",
            ],
        }
    )
    # Создаем фейковый объект self.cur
    fake_cur = mock.MagicMock()
    # Определяем, как метод execute должен обрабатывать запросы SQL
    def execute(sql_query):
        product = sql_query.split("'")[1]  # Извлекаем продукт из запроса
        subset = mock_db_manage.data[mock_db_manage.data["product"] == product]
        average_price = subset["price"].mean()
        fake_cur.fetchone.return_value = (average_price,)

    fake_cur.execute.side_effect = execute
    # Передаем фейковый self.cur в объект mock_db_manage
    mock_db_manage.cur = fake_cur
    # Вызываем метод get_average_prices_for_each_product
    average_prices = mock_db_manage.get_average_prices_for_each_product()
    # Проверяем, что метод возвращает правильные средние цены
    assert average_prices == {"A": 30.0, "B": 70.0, "C": 100.0}


def test_get_max_min_price_for_each_product(mock_db_manage):
    """Тест максимальной и минимальной цены"""
    # Подготовим фейковые данные для теста
    mock_db_manage.data = pd.DataFrame(
        {
            "price": [20, 40, 60, 80, 100, 10, 110],
            "product": ["A", "A", "B", "B", "C", "A", "C"],
        }
    )
    # Вызываем метод get_max_min_price_for_each_product
    max_min_prices = mock_db_manage.get_max_min_price_for_each_product()
    # Проверяем, что метод возвращает правильные максимальные и минимальные цены
    assert max_min_prices == {
        "A": {"max_price": 40, "min_price": 10},
        "B": {"max_price": 80, "min_price": 60},
        "C": {"max_price": 110, "min_price": 100},
    }

def test_get_record_count_for_each_product(mock_db_manage):
    """Тест количества записей"""
    # Подготовим фейковые данные для теста
    mock_db_manage.data = pd.DataFrame({"product": ["A", "A", "B", "B", "C", "A", "C"]})
    # Вызываем метод get_record_count_for_each_product
    record_counts = mock_db_manage.get_record_count_for_each_product()
    # Проверяем, что метод возвращает правильное количество записей
    assert record_counts == {"A": 3, "B": 2, "C": 2}


def test_close_connection(mock_db_manage, mocker):
    """Тест закрытия соединения"""
    # Создаем мок-объект для psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Создаем мок-объект для psycopg2.cursor
    mock_cursor = mock_conn.cursor.return_value
    # Вызываем метод close_connection
    mock_db_manage.close_connection()
    # Убеждаемся, что методы закрытия соединения и курсора вызываются
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_error_table(mock_db_manage, mocker):
    """Тест наличия таблицы"""
    # Создаем мок-объект для psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Создаем мок-объект для psycopg2.cursor
    mock_cursor = mock_conn.cursor.return_value
    # Мокируем результат запроса
    mock_cursor.fetchone.return_value = None
    # Вызываем метод error_table
    mock_db_manage.error_table()
    # Убеждаемся, что метод execute вызывается с правильным SQL-запросом
    expected_sql = "SELECT * FROM products LIMIT 1"
    actual_sql = re.sub(r"\s+", " ", mock_cursor.execute.call_args[0][0]).strip()
    expected_sql = re.sub(r"\s+", " ", expected_sql).strip()
    assert actual_sql == expected_sql


def test_predict_prices_for_all_products(mock_db_manage):
    """Тест прогнозирования цен для продуктов"""
    # Подготовим фейковые данные для теста
    mock_db_manage.data = pd.DataFrame(
        {
            "count": [1, 2, 3, 4, 5],
            "add_cost": [10, 20, 30, 40, 50],
            "price": [20, 40, 60, 80, 100],
            "product": ["A", "A", "B", "B", "C"],
        }
    )

    # Создадим фейковые модели на основе данных из mock_db_manage.data
    mock_db_manage.models = {}
    for product, product_data in mock_db_manage.data.groupby("product"):
        model_mock = mock.Mock(predict=lambda x, p=product_data["price"].mean(): [p])
        mock_db_manage.models[product] = model_mock

    # Вызываем метод predict_prices_for_all_products
    predictions = mock_db_manage.predict_prices_for_all_products()

    # Проверяем, что метод возвращает правильные предсказания
    assert predictions == {"A": 30.0, "B": 70.0, "C": 100.0}