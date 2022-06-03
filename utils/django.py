from decimal import Decimal
from django.db import models
from django.utils import timezone
from datetime import datetime, date, timedelta, time


class DictToObj:
    field_map = {
        str: [models.CharField, models.TextField, models.URLField, models.SlugField, models.EmailField],
        bool: [models.BooleanField],
        int: [models.IntegerField, models.PositiveIntegerField, models.PositiveBigIntegerField,
              models.PositiveSmallIntegerField],
        float: [models.FloatField],
        Decimal: [models.DecimalField],
        date: [models.DateField],
        datetime: [models.DateTimeField],
        time: [models.TimeField],
        timedelta: [models.DurationField],
    }
    relationships = [models.OneToOneField, models.ForeignKey, models.ManyToManyField]

    @classmethod
    def field_type(cls, model_klass, field: str):
        return type(getattr(model_klass, field).field)

    @classmethod
    def null_processor(cls, model_klass, key: str, value):
        if value is not None and value:
            return value

        field_type = cls.field_type(model_klass, key)
        if field_type in cls.field_map[str]:
            return str()
        if field_type in cls.field_map[bool]:
            return bool(value)
        if field_type in cls.field_map[int] or field_type in cls.field_map[float] or \
                field_type in cls.field_map[Decimal]:
            return 0
        return None

    @classmethod
    def value_processor(cls, model_klass, key: str, value, extra_processors: dict[callable]):
        value = cls.null_processor(model_klass, key, value)
        if value is None or not value:
            return value

        field_type = cls.field_type(model_klass, key)
        if field_type == models.DateTimeField and isinstance(value, datetime):
            value = timezone.localtime(value)

        if field_type in cls.field_map[int]:
            if isinstance(value, float):
                value = int(value)
            elif isinstance(value, str) and value.isdigit():
                value = int(value)
            elif isinstance(value, int):
                pass
            else:
                return None

        if field_type in cls.field_map[float]:
            if isinstance(value, str) and value.replace('.', '').isdigit():
                value = float(value)
            elif isinstance(value, (float, int)):
                pass
            else:
                return None

        if field_type in cls.field_map[Decimal]:
            if isinstance(value, (int, float)):
                value = Decimal(value)
            elif isinstance(value, str) and value.replace('.', '').isdigit():
                value = Decimal(float(value))
            elif isinstance(value, Decimal):
                pass
            else:
                return None

        if extra_processors and key in extra_processors:
            processors = extra_processors[key]
            if not isinstance(processors, (list, tuple)):
                processors = [processors]
            for proc in processors:
                value = proc(value)

        return value

    @classmethod
    def obj_from_dict(cls, data: dict, model_klass, convert_keys: dict, exclude_keys: list,
                      extra_processors: dict[str, list[callable]] = None):
        extra_processors = list() if extra_processors is None else extra_processors

        obj = model_klass()
        for key in data:
            value = data[key]
            if key in exclude_keys:
                continue
            if key in convert_keys:
                key = convert_keys[key]
            value = cls.value_processor(model_klass, key, value, extra_processors)
            setattr(obj, key, value)

        return obj
