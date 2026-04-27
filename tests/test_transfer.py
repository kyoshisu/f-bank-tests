import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# URL вашего локального сервера с F-Bank
BASE_URL = "http://localhost:3000/"


class TestFBank:
    
    def test_bug_1_card_field_allows_17_digits(self, driver):
        """
        БАГ №1: Поле ввода номера карты принимает 17 цифр вместо 16
        """
        driver.get(BASE_URL + "?balance=30000")
        time.sleep(1)
        
        # Кликаем на карточку RUB
        rub_card = driver.find_element(By.XPATH, "//div[contains(., 'Рубли')]")
        rub_card.click()
        time.sleep(0.5)
        
        # Находим поле для номера карты
        card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
        
        # Пытаемся ввести 17 цифр
        card_input.clear()
        card_input.send_keys("1234 5678 9012 3456 7")
        
        # Получаем значение поля (очищаем от пробелов)
        actual_value = card_input.get_attribute("value").replace(" ", "")
        
        # Ожидаем не более 16 цифр, но получаем 17 — тест упадёт
        assert len(actual_value) <= 16, f"БАГ! Поле принимает {len(actual_value)} цифр вместо 16"
    
    def test_bug_2_negative_amount_is_accepted(self, driver):
        """
        БАГ №2: Поле суммы принимает отрицательные значения
        """
        driver.get(BASE_URL + "?balance=30000")
        time.sleep(1)
        
        # Кликаем на карточку RUB
        rub_card = driver.find_element(By.XPATH, "//div[contains(., 'Рубли')]")
        rub_card.click()
        time.sleep(0.5)
        
        # Находим поле для суммы перевода
        amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        
        # Вводим отрицательную сумму
        amount_input.clear()
        amount_input.send_keys("-50000")
        
        # Получаем введённое значение
        actual_value = amount_input.get_attribute("value")
        
        # Ожидаем, что отрицательных чисел быть не должно — тест упадёт
        is_negative = actual_value.startswith("-")
        assert not is_negative, f"БАГ! Поле принимает отрицательную сумму: {actual_value}"
    
    def test_bug_3_commission_calculation_wrong(self, driver):
        """
        БАГ №3: Комиссия неправильно округляется
        Для суммы 22220 должна быть 2222, но показывает 2220
        """
        driver.get(BASE_URL + "?balance=100000")
        time.sleep(1)
        
        # Кликаем на карточку RUB
        rub_card = driver.find_element(By.XPATH, "//div[contains(., 'Рубли')]")
        rub_card.click()
        time.sleep(0.5)
        
        # Находим поле для суммы перевода
        amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        
        # Тестируем несколько значений комиссии
        test_cases = [
            (20000, "2000"),    # 10% от 20000 = 2000
            (22000, "2200"),    # 10% от 22000 = 2200
            (22200, "2220"),    # 10% от 22200 = 2220 (тут правильно)
            (22220, "2222"),    # 10% от 22220 = 2222 — БАГ! Покажет 2220
        ]
        
        for amount, expected_commission in test_cases:
            amount_input.clear()
            amount_input.send_keys(str(amount))
            time.sleep(0.5)
            
            commission_span = driver.find_element(By.ID, "comission")
            actual_commission = commission_span.text
            
            assert actual_commission == expected_commission, \
                f"БАГ! Сумма={amount}, комиссия={actual_commission}, ожидалось={expected_commission}"