import os
import json
import subprocess

from django.db.models import Q
from django.conf import settings
from observations.models import IGUser
from django.core.management.base import BaseCommand
from scrapy_scrapers.scrapy_scrapers.spiders.post_scripts import add_ig_user_info_to_db


class Command(BaseCommand):
    help = 'Runs the regular tasks.'

    def handle(self, *args, **options):
        dst = settings.BASE_DIR / 'scrapy_scrapers'
        os.chdir(dst)
        usernames = IGUser.objects.filter(~Q(username=str()), follower_count=0, biography=str())
        if usernames.count() == 0:
            self.stdout.write('there are no users left.')
            return
        usernames = json.dumps(list(usernames.values_list('username', flat=True))).replace(' ', '')

        command = f"scrapy crawl profile_spider -a usernames='{usernames}'"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        self.stdout.write('-' * 100 + '  OUTPUT:\n')
        self.stdout.write(str(output))
        self.stdout.write('\n' * 2 + '-' * 100 + '  ERROR:\n')
        self.stdout.write(str(error))
        self.stdout.write('\n\n' + self.style.SUCCESS('Downloaded Profile information.'))
        self.stdout.write('\n' + 'now parsing them to db...')
        add_ig_user_info_to_db()
        self.stdout.write('\n' + self.style.SUCCESS('Parsed user information into db.'))

        unsuccessful = IGUser.objects.filter(~Q(username=str()), follower_count=0, biography=str())
        self.stdout.write(f'some were not successful. count={unsuccessful.count()}')
        self.stdout.write('\nusernames=', json.dumps(list(unsuccessful.values_list('username', flat=True))))
