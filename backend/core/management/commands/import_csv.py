import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из ingredients.csv в базу данных ингредиентов'

    def handle(self, *args: any, **options: any) -> None:
        csv_file_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'ingredients.csv',
        )

        with open(csv_file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            print(
                'Процесс импорта начат, он будет выполнен примерно за 20'
                ' секунд',
            )
            for row in reader:
                name = row[0]
                measurement_unit = row[1]
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )
            self.stdout.write(self.style.SUCCESS('Ингредиенты импортированы'))
