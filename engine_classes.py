from abc import ABC, abstractmethod
from connector_class import Connector
import os
import requests
api_key = os.getenv('API_SuperJob')


class Engine(ABC):
    """Абстрактный класс для парсинга вакансий"""
    @abstractmethod
    def get_request(self, keyword):
        """Запрос информации с сайта по ключевому слову"""
        pass

    @staticmethod
    def get_connector(file_name):
        """Возвращает экземпляр класса Connector для работы с записанной в файл json информацией о вакансиях"""
        connector = Connector(file_name)
        return connector

    def save_vacancies(self, file_name, vacancies):
        """Сохраняет собранные с сайтов вакансии в файл json"""
        connector = self.get_connector(file_name)
        connector.insert(vacancies)


class SuperJob(Engine):
    """Класс для парсинга вакансий с сайта SuperJob"""

    @staticmethod
    def _get_salary(salary_info: dict):
        """Обработка поля salary(зарплата): предпочтительно выводить зарплату 'от', если же она не указана,
        то выводить зарплату 'до'. Или выводить 0, если поле отсутствует"""
        if salary_info.get('payment_to'):
            return salary_info['payment_to']
        if salary_info.get('payment_from'):
            return salary_info['payment_from']
        return 0

    @staticmethod
    def _get_remote_work(remote_work_info: dict):
        """Обработка поля remote_work(удаленная работа)"""
        if remote_work_info:
            if remote_work_info['id'] == 1:
                return 'В офисе'
            if remote_work_info['id'] == 2:
                return 'Удаленно'
        return 'Другое'

    def get_request(self, keyword):
        """Парсинг 500 вакансий и создание из них объекта типа list"""
        vacancies = []
        for page_no in range(5):
            response = requests.get('https://api.superjob.ru/2.0/vacancies/', headers={'X-Api-App-Id': api_key},
                                    params={"keywords": keyword, "count": 100,
                                            "page": page_no}).json()
            for vacancy in response['objects']:
                vacancies.append({
                    "name": vacancy['profession'],
                    "company_name": vacancy['firm_name'],
                    "url": vacancy['link'],
                    "description": vacancy['candidat'],
                    "remote_work": self._get_remote_work(vacancy.get('place_of_work', {})),
                    "salary": self._get_salary(vacancy),
                })
        return vacancies


class HeadHunter(Engine):
    """Класс для парсинга вакансий с сайта HeadHunter"""

    @staticmethod
    def _get_salary(salary_info: dict):
        """Обработка поля salary(зарплата): предпочтительно выводить зарплату 'от', если же она не указана,
                то выводить зарплату 'до'. Или выводить 0, если поле отсутствует"""
        if salary_info:
            if salary_info.get('to'):
                return salary_info['to']
            if salary_info.get('from'):
                return salary_info['from']
        return 0

    @staticmethod
    def _get_remote_work(remote_work_info: dict):
        """Обработка поля remote_work(удаленная работа)"""
        if remote_work_info:
            if remote_work_info['id'] == 'fullDay':
                return 'В офисе'
            if remote_work_info['id'] == 'remote':
                return 'Удаленно'
        return 'Другое'

    def get_request(self, keyword):
        """Парсинг 500 вакансий и создание из них объекта типа list"""
        vacancies = []
        for page_no in range(5):
            response = requests.get(f"https://api.hh.ru/vacancies?text={keyword}", params={'per_page': '100', 'page': page_no}).json()
            for vacancy in response['items']:
                vacancies.append({
                    "Название": vacancy['name'],
                    "Компания": vacancy['employer']['name'],
                    "Ссылка": vacancy['alternate_url'],
                    "Описание": vacancy['snippet']['requirement'],
                    "Работа": self._get_remote_work(vacancy.get('schedule', {})),
                    "Зарплата": self._get_salary(vacancy.get('salary', {})),
                })
        return vacancies
