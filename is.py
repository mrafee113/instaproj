from instagrapi import Client
from django.conf import settings

# todo: fork instagrapi
#  when data is collected in _*_cache within Mixin objects,
#   add a added_datetime value to keep account of the time data was last evaluated.
#  also, define multiple timers on which you can base timeouts of added_datetime.
#  also, when loading data, have a timedelta, after which objects should be removed from cache.
#  also, add pickle.dump and pickle.load to these _*_cache objects to keep them persistent.
#  if data is too big, consider redis.

cl = Client()
cl.login(settings.IG_USER, settings.IG_PASS)

user_id = cl.user_id_from_username('tmehdirafee')
medias = cl.user_medias(user_id, 20)  # noqa



"""
class Client:
    # media
    media_id(media_pk: int) -> str
    media_pk(media_id: str) -> int
    media_pk_from_code(code: str) -> int
    media_pk_from_url(url: str) -> int
    user_medias(user_id: int, amount: int = 20) -> List[Media]
    media_info(media_pk: int) -> Media
    media_oembed(url: str) -> MediaOembed
    media_likers(media_id: str) -> List[ShortUser]
    
    # download  # filename = "{username}_{media_pk}"
    clip_download(media_pk: int, folder: Path)
    clip_download_by_url(url: str, filename: str, folder)
    video_download(media_pk)
    video_download_by_url(url, filename, folder)
    album_download(media_pk, folder)
    album_download_by_urls(urls, folder)
    igtv_download(media_pk, folder)
    igtv_download_by_url(url, filename, folder)
    photo_download(media_pk, folder)
    photo_download_by_url(url, filename, folder)
    story_download(story_pk, filename, folder)
    story_download(url, filename, folder)
    
    # user
    user_followers(user_id: int, amount: int = 0) -> dict[int, UserShort]
    user_following(user_id: int, amount: int = 0) -> dict[int, UserShort]
    search_followers(user_id: int, query: str) -> list[UserShort]
    search_following(user_id: int, query: str) -> list[UserShort]
    user_info(user_id: int) -> User
    user_info_by_username(username: str) -> User
    user_id_from_username(username: str) -> int
    username_from_user_id(user_id: int) -> str
    
    # location
    location_search(lat: float, lng: float) -> list[Location]
    location_medias_top(location_pk: int, amount: int = 9) -> list[Media]
    location_medias_recent(location_pk: int, amount: int = 24) -> list[Media]
    location_complete(location: Location) -> Location  # use when you have location info but not pk
    fbsearch_places(query: str, lat: float = 40.74, lng: float = -73.94) -> list[Location]
    location_info(location_pk: int) -> Location

    # tags
    hashtag_info(name: str) -> Hashtag
    hashtag_related_hashtags(name: str) -> List[Hashtags]  # raises Exception (BUG)
    hashtag_medias_top(name: str, amount: int = 9) -> List[Media]
    hashtag_medias_recent(name: str, amount: int = 27) -> List[Media]
    
    # comment
    media_comments(media_id: str, amount: int = 0) -> List[Comment]
    
    # highlight
    highlight_pk_from_url(url: str) -> Highlight
    highlight_info(highlight_pk: int) -> Highlight
    user_highlights(user_id: int, amount: int = 0) -> List[Highlight]
    
    # story
    user_stories(user_id: int, amount: int = None) -> List[Story]
    story_info(story_pk: int, use_cache: bool = True) -> Story
    story_pk_from_url(url: str) -> int
    
    # insight
    insights_media_feed_all(post_type: str = "ALL", time_frame: str = "TWO_YEARS",
                            data_ordering: str = "REACH_COUNT", count: int = 0, sleep: int = 2)
                            -> List[dict]
    insights_media(media_pk: int)
    

class Media:
    media_id: str - "{media_id}_{user_id}", e.g. "2277033926878261772_1903424587"
    media_pk: int - (real media id), e.g. 2277033926878261772
    code: str - Short code (slug for media), e.g. BjNLpA1AhXM from "https://www.instagram.com/p/BjNLpA1AhXM/"
    title: Optional[str]
    caption_text: str
    user: UserShort
    url: str - e.g. "https://www.instagram.com/p/BjNLpA1AhXM/"
    video_url: Optional[HttpUrl]  # for video and igtv
    media_type: int
    product_type: Optional[str]
    taken_at: datetime
    location: Optional[Location]
    comment_count: Optional[int] = 0
    like_count: int
    view_count: Optional[int] = 0  # for video and igtv
    usertags: List[UserTag]
    video_duration: Optional[float] = 0.0  # for video and igtv
    resources: List[Resource] = []
    clips_metadata: dict = {}

class MediaOembed:
    title: str
    author_name: str
    author_url: str
    author_id: str
    media_id: str
    provider_name: str
    provider_url: HttpUrl
    type: str
    width: Optional[int] = None
    height: Optional[int] = None
    html = str
    thumbnail_url: HttpUrl
    thumbnail_width: int
    thumbnail_height: int
    can_view: bool

class Location:
    [example]
    'pk': 260916528,
    'name': 'Foros, Crimea',
    'address': '',
    'lng': 33.7878,
    'lat': 44.3914,
    'external_id': 181364832764479,
    'external_id_source': 'facebook_places'
    website: Optional[str] = ""
    hours: Optional[dict] = {}
    city: Optional[str] = "'
    zip = Optional[str] = ""

class Resources:  # for albums
    [example[list]]
    [{'pk': 1787135361353462176,
    'video_url': HttpUrl('https://scontent-hel3-1.cdninstagram.com/v/t50.2886-16/33464086_3755...0e2362', scheme='https', ...),
    'thumbnail_url': HttpUrl('https://scontent-hel3-1.cdninstagram.com/v/t51.2885-15/e35/3220311...AE7332', scheme='https', ...),
    'media_type': 2},
   {'pk': 1787135762219834098,
    'video_url': HttpUrl('https://scontent-hel3-1.cdninstagram.com/v/t50.2886-16/32895...61320_n.mp4', scheme='https', ...),
    'thumbnail_url': HttpUrl('https://scontent-hel3-1.cdninstagram.com/v/t51.2885-15/e35/3373413....8480_n.jpg', scheme='https', ...),
    'media_type': 2},
   {'pk': 1787133803186894424,
    'video_url': None,
    'thumbnail_url': HttpUrl('https://scontent-hel3-1.cdninstagram.com/v/t51.2885-15/e35/324307712_n.jpg...', scheme='https', ...),
    'media_type': 1}]

class UserShort:
    pk: str
    username: Optional[str]
    full_name: Optional[str] = ""
    profile_pic_url: Optional[HttpsUrl]
    profile_pic_url_hd: Optional[HttpUrl]
    is_private: Optional[bool]
    stories: List = []

class User:
    pk: str  # aka user_id
    username: str
    full_name: str
    is_private: str
    profile_pic_url: HttpUrl
    profile_pic_url_hd: Optional[HttpUrl]
    is_verified: bool
    media_count: int
    follower_count: int
    following_count: int
    biography: Optional[str]
    external_url: Optional[str]
    account_type: Optional[int]  # todo
    
    is_business: bool
    public_email: Optional[str]
    contact_phone_number: Optional[str]
    public_phone_country_code: Optional[str]
    public_phone_number: Optional[str]
    business_contact_method: Optional[str]
    business_category_name: Optional[str]
    category_name: Optional[str]
    category: Optional[str]
    
    address_street: Optional[str]
    city_id: Optional[str]
    city_name: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    zip: Optional[str]
    instagram_location_id: Optional[str]

class HashTag:
    id: str
    name: str
    media_count: Optional[int]
    profile_pic_url: Optional[HttpUrl]

class Comment:
    pk: str
    text: str
    user: UserShort
    created_at_utc: datetime
    content_type: str
    status: str
    like_count: Optional[int]

class Highlight:
    pk: str  # 17895485401104052
    id: str  # highlight:17895485401104052
    latest_reel_media: int  # fixme: wtf is this?
    cover_media: int
    user: UserShort
    title: str
    created_at: datetime
    is_pinned_highlight: bool
    media_count: int
    media_ids: List[int] = []
    items: List[Story] = []
"""

