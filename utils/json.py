""" Модуль для работы с json.
"""
import datetime
import json
from uuid import UUID


class ServiceJSONEncoder(json.JSONEncoder):
    """ Кодирование данных в json.
    """
    def default(self, obj):
        """ Определяет правила для кодирования в json нестандартных данных.
        """
        if isinstance(obj, datetime.datetime):
            # Внимание! Порядок проверок - важен! Так как datetime
            # является потомком date
            date_time = obj.replace(microsecond=0)
            return str(date_time.isoformat())

        if isinstance(obj, (UUID, datetime.date)):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def json_dumps(data) -> str:
    """ Кодирование данных в json.
    """
    return json.dumps(data, cls=ServiceJSONEncoder, ensure_ascii=False)
