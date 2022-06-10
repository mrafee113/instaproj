import termcolor
import scrapy.loader

from typing import Iterable
from functools import partial
from types import GenericAlias
from itemloaders import unbound_method
from itemloaders.processors import Compose, TakeFirst


class TFCompose(Compose):
    """Uses TakeFirst as the first function."""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.functions = [TakeFirst()] + list(self.functions)


# todo: date outputs list
class ItemLoader(scrapy.loader.ItemLoader):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.__item_annotations = dict()

    @property
    def _item_annotations(self) -> dict[str, type]:
        if self.__item_annotations:
            return self.__item_annotations
        if not hasattr(self.item.__class__, '__annotations__'):
            print(termcolor.colored(
                f'item.__class__ of type={type(self.item)} did not have __annotations__. skipping.'))
            return self._item_annotations

        _ann: dict = self.item.__class__.__annotations__
        annotations = dict()
        for field_name, ann in _ann.items():
            if isinstance(ann, type) and not isinstance(ann, GenericAlias):
                annotations[field_name] = ann
            elif isinstance(ann, GenericAlias):
                if not hasattr(ann, '__origin__'):
                    print(termcolor.colored('annotation.__origin__ not found. skipping.', 'cyan'))
                    continue

                ann = ann.__origin__
                if isinstance(ann, type):
                    annotations[field_name] = ann
                    continue

                print(termcolor.colored('annotation.__origin__ was not an instance of type. skipping.', 'cyan'))

        self.__item_annotations = annotations
        return annotations

    def _flatten_fields(self, values: dict) -> dict:
        _values = dict()
        for field_name, value in values.items():
            if field_name in self._item_annotations:
                item_ann = self._item_annotations[field_name]
                if not issubclass(item_ann, Iterable) or item_ann == str:
                    print(f'flattened {field_name}:{item_ann}:{value}:{value[-1]}')
                    value = value[-1]
                _values[field_name] = value
            else:
                _values[field_name] = value

        return _values

    def get_output_processor(self, field_name):
        proc = getattr(self, '%s_out' % field_name, None)
        if not proc:
            proc = self._get_item_field_attr(
                field_name,
                'output_processor',
                partial(self.default_output_processor, field_name)
            )
        return unbound_method(proc)

    def typical_output_processor(self, field_name, value):
        if field_name not in self._item_annotations:
            return value

        item_ann = self._item_annotations[field_name]
        if not issubclass(item_ann, Iterable) or item_ann == str:
            value = value[-1]
        elif item_ann is set:
            value = set(value)

        return value

    default_output_processor = typical_output_processor
