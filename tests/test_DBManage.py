import pytest
import os
import pandas as pd
import psycopg2
from db_scr.DBManage import DBManage

# Путь к тестовому файлу CSV
TEST_CSV_FILE = "test_data.csv"

# Параметры для временной тестовой базы данных
TEST_DB_NAME = "test_db"
TEST_DB_PARAMS = {
    "user": "postgres",
    "password": "12345",
    "host": "localhost",
    "port": "5432",
}


@pytest.fixture(scope="module")
def test_db():
    # Создание временной базы данных для тестов
    conn_temp = psycopg2.connect(dbname="postgres", **TEST_DB_PARAMS)
    conn_temp.autocommit = True
    cur_temp = conn_temp.cursor()
    cur_temp.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cur_temp.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cur_temp.close()
    conn_temp.close()
    yield
    # Удаление временной базы данных после завершения всех тестов
    conn_temp = psycopg2.connect(dbname="postgres", **TEST_DB_PARAMS)
    conn_temp.autocommit = True
    cur_temp = conn_temp.cursor()
    cur_temp.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cur_temp.close()
    conn_temp.close()


@pytest.fixture(scope="module")
def test_data():
    # Создание временного файла CSV с тестовыми данными
    data = {
        "price": [10.0, 20.0, 30.0],
        "count": [5.0, 10.0, 15.0],
        "add_cost": [2.0, 3.0, 4.0],
        "product": ["A", "B", "A"],
        "company": ["X", "Y", "X"],
    }
    df = pd.DataFrame(data)
    df.to_csv(TEST_CSV_FILE, index=False)
    yield
    # Удаление временного файла CSV после завершения всех тестов
    os.remove(TEST_CSV_FILE)


def test_create_database(test_db):
    """Создание БД, тест"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_database()
    # Проверяем, что база данных успешно создана
    assert db_manager.conn is not None


def test_create_tables(test_db):
    """Тест создания таблиц"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    # Проверяем, что таблица "products" успешно создана
    db_manager.cur.execute("SELECT * FROM products")
    assert db_manager.cur.rowcount == 0


def test_insert_table(test_db, test_data):
    """Тест заполнения таблиц"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    # Проверяем, что данные успешно вставлены в таблицу
    db_manager.cur.execute("SELECT * FROM products")
    assert db_manager.cur.rowcount == 3


def test_load_data(test_db, test_data):
    """Тест загрузки данных из БД"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    # Проверяем, что данные успешно загружены
    assert isinstance(db_manager.data, pd.DataFrame)
    assert len(db_manager.data) == 6


def test_train_models(test_db, test_data):
    """Тест обучения модели"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    db_manager.train_models()
    # Проверяем, что модели успешно обучены
    assert len(db_manager.models) == 2
    assert len(db_manager.mse_scores) == 2


def test_train_models_not_line(test_db, test_data):
    """Тест обучения модели, дерева"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    db_manager.train_models__not_line()
    # Проверяем, что модели (не линейные) успешно обучены
    assert len(db_manager.models) == 2
    assert len(db_manager.mse_scores) == 2


def test_predict_prices_for_all_products(test_db, test_data):
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    db_manager.train_models()
    predictions = db_manager.predict_prices_for_all_products()
    # Проверяем, что прогнозы успешно выполнены
    assert isinstance(predictions, dict)
    assert len(predictions) == 2


def test_get_average_prices_for_each_product(test_db, test_data):
    """Тест средней цены"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    average_prices = db_manager.get_average_prices_for_each_product()
    # Проверяем, что средние цены успешно получены
    assert isinstance(average_prices, dict)
    assert len(average_prices) == 2


def test_get_max_min_price_for_each_product(test_db, test_data):
    """Тест максимальной и минимальной цены"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    max_min_prices = db_manager.get_max_min_price_for_each_product()
    # Проверяем, что максимальные и минимальные цены успешно получены
    assert isinstance(max_min_prices, dict)
    assert len(max_min_prices) == 2


def test_get_record_count_for_each_product(test_db, test_data):
    """Тест количества записей"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.insert_table(TEST_CSV_FILE)
    db_manager.load_data()
    record_counts = db_manager.get_record_count_for_each_product()
    # Проверяем, что количество записей успешно получено
    assert isinstance(record_counts, dict)
    assert len(record_counts) == 2


def test_close_connection(test_db):
    """Тест закрытия соединения"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.close_connection()
    # Проверяем, что соединение успешно закрыто
    assert db_manager.conn.closed == 1


def test_error_table(test_db):
    """Тест наличия таблицы"""
    db_manager = DBManage(TEST_DB_NAME, TEST_DB_PARAMS)
    db_manager.create_tables()
    db_manager.error_table()
    # Проверяем, что метод не вызывает ошибку
    assert True