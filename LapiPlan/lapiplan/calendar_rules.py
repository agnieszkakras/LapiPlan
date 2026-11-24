"""Predictable public holidays for PL, UK regions and US federal calendar.

Calendar covers a rolling 10-year interval from app's current date. Rules
represent ordinary recurring public holidays; exceptional one-off declarations
or later changes to law require updating this module. Not a school term calendar.
"""
from __future__ import annotations
from datetime import date, timedelta
from functools import lru_cache

REGIONS = ("PL", "UK-EW", "UK-SCT", "UK-NIR", "US")


def easter_sunday(year: int) -> date:
    """Gregorian computus (Meeus/Jones/Butcher)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month, day = divmod(h + l - 7*m + 114, 31)
    return date(year, month, day+1)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday-first.weekday()) % 7 + 7*(n-1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month+1, 1)-timedelta(days=1)
    return last-timedelta(days=(last.weekday()-weekday) % 7)


def monday_substitute(day: date, occupied: set[date]) -> date:
    # UK's general substitute convention: next weekday not already assigned.
    proposed = day
    while proposed.weekday() >= 5 or proposed in occupied:
        proposed += timedelta(days=1)
    return proposed


def federal_observed(day: date) -> date:
    if day.weekday() == 5:
        return day-timedelta(days=1)
    if day.weekday() == 6:
        return day+timedelta(days=1)
    return day


@lru_cache(maxsize=256)
def holiday_map(year: int, region: str, language: str = "PL") -> dict[date, str]:
    """Date->localized public holiday. US returns federal observances.

    Christmas/New Year observed dates can fall in adjacent years, so callers
    combine year-1/year/year+1 and filter by requested date.
    """
    if region not in REGIONS:
        raise ValueError("Unsupported region")
    if language not in ("PL", "EN"):
        raise ValueError("Unsupported language")
    out: dict[date, str] = {}
    def add(d: date, pl: str, en: str):
        out[d] = pl if language == "PL" else en
    easter = easter_sunday(year)
    if region == "PL":
        fixed = [
            (1,1,"Nowy Rok","New Year's Day"),
            (1,6,"Trzech Króli","Epiphany"),
            (5,1,"Święto Pracy","Labour Day"),
            (5,3,"Święto Konstytucji 3 Maja","Constitution Day"),
            (8,15,"Wniebowzięcie NMP","Assumption Day"),
            (11,1,"Wszystkich Świętych","All Saints' Day"),
            (11,11,"Święto Niepodległości","Independence Day"),
            (12,24,"Wigilia Bożego Narodzenia","Christmas Eve"),
            (12,25,"Boże Narodzenie","Christmas Day"),
            (12,26,"Drugi dzień Bożego Narodzenia","Second Day of Christmas"),
        ]
        for month, day, pl, en in fixed:
            add(date(year,month,day),pl,en)
        for offset, pl, en in [
            (0,"Wielkanoc","Easter Sunday"),
            (1,"Poniedziałek Wielkanocny","Easter Monday"),
            (49,"Zesłanie Ducha Świętego","Pentecost Sunday"),
            (60,"Boże Ciało","Corpus Christi"),
        ]:
            add(easter+timedelta(days=offset),pl,en)
        return out

    if region.startswith("UK"):
        scotland = region == "UK-SCT"
        northern_ireland = region == "UK-NIR"
        def fixed_sub(month: int, day: int, pl: str, en: str):
            original = date(year,month,day)
            # Official substitute bank holiday usually replaces the weekend date.
            actual = monday_substitute(original,set(out))
            suffix = " (dzień zastępczy)" if language == "PL" else " (substitute day)"
            add(actual,pl+(suffix if actual != original else ""),en+(suffix if actual != original else ""))
        fixed_sub(1,1,"Nowy Rok","New Year's Day")
        if scotland:
            fixed_sub(1,2,"Drugi dzień Nowego Roku","2 January")
        if northern_ireland:
            fixed_sub(3,17,"Dzień św. Patryka","St Patrick's Day")
        add(easter-timedelta(days=2),"Wielki Piątek","Good Friday")
        if not scotland:
            add(easter+timedelta(days=1),"Poniedziałek Wielkanocny","Easter Monday")
        add(nth_weekday(year,5,0,1),"Wczesnomajowe święto bankowe","Early May bank holiday")
        add(last_weekday(year,5,0),"Wiosenne święto bankowe","Spring bank holiday")
        if northern_ireland:
            fixed_sub(7,12,"Bitwa nad Boyne","Battle of the Boyne")
        if scotland:
            add(nth_weekday(year,8,0,1),"Letnie święto bankowe","Summer bank holiday")
            fixed_sub(11,30,"Dzień św. Andrzeja","St Andrew's Day")
        else:
            add(last_weekday(year,8,0),"Letnie święto bankowe","Summer bank holiday")
        # Christmas and Boxing Day must use distinct observed dates.
        fixed_sub(12,25,"Boże Narodzenie","Christmas Day")
        fixed_sub(12,26,"Drugi dzień Bożego Narodzenia","Boxing Day")
        return out

    # United States: federal public holidays (not individual state holidays).
    def us_fixed(month: int, day: int, pl: str, en: str):
        original=date(year,month,day)
        observed=federal_observed(original)
        suffix_pl=" (dzień obserwowany)" if observed != original else ""
        suffix_en=" (observed)" if observed != original else ""
        add(observed,pl+suffix_pl,en+suffix_en)
    us_fixed(1,1,"Nowy Rok","New Year's Day")
    add(nth_weekday(year,1,0,3),"Dzień Martina Luthera Kinga","Martin Luther King Jr. Day")
    add(nth_weekday(year,2,0,3),"Urodziny Waszyngtona","Washington's Birthday")
    add(last_weekday(year,5,0),"Dzień Pamięci","Memorial Day")
    us_fixed(6,19,"Juneteenth","Juneteenth")
    us_fixed(7,4,"Dzień Niepodległości","Independence Day")
    add(nth_weekday(year,9,0,1),"Święto Pracy","Labor Day")
    add(nth_weekday(year,10,0,2),"Dzień Kolumba","Columbus Day")
    us_fixed(11,11,"Dzień Weteranów","Veterans Day")
    add(nth_weekday(year,11,3,4),"Święto Dziękczynienia","Thanksgiving Day")
    us_fixed(12,25,"Boże Narodzenie","Christmas Day")
    return out


def holidays_between(start: date, end: date, region: str, language: str = "PL") -> dict[date,str]:
    if end < start:
        raise ValueError("End before start")
    result={}
    for year in range(start.year-1,end.year+2):
        for day, label in holiday_map(year,region,language).items():
            if start <= day <= end:
                result[day]=label
    return dict(sorted(result.items()))


def calendar_window(today: date | None = None) -> tuple[date,date]:
    start=today or date.today()
    try:
        finish=start.replace(year=start.year+10)
    except ValueError:  # Feb 29 -> Feb 28
        finish=start.replace(year=start.year+10,day=28)
    return start, finish


def weekend(day: date) -> bool:
    return day.weekday() >= 5
