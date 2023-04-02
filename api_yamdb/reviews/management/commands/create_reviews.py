import csv

from api_yamdb.settings import BASE_DIR
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


DATA_IMPORT_DIR = f'{BASE_DIR}/static/data'


class Command(BaseCommand):
    """Команда manage.py create_review - заполняет базу тестовыми данными
    из csv файлов.
    python manage.py create_reviews --table name_table - заполняет таблицу
    name_table тестовыми данными.
    manage.py create_review --overwrite - полностью перезаписывает данные в БД.
    python manage.py create_reviews --overwrite --table name_table
    - перезаписывает данные в таблице name_table.
    """
    help = (
        'используйте: manage.py create_review'
        ' для заполнения БД тестовыми данными'
    )
    PARAMETERS_LOADING_LIST = {
        'category': {
            'fdata': f'{DATA_IMPORT_DIR}/category.csv',
            'model': Category,
        },
        'genre': {
            'fdata': f'{DATA_IMPORT_DIR}/genre.csv',
            'model': Genre,
        },
        'title': {
            'fdata': f'{DATA_IMPORT_DIR}/titles.csv',
            'model': Title,
        },
        'genretitle': {
            'fdata': f'{DATA_IMPORT_DIR}/genre_title.csv',
            'model': GenreTitle,
        },
        'user': {
            'fdata': f'{DATA_IMPORT_DIR}/users.csv',
            'model': User,
        },
        'review': {
            'fdata': f'{DATA_IMPORT_DIR}/review.csv',
            'model': Review,
        },
        'comment': {
            'fdata': f'{DATA_IMPORT_DIR}/comments.csv',
            'model': Comment,
        }
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '-ow', '--overwrite',
            action='store_true',
            help='перезаписать данные в тестовой БД'
        )
        parser.add_argument(
            '-t', '--table',
            type=str, help='имя таблица для заполнения тестовыми данными'
        )

    def loading_data(self, fdata, model):
        with open(fdata, 'r') as fdata:
            data = csv.reader(fdata)
            fields = next(data)
            for row in data:
                record = dict(zip(fields, row))
                try:
                    m = model(**record)
                    m.save()
                except Exception as ex:
                    print(
                        f'запись из файла {fdata.name}:'
                        f' {record} содержит ошибки и не была занесена в БД.'
                        f' Возникло исключение {ex}.'
                    )

    def handle(self, *args, **options):
        overwrite = options.get('overwrite')
        table = options.get('table')

        # --overwrite --table
        if overwrite and table:
            param_load = self.PARAMETERS_LOADING_LIST.get(table)
            self.loading_data(**param_load)
            return f'Данные в таблице {table} перезаписаны.'

        # --overwrite
        if overwrite and not table:
            for table_name in self.PARAMETERS_LOADING_LIST:
                param_load = self.PARAMETERS_LOADING_LIST[table_name]
                self.loading_data(**param_load)
            return 'Данные в БД перезаписаны.'

        # --table
        if table and not overwrite:
            param_load = self.PARAMETERS_LOADING_LIST.get(table)
            if param_load['model'].objects.count() > 0:
                return (
                    f'Таблица {table} содержит данные,'
                    ' если вы хотите перезаписать данные в таблице,'
                    ' используйте команду: \n'
                    'python manage.py create_reviews --overwrite --table'
                    f' {table}'
                )
            self.loading_data(**param_load)
            return 'Данные в таблицу {table} записаны.'

        for table_name in self.PARAMETERS_LOADING_LIST:
            param_load = self.PARAMETERS_LOADING_LIST[table_name]
            if param_load['model'].objects.count() > 0:
                return (
                    'БД содержит данные, если вы хотите'
                    ' перезаписать данные в таблицах, используйте команду \n'
                    'python manage.py create_reviews --overwrite'
                )

        for table_name in self.PARAMETERS_LOADING_LIST:
            param_load = self.PARAMETERS_LOADING_LIST[table_name]
            self.loading_data(**param_load)

        return 'Загрузка данных в БД завершена.'
