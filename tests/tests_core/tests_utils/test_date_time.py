import pytest

from datetime import datetime, timedelta, timezone

from core.utils.date_time import (DateTimeUtilsError, convert_timezone,
                                  datetime_to_str, tzstr_to_timedelta)


def test_tzstr_to_timedelta():

    result = tzstr_to_timedelta("00:00")
    assert result == timedelta(minutes=0)

    result = tzstr_to_timedelta("+01:00")
    assert result == timedelta(minutes=60)
    result = tzstr_to_timedelta("-01:00")
    assert result == timedelta(minutes=-60)

    result = tzstr_to_timedelta("01:30")
    assert result == timedelta(minutes=90)
    result = tzstr_to_timedelta("-01:30")
    assert result == timedelta(minutes=-90)


def test_tzstr_to_timedelta_wrong_hours_minutes():

    with pytest.raises(DateTimeUtilsError) as error:
        tzstr_to_timedelta("24:00")
    assert "24" in str(error)

    with pytest.raises(DateTimeUtilsError) as error:
        tzstr_to_timedelta("-24:00")
    assert "-24" in str(error)

    with pytest.raises(DateTimeUtilsError) as error:
        tzstr_to_timedelta("-00:60")
    assert "60" in str(error)

    with pytest.raises(DateTimeUtilsError) as error:
        tzstr_to_timedelta("00:-60")
    assert "-60" in str(error)


# Исходный dt без указания таймзоны
dt = datetime(2022, 4, 18, 21, 00)
# Исходный dt c указаним таймзоны
dt_with_ts = datetime(2022, 4, 18, 21, 0, tzinfo=timezone.utc)


def test_convert_timezone():

    # По умолчанию сконвертирует в utc0
    result = convert_timezone(dt)
    ex = datetime(2022, 4, 18, 21, 0, tzinfo=timezone.utc)
    assert result.isoformat() == ex.isoformat()
    result = convert_timezone(dt_with_ts)
    assert result.isoformat() == ex.isoformat()

    # Прибавим один час к таймзоне
    result = convert_timezone(dt, target_tz="01:00")
    ex = datetime(2022, 4, 18, 22, 0, tzinfo=timezone(timedelta(hours=1)))
    assert result.isoformat() == ex.isoformat()
    result = convert_timezone(dt_with_ts, "+01:00")
    assert result.isoformat() == ex.isoformat()

    # Отнимем один час и тридцать минут от таймзоны
    result = convert_timezone(dt, target_tz="-01:30")
    ex = datetime(2022, 4, 18, 19, 30, tzinfo=timezone(timedelta(minutes=-90)))
    assert result.isoformat() == ex.isoformat()
    result = convert_timezone(dt_with_ts, "-01:30")
    assert result.isoformat() == ex.isoformat()

    # Отнимем тридцать минут от таймзоны
    result = convert_timezone(dt, target_tz="-00:30")
    ex = datetime(2022, 4, 18, 20, 30, tzinfo=timezone(timedelta(minutes=-30)))
    assert result.isoformat() == ex.isoformat()
    result = convert_timezone(dt_with_ts, "-00:30")
    assert result.isoformat() == ex.isoformat()


def test_datetime_to_str():

    # По умолчанию сконвертирует в utc0, вернет в формате "%d-%m-%Y %H:%M:%S%z"
    result = datetime_to_str(dt)
    assert result == "2022-04-18T21:00:00+0000"
    result = datetime_to_str(dt_with_ts)
    assert result == "2022-04-18T21:00:00+0000"

    # Изменим формат
    result = datetime_to_str(dt, format="%d-%m-%Y %H:%M")
    assert result == "18-04-2022 21:00"

    # Изменим таймзону
    result = datetime_to_str(dt_with_ts, target_tz="+01:30")
    assert result == "2022-04-18T22:30:00+0130"
    result = datetime_to_str(dt_with_ts, "-00:30")
    assert result == "2022-04-18T20:30:00-0030"
