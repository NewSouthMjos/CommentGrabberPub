from datetime import datetime
import pytz
from django.utils.timezone import make_aware


def _converttime(dt_str, tz_str):
    dt = datetime.fromisoformat(dt_str)
    tz = pytz.timezone(tz_str)
    dt = tz.localize(dt)
    return dt


def _converttime2(dt_str, tz_str):
    dt = datetime.fromisoformat(dt_str)
    tz = pytz.timezone(tz_str)
    dt = make_aware(dt, tz)
    return dt


def get_localtime_posix_intervals(
    request_end_date, request_start_date, client_timezone
):
    """
    Возвращает кортеж posix-времени начала запрошенного дня и конца запрошенного дня
    с точки зрения клиента. Таймзона клиента должна находиться client_timezone
    """
    #print(f"for timezone {client_timezone}")
    enddayloctime = _converttime2(request_end_date, client_timezone)
    #print(f"enddayloctime: {enddayloctime}")
    enddayloctime = enddayloctime.replace(hour=23, minute=59, second=59)
    enddayloctime_posix = datetime.timestamp(enddayloctime)
    #print(f"start-day time:{enddayloctime}, posix: {enddayloctime_posix}")

    startdayloctime = _converttime2(request_start_date, client_timezone)
    startdayloctime = startdayloctime.replace(hour=0, minute=0, second=0)
    startdayloctime_posix = datetime.timestamp(startdayloctime)
    #print(f"end-day time:{startdayloctime}, posix: {startdayloctime_posix}")

    return (enddayloctime_posix, startdayloctime_posix)


if __name__ == "__main__":
    assert (1630695599, 1630609200) == get_localtime_posix_intervals(
        "2021-09-03", "2021-09-03", "Asia/Yekaterinburg"
    )
    assert (1630699199, 1630612800) == get_localtime_posix_intervals(
        "2021-09-03", "2021-09-03", "Europe/Samara"
    )
    assert (1609718399, 1609459200) == get_localtime_posix_intervals(
        "2021-01-03", "2021-01-01", "Etc/UTC"
    )
    assert (1514872799, 1514786400) == get_localtime_posix_intervals(
        "2018-01-01", "2018-01-01", "Etc/GMT+6"
    )
    assert (1456757999, 1456671600) == get_localtime_posix_intervals(
        "2016-02-29", "2016-02-29", "Asia/Seoul"
    )
    start_posix_interval, end_posix_interval = get_localtime_posix_intervals(
        "2016-03-01", "2016-02-29", "Asia/Yekaterinburg"
    )
    print(start_posix_interval - end_posix_interval)

    # a = datetime(2018, 1, 1, 0, 0, 0)
    # print(f'a: {a}')

    d = _converttime2("2018-01-01", "Europe/Samara")
    print(f"d: {d}")

    E = _converttime("2018-01-01", "Europe/Kirov")
    print(f"E: {E}")

    # b_posix = datetime.timestamp(b)
    # , posix: {b_posix}')
