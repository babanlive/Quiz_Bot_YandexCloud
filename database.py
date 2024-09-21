import os
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)    

# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0,
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0,
    },
    {
        'question': 'Какой тип данных используется для хранения последовательности символов в Python?',
        'options': ['str', 'list', 'tuple', 'dict'],
        'correct_option': 0,
    },
    {
        'question': 'Какой оператор используется для "не равно" в Python?',
        'options': ['==', '!=', '<=', '=>'],
        'correct_option': 1,
    },
    {
        'question': 'Какой оператор используется для вычисления остатка от деления в Python?',
        'options': ['-', '**', '//', '+', '%'],
        'correct_option': 4,
    },
    {
        'question': 'Каков результат выражения "True and False" в Python?',
        'options': ['True', 'False', 'Error', 'None'],
        'correct_option': 1,
    },
    {
        'question': 'Для чего в Python используются блоки "try" и "except"?',
        'options': ['Для вывода текста на консоль', 'Для выполнения операций с файлами', 'Для обработки исключений или ошибок в коде', 'Для создания циклов'],
        'correct_option': 2,

    },
    {
        'question': 'Какое из следующих не является допустимым именем переменной в Python?',
        'options': ['my_variable', '2variable',  '_variable', 'variable_2'],
        'correct_option': 1,
    },
    {
        'question': 'Что такое декоратор в Python?',
        'options': ['Синтаксис для создания списков', 'Инструмент для перебора последовательностей', 'Тип класса Python', 'Функция, которая изменяет другую функцию'],
        'correct_option': 3,
    },
    {
        'question': 'Что представляет собой ключевое слово "self" в классе Python?',
        'options': ['Статический метод внутри класса', 'Экземпляр класса', 'Глобальная переменная внутри класса', 'Сам класс'],
        'correct_option': 1,
    },

]

