import jdatetime
from django.db import models
from django.core.exceptions import ValidationError


class PersianDateField(models.DateField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return jdatetime.date.fromgregorian(date=value)
        except Exception:
            return value

    def to_python(self, value):
        if isinstance(value, jdatetime.date):
            return value
        if value is None:
            return value
        if isinstance(value, str):
            try:
                return jdatetime.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass
        return super().to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, jdatetime.date):
            return value.togregorian()
        if isinstance(value, str):
            try:
                return jdatetime.datetime.strptime(value, '%Y-%m-%d').date().togregorian()
            except ValueError:
                pass
        return super().get_prep_value(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is None:
            return ''
        if isinstance(value, jdatetime.date):
            return value.strftime('%Y-%m-%d')
        return value.strftime('%Y-%m-%d')


class PersianDateTimeField(models.DateTimeField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return jdatetime.datetime.fromgregorian(datetime=value)
        except Exception:
            return value

    def to_python(self, value):
        if isinstance(value, jdatetime.datetime):
            return value
        if value is None:
            return value
        if isinstance(value, str):
            try:
                return jdatetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        return super().to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, jdatetime.datetime):
            return value.togregorian()
        if isinstance(value, str):
            try:
                return jdatetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').togregorian()
            except ValueError:
                pass
        return super().get_prep_value(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is None:
            return ''
        if isinstance(value, jdatetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value.strftime('%Y-%m-%d %H:%M:%S')
