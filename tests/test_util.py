from func.utils import WelcomeMessage, config
import pytest


def test_welcome_message():
    """Тест для welcome_message"""
    message = "Тестовое приветствие"
    welcome_message = WelcomeMessage(message)
    # Тестирование
    message_test = (
        f"+{'-' * (len(message) + 4)}+\n|  {message}  |\n+{'-' * (len(message) + 4)}+\n"
    )
    assert str(welcome_message) == message_test


def test_create_border():
    """Тест для create_border"""
    welcome_message = WelcomeMessage("Hello")
    border = welcome_message.create_border(5, 3)
    assert border == "+------+\n"


def test_existing_section():
    """Тест наличия данных для подключения"""
    # params = config("../database.ini") # Строка для теста конкретного файла
    params = config()  # Строка для теста pytest --cov

    assert "host" in params
    assert "port" in params
    assert "user" in params
    assert "password" in params


def test_non_existing_file():
    """Тест отсутствия файла"""

    with pytest.raises(Exception):
        config("non_existent.ini", "postgresql")


def test_empty_config_file(tmpdir):
    """Тест для случая, когда конфигурация файла существует, но он пустой"""
    empty_config_file = tmpdir.join("empty_config.ini")
    with open(empty_config_file, "w") as f:
        pass  # Создаем пустой файл
    with pytest.raises(Exception) as excinfo:
        config(empty_config_file, "postgresql")
    assert "Section postgresql is not found" in str(excinfo.value)