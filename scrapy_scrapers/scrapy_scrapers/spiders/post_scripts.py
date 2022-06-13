import os
import json

from django.conf import settings
from observations.models import IGUser


def add_ig_user_info_to_db():
    folder = settings.DATA_PATH / 'ig_user_info'
    if not folder.exists():
        return

    data: dict[str, dict] = dict()
    for filepath in folder.iterdir():
        if not filepath.is_file() or not filepath.suffix.replace('.', '') or filepath.suffix.replace('.', '') != 'json':
            continue

        with open(filepath) as file:
            data[filepath.name.replace('.json', '')] = json.load(file)

        os.remove(str(filepath))

    usernames = data.keys()
    users = IGUser.objects.filter(username__in=usernames)
    for username, info in data.items():
        for user in users:
            if user.username == username:
                for k, v in info.items():
                    setattr(user, k, v)

                break

    try:
        IGUser.objects.bulk_update(users, ['media_count', 'follower_count', 'following_count',
                                           'full_name', 'category_name', 'biography', 'external_url'])
    except Exception:
        for username, info in data.items():
            with open(folder / f'{username}.json', 'w') as file:
                json.dump(info, file)
