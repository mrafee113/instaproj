import os

from argparse import ArgumentParser
from observations.scripts.client import setup_client
from observations.scripts.hashtag import parse_medias, download_hashtag_top_medias
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs the regular tasks.'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-n', '--name', type=str, required=True)
        parser.add_argument('-a', '--amount', type=int, required=True)

    def handle(self, *args, **options):
        client = setup_client()
        name, amount = options['name'], options['amount']
        medias, filepath = download_hashtag_top_medias(client, name, amount)
        self.stdout.write(self.style.SUCCESS(f'successfully downloaded medias from #{name}'))
        parse_medias(medias)
        os.remove(filepath)
        self.stdout.write(self.style.SUCCESS(f'successfully parsed medias from #{name} into database.'))
