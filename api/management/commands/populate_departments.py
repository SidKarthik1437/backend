from django.core.management.base import BaseCommand
from api.models import Department

class Command(BaseCommand):
    help = 'Populate the Department database with predefined departments'

    def handle(self, *args, **options):
        departments = [
            {'id': 1, 'name': 'ai&ds'},
            {'id': 2, 'name': 'ai&ml'},
            {'id': 3, 'name': 'cse'},
            {'id': 4, 'name': 'ise'},
            {'id': 5, 'name': 'ece'},
            {'id': 6, 'name': 'eee'},
            {'id': 7, 'name': 'ae'},
            {'id': 8, 'name': 'me'},
        ]

        for dept_data in departments:
            department = Department(**dept_data)
            department.save()

        self.stdout.write(self.style.SUCCESS('Departments successfully populated'))
