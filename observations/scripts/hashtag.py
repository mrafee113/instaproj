import pickle
import sys

from typing import Union
from instagrapi import Client
from django.conf import settings

from observations.models import Media, IGUser, Resource, Location, HashTag


def uniqify(objs: list) -> list:
    _t = list()
    for obj in objs:
        if obj not in _t:
            _t.append(obj)
    return _t


def something(model_klass, objs: list, pk_field: str,
              alt_objs: Union[list, list[list]] = None,
              alt_pk_field: Union[str, list[str]] = None,
              alt_ref_field: Union[str, list[str]] = None,
              reload: bool = False):
    # update
    existing_objs = model_klass.objects.all()
    existing_objs_pks = {getattr(obj, pk_field) for obj in existing_objs if
                         hasattr(obj, pk_field) and getattr(obj, pk_field)}
    downloaded_objs_pks = {getattr(obj, pk_field) for obj in objs if
                           hasattr(obj, pk_field) and getattr(obj, pk_field)}
    to_update_objs = uniqify([obj for obj in existing_objs if
                              getattr(obj, pk_field) in existing_objs_pks.intersection(downloaded_objs_pks)])
    model_klass.objects.bulk_update(to_update_objs, model_klass.update_keys)
    # create
    non_existing_objs_pks = {getattr(obj, pk_field) for obj in objs if obj and getattr(obj, pk_field) and
                             getattr(obj, pk_field) not in existing_objs_pks}
    to_create_objs = uniqify([obj for obj in objs if obj and getattr(obj, pk_field) and
                              getattr(obj, pk_field) in non_existing_objs_pks])
    model_klass.objects.bulk_create(to_create_objs, ignore_conflicts=True)
    # reload objs
    if reload:
        objs = model_klass.objects.filter(**{f'{pk_field}__in': set(existing_objs_pks) | set(non_existing_objs_pks)})

    if any(map(lambda x: x is None, (alt_objs, alt_pk_field, alt_ref_field))):
        return objs
    # update alt model obj references
    if isinstance(alt_pk_field, list) and len(alt_objs) != len(alt_pk_field) != len(alt_ref_field):
        return
    elif not isinstance(alt_pk_field, list):
        alt_objs, alt_pk_field, alt_ref_field = [alt_objs], [alt_pk_field], [alt_ref_field]

    for alt_objs, alt_pk_field, alt_ref_field in zip(alt_objs, alt_pk_field, alt_ref_field):
        for alt_obj in alt_objs:
            if getattr(alt_obj, alt_pk_field) is None:
                continue

            for obj in objs:
                if getattr(alt_obj, alt_pk_field) == getattr(obj, pk_field):
                    setattr(alt_obj, alt_ref_field, obj)

    return objs


def download_hashtag_top_medias(client: Client, name: str, amount: int, force: bool = False):
    folder = settings.DATA_PATH / 'hashtag_data'
    folder.mkdir(exist_ok=True)
    filepath = folder / f'{name}.pickle'
    if filepath.exists() and not force:
        return
    dl_medias = client.hashtag_medias_top(name, amount)
    with open(filepath, 'wb') as file:
        pickle.dump(dl_medias, file)

    return dl_medias, filepath


def parse_medias(dl_medias: list[Media]):
    folder = settings.DATA_PATH / 'hashtag_data'
    folder.mkdir(exist_ok=True)

    medias: list[Media] = list()
    users: list[IGUser] = list()
    locations: list[Location] = list()
    all_resources: list[Resource] = list()
    all_usertags: list[tuple[str, list]] = list()
    all_hashtags: list[HashTag] = list()

    for media in dl_medias:
        media_dict = media.dict()
        # media_dict.update({'user': client.user_info(media.user.pk).dict()})
        obj, user, location, resources, usertags, hashtags = Media.from_dict(media_dict)

        medias.append(obj)
        users.append(user)
        if location is not None:
            locations.append(location)
        if resources:
            all_resources.extend(resources)
        if usertags:
            all_usertags.append((obj.ig_pk, usertags))
        if hashtags:
            all_hashtags.extend(hashtags)

    # locations
    something(Location, locations, 'ig_pk',
              [users, medias], ['location_ig_pk', 'location_ig_pk'], ['location', 'location'], reload=True)
    # users
    something(IGUser, users, 'ig_pk',
              medias, 'user_ig_pk', 'user', reload=True)
    # medias
    medias = something(Media, medias, 'ig_pk', all_resources, 'media_ig_pk', 'media', reload=True)
    # resources
    something(Resource, all_resources, 'ig_pk')
    # usertags
    usertag_user_objs = list(IGUser.objects.filter(
        ig_pk__in=[usertag for _, usertags in all_usertags for usertag in usertags]
    ))
    existing_usertag_pks = {i.ig_pk for i in usertag_user_objs}
    for media_ig_pk, media_usertag_pks in all_usertags:
        if not media_usertag_pks or not media_ig_pk:
            continue

        # existing users
        media_usertag_user_objs = [obj for user_ig_pk in media_usertag_pks for obj in usertag_user_objs
                                   if obj.ig_pk == user_ig_pk]
        # download non-existing users
        for user_pk in set(media_usertag_pks) - set(existing_usertag_pks):
            print(f'WARNING! ignored usertag. uid={user_pk} mid={media_ig_pk}', file=sys.stderr)
            # user_info = client.user_info(user_pk)
            # user_obj = IGUser.from_dict(user_info.dict())
            # media_usertag_user_objs.append(user_obj)

        for media in medias:
            if media_ig_pk == media.ig_pk:
                new_objs = list(filter(lambda x: x and x.id is None, media_usertag_user_objs))
                media.usertags.bulk_create(new_objs)
                old_objs = list(filter(lambda x: x and x not in new_objs, media_usertag_user_objs))
                media.usertags.add(*(new_objs + old_objs))
                break

    # hashtags
    for media in medias:
        if not media.hashtags:
            continue

        media_tag_objs = list()
        for media_tag_name in media.hashtags:
            for tag in all_hashtags:
                if not tag:
                    continue
                if not tag.ig_id or not tag.media_count:
                    # tag.evaluate(client)
                    print(f'WARNING! ignored tag eval. tag={tag} mid={media.ig_pk}', file=sys.stderr)

                if tag.name == media_tag_name:
                    media_tag_objs.append(tag)

        media.tags.add(media_tag_objs)
