from datetime import datetime, timedelta, timezone


class DateTimeUtilsError(Exception):
    pass


def tzstr_to_timedelta(tz: str) -> timedelta:
    """ Конвертирует таймзону вида "+00:00" в timedelta и возвращает ее.

        :tz: Таймзона вида "+00:00"
    """
    sign = -1 if tz[0] == "-" else 1
    h, m = tz.split(":")

    hours, minutes = abs(int(h)), int(m)
    if hours > 23:
        raise DateTimeUtilsError(f"abs(hours) > 23 (hours={h})")
    if minutes > 59 or minutes < 0:
        msg = "minutes > 59 or minutes < 0"
        raise DateTimeUtilsError(f"{msg} (minutes={m})")

    all_minutes = (hours * 60 + minutes) * sign

    return timedelta(minutes=all_minutes)


def convert_timezone(dt: datetime, target_tz: str = "+00:00") -> datetime:
    """ Конвертирует datetime из одной таймзоны в другую и возвращает
        datetime в новой таймзоне с ее указанием.
        Если поступила datetime без таймзоны, то считается что она UTC0.

        :dt:        Дата и время. Если без таймзоны, то считается что она UTC0.
        :target_tz: Таймзона вида "+00:00"
    """
    if dt.utcoffset() is None:
        dt = dt.replace(tzinfo=timezone.utc)

    time_zone = timezone(tzstr_to_timedelta(target_tz))

    return dt.astimezone(time_zone)


def datetime_to_str(
    dt: datetime,
    target_tz: str = "+00:00",
    format: str = "%Y-%m-%dT%H:%M:%S%z",
) -> str:
    """ Возвращает строку с временем и датой в заданном формате.

        :dt:        Дата и время. Если без таймзоны, то считается что она UTC0.
        :target_tz: Таймзона вида "+00:00"
        :format:    Формат строки-результата.
    """
    return convert_timezone(dt, target_tz).strftime(format)