"""story classes
class StoryMention:
    user: UserShort
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]

class StoryMedia:
    # Instagram does not return the feed_media object when requesting story,
    # so you will have to make an additional request to get media and this is overhead:
    # media: Media
    x: float = 0.5
    y: float = 0.4997396
    z: float = 0
    width: float = 0.8
    height: float = 0.60572916
    rotation: float = 0.0
    is_pinned: Optional[bool]
    is_hidden: Optional[bool]
    is_sticker: Optional[bool]
    is_fb_sticker: Optional[bool]
    media_pk: int
    user_id: Optional[int]
    product_type: Optional[str]
    media_code: Optional[str]

class StoryHashtag:
    hashtag: Hashtag
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]

class StoryLocation:
    location: Location
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]

class StorySticker:
    id: Optional[str]
    type: Optional[str] = 'gif'
    x: float
    y: float
    z: Optional[int] = 1000005
    width: float
    height: float
    rotation: Optional[float] = 0.0
    extra: Optional[dict] = {}

class StoryBuild:
    mentions: List[StoryMention]
    path: FilePath
    paths: List[FilePath] = []
    stickers: List[StorySticker] = []

class StoryLink:
    webUri: HttpUrl
    x: float = 0.5126011
    y: float = 0.5168225
    z: float = 0.0
    width: float = 0.50998676
    height: float = 0.25875
    rotation: float = 0.0

class Story:
    pk: str
    id: str
    code: str
    taken_at: datetime
    media_type: int
    product_type: Optional[str] = ""
    thumbnail_url: Optional[HttpUrl]
    user: UserShort
    video_url: Optional[HttpUrl]  # for Video and IGTV
    video_duration: Optional[float] = 0.0  # for Video and IGTV
    mentions: List[StoryMention]
    links: List[StoryLink]
    hashtags: List[StoryHashtag]
    locations: List[StoryLocation]
    stickers: List[StorySticker]
    medias: List[StoryMedia] = []

class MediaInsight:
    id: str
    creation_time: int  # timestamp
    instagram_media_id: str
    instagram_media_owner_id: str  # user
    instagram_media_type: str  # choices: [ "ALL", "CAROUSEL_V2", "IMAGE", "SHOPPING", "VIDEO" ]
    comment_count: int
    like_count: int
    save_count: int (probably None)
"""
