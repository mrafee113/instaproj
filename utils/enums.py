import sys

from typing import Optional


class MediaTypes:
    """tuple: [0]: media_type, [1]: product_type"""
    PHOTO = 1, (None, 'feed')
    VIDEO = 2, ('feed',)
    IGTV = 2, ('igtv',)
    REEL = 2, ('clips',)
    ALBUM = 8, (None, 'carousel_container')

    @classmethod
    def items(cls):
        return [k for k in dir(cls) if k.isupper()
                and isinstance(getattr(cls, k), tuple) and len(getattr(cls, k)) == 2]

    @classmethod
    def decide_type(cls, media_type: int, product_type: Optional[str] = None) -> str:
        for item in cls.items():
            mt, pt = getattr(cls, item)
            if media_type == mt:
                if product_type in pt:
                    return item.lower()

        # fixme: temporary workaround
        if media_type == 1:
            return 'photo'
        if media_type == 8:
            return 'album'
        if media_type == 2:
            print(f'WARNING! new type of product_type. {media_type}:{product_type}', file=sys.stderr)
            
