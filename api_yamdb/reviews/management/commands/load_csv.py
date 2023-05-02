import csv
import os

from api_yamdb.settings import CSV_FILES_DIRS
from django.core.management import BaseCommand
from django.db import IntegrityError

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


FIELDS_NAMES = {
    'category': ('category', Category),
    'title_id': ('title', Title),
    'genre_id': ('genre', Genre),
    'author': ('author', User),
    'review_id': ('review', Review),
}

CATEGORIES_NAMES = {
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'genre_title': GenreTitle,
    'users': User,
    'review': Review,
    'comments': Comment,
}


def open_csv(file_name):
    csv_file = file_name + '.csv'
    csv_path = os.path.join(CSV_FILES_DIRS, csv_file)
    try:
        with (open(csv_path, encoding='utf-8')) as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        print(f'Файл {csv_file} не найден.')


def change_values(data_csv):
    csv_copy = data_csv.copy()
    for field_key, field_value in data_csv.items():
        if field_key in FIELDS_NAMES.keys():
            field_key0 = FIELDS_NAMES[field_key][0]
            csv_copy[field_key0] = FIELDS_NAMES[field_key][1].objects.get(
                pk=field_value)
    return csv_copy


def load_csv(file_name, model_name):
    table_not_loaded = f'Таблица {model_name.__qualname__} не загружена.'
    table_loaded = f'Таблица {model_name.__qualname__} загружена.'
    data = open_csv(file_name)
    rows = data[1:]
    for row in rows:
        data_csv = dict(zip(data[0], row))
        data_csv = change_values(data_csv)
        try:
            table = model_name(**data_csv)
            table.save()
        except (ValueError, IntegrityError) as error:
            print(f'Ошибка при загрузке данных: {error}. '
                  f'{table_not_loaded}')
            break
    print(table_loaded)


class Command(BaseCommand):
    """Класс загрузки базы данных."""

    def handle(self, *args, **options):
        for key, value in CATEGORIES_NAMES.items():
            print(f'Загрузка таблицы {value.__qualname__}')
            load_csv(key, value)
