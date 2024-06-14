import psycopg2
from typing import List, Dict, Any
import requests


def fetch_hh_ru_data(company_list: List[str]) -> List[Dict[str, Any]]:
    """
    Получение данных о работодателях и вакансиях с использованием API HH.ru.

    Параметры:
    - employer_ids: Список строк, представляющих идентификаторы работодателей, для которых нужно получить данные.

    Возвращает:
    Список словарей, где каждый словарь содержит информацию о работодателе и список вакансий.
    """
    data = []
    for employer_id in company_list:
        employer_response = requests.get('https://api.hh.ru/employers/' + employer_id)
        employer_info = employer_response.json()

        vacancies = []
        vacancy_response = requests.get('https://api.hh.ru/vacancies?employer_id=' + employer_id)
        vacancies_text = vacancy_response.json()

        vacancies.extend(vacancies_text['items'])

        data.append({
            'employers': employer_info,
            'vacancies': vacancies
        })
    return data


def create_base(base_name: str, params: dict):
    """Функция для создания базы данных и таблиц для сохранения данных

    Args:
        имя_базы_данных (str): Имя базы данных, которую необходимо создать
    Создает базу данных с указанным именем, а также две таблицы 'employers' и 'vacancies' для хранения информации
    о работодателях и вакансиях соответственно.
    """

    # conn = psycopg2.connect(**params)
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"DROP DATABASE IF EXISTS {base_name}")
    except:
        cur.execute(f"CREATE DATABASE {base_name}")

    conn.close()

    conn = psycopg2.connect(dbname=base_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employers (
                employer_id SERIAL PRIMARY KEY,
                company_name VARCHAR(500) NOT NULL,
                open_vacancies INTEGER,
                employer_url TEXT,
                description TEXT)
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employers(employer_id),
                vacancy_name VARCHAR(500) NOT NULL,
                salary_from INTEGER,
                vacancy_url TEXT)
        """)

    conn.commit()
    conn.close()

