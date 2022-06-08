from django.db import models
from instagrapi import Client
from utils.enums import MediaTypes
from utils.django import DictToObj
from utils.string import extract_hashtags


class Location(models.Model):
    ig_pk = models.CharField(blank=True, max_length=100, unique=True)
    category = models.CharField(blank=True, max_length=100)
    name = models.CharField(blank=True, max_length=100)
    lng = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    city = models.CharField(blank=True, null=True, max_length=100)

    update_keys = ['category', 'name', 'lng', 'lat', 'city']
    convert_keys = {'pk': 'ig_pk'}
    exclude_keys = ['website', 'hours', 'address', 'zip', 'external_id', 'external_id_source', 'phone']

    @staticmethod
    def round_coordinates(value):
        return round(value, 4)

    @classmethod
    def from_dict(cls, location: dict):
        return DictToObj.obj_from_dict(location, cls, cls.convert_keys, cls.exclude_keys,
                                       extra_processors={'lng': [cls.round_coordinates],
                                                         'lat': [cls.round_coordinates]})


class IGUser(models.Model):
    ig_pk = models.CharField(blank=True, max_length=100, unique=True)
    username = models.CharField(blank=True, max_length=150, unique=True)
    full_name = models.CharField(blank=True, max_length=200)
    is_private = models.BooleanField(blank=True, default=False)
    profile_pic_url = models.URLField(max_length=1000, blank=True, null=True)
    profile_pic_url_hd = models.URLField(max_length=1000, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    media_count = models.IntegerField(blank=True, default=0)
    follower_count = models.IntegerField(blank=True, default=0)
    following_count = models.IntegerField(blank=True, default=0)
    biography = models.TextField(blank=True)
    external_url = models.URLField(max_length=1000, blank=True, null=True)  # the url people put in their profile
    is_business = models.BooleanField(blank=True, default=False)
    business_category_name = models.CharField(blank=True, max_length=150)
    category_name = models.CharField(blank=True, max_length=150)
    category = models.CharField(blank=True, max_length=150)
    public_email = models.EmailField(blank=True)
    contact_phone_number = models.CharField(blank=True, max_length=30)
    public_phone_country_code = models.CharField(blank=True, max_length=5)
    public_phone_number = models.CharField(blank=True, max_length=30)
    business_contact_method = models.CharField(blank=True, max_length=50)
    city_id = models.CharField(blank=True, max_length=100)
    city_name = models.CharField(blank=True, max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    location_ig_pk = None

    update_keys = ['full_name', 'profile_pic_url', 'profile_pic_url_hd', 'media_count', 'follower_count',
                     'following_count', 'biography']
    convert_keys = {'pk': 'ig_pk'}
    exclude_keys = ['stories', 'account_type', 'address_street', 'latitude', 'longitude', 'zip',
                    'instagram_location_id', 'interop_messaging_user_fbid']

    @classmethod
    def from_dict(cls, user: dict):
        obj = DictToObj.obj_from_dict(user, cls, cls.convert_keys, cls.exclude_keys)
        location_ig_pk = user.get('instagram_location_id', None)
        obj.location_ig_pk = location_ig_pk
        return obj


class HashTag(models.Model):
    ig_id = models.CharField(blank=True, max_length=100, unique=True)
    name = models.CharField(blank=True, max_length=150, unique=True)
    media_count = models.IntegerField(blank=True, default=0)

    convert_keys = {'id': 'ig_id'}
    exclude_keys = ['profile_pic_url']

    @classmethod
    def from_dict(cls, hashtag: dict):
        obj = DictToObj.obj_from_dict(hashtag, cls, cls.convert_keys, cls.exclude_keys)
        return obj

    @classmethod
    def from_name(cls, name: str):
        return cls(name)

    def evaluate(self, client: Client):
        if self.ig_id is not None or self.media_count != 0 or not self.name:
            return
        tag_info = client.hashtag_info(self.name)
        self.ig_id = tag_info.id
        self.media_count = tag_info.media_count


class Media(models.Model):
    ig_pk = models.CharField(blank=True, max_length=100, unique=True)
    ig_id = models.CharField(blank=True, max_length=100)  # {ig_id}_{user.ig_pk}"
    code = models.SlugField(blank=True)
    title = models.CharField(blank=True, max_length=200)
    caption_text = models.TextField(blank=True)
    url = models.URLField(max_length=1000, blank=True, null=True)
    video_url = models.URLField(max_length=1000, blank=True, null=True)  # for video and igtv
    media_type = models.CharField(blank=True, max_length=7,
                                  choices=[(v, v) for v in ["Photo", "Video", "IGTV", "Reel", "Album"]])
    taken_at = models.DateTimeField(blank=True, null=True)
    comment_count = models.IntegerField(blank=True, default=0)
    like_count = models.IntegerField(blank=True, default=0)  # todo: like_count = -1
    view_count = models.IntegerField(blank=True, default=0)
    video_duration = models.FloatField(default=0)

    user = models.ForeignKey(IGUser, on_delete=models.CASCADE, related_name='medias')
    user_ig_pk = None
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    location_ig_pk = None
    usertags = models.ManyToManyField(IGUser)
    tags = models.ManyToManyField(HashTag)
    hashtags = None

    update_keys = ['code', 'title', 'caption_text', 'url', 'video_url', 'media_type', 'taken_at', 'comment_count',
                   'like_count', 'view_count', 'video_duration', 'user', 'location']
    convert_keys = {'pk': 'ig_pk', 'id': 'ig_id'}
    exclude_keys = ['media_type', 'product_type', 'thumbnail_url', 'has_liked', 'accessibility_caption',
                    'clips_metadata', 'usertags',
                    'user', 'location', 'resources']

    @classmethod
    def from_dict(cls, media: dict):
        obj = DictToObj.obj_from_dict(media, cls, cls.convert_keys, cls.exclude_keys)
        obj.media_type = MediaTypes.decide_type(media['media_type'], media['product_type'])
        user = IGUser.from_dict(media['user'])
        obj.user_ig_pk = user.ig_pk
        location = Location.from_dict(media['location']) if media['location'] is not None else None
        obj.location_ig_pk = location.ig_pk if hasattr(location, 'ig_pk') else None
        resources = [Resource.from_dict(resource, obj) for resource in media['resources']] \
            if media['resources'] else list()

        usertags = list()
        for usertag in media['usertags']:
            if 'user' not in usertag:
                if 'pk' not in usertag['user']:
                    continue
            user_ig_pk = usertag['user']['pk']
            if user_ig_pk:
                usertags.append(user_ig_pk)

        obj.hashtags = extract_hashtags(media.get('caption_text', None))
        hashtags = list()
        if obj.hashtags:
            for tag_name in obj.hashtags:
                hashtags.append(HashTag.from_name(tag_name))

        return obj, user, location, resources, usertags, hashtags


class Resource(models.Model):
    ig_pk = models.CharField(blank=True, max_length=100, unique=True)
    video_url = models.URLField(max_length=1000, blank=True, null=True)
    thumbnail_url = models.URLField(max_length=1000, blank=True, null=True)
    media_type = models.CharField(blank=True, max_length=7, choices=[(v, v) for v in ["Photo", "Video"]])
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='resources')
    media_ig_pk = None

    update_keys = ['video_url', 'thumbnail_url', 'media_type', 'media']
    convert_keys = {'pk': 'ig_pk'}

    @classmethod
    def from_dict(cls, resource: dict, media: Media):
        obj = DictToObj.obj_from_dict(resource, cls, cls.convert_keys, list())
        obj.media = media
        obj.media_ig_pk = media.ig_pk
        return obj
