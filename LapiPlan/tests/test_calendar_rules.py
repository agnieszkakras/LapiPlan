from datetime import date, timedelta
import pytest
from lapiplan.calendar_rules import (
    easter_sunday, holiday_map, holidays_between, weekend, calendar_window,
)

@pytest.mark.parametrize('year,expected',[(2026,date(2026,4,5)),(2027,date(2027,3,28)),(2030,date(2030,4,21)),(2036,date(2036,4,13))])
def test_easter(year,expected):
    assert easter_sunday(year)==expected


def test_poland_christmas_eve_and_movable():
    h=holiday_map(2026,'PL')
    assert date(2026,12,24) in h
    assert date(2026,6,4) in h  # Corpus Christi
    assert date(2026,5,24) in h  # Pentecost


def test_uk_regions_2027():
    ew=holiday_map(2027,'UK-EW','EN')
    sc=holiday_map(2027,'UK-SCT','EN')
    ni=holiday_map(2027,'UK-NIR','EN')
    assert date(2027,3,29) in ew and date(2027,3,29) in ni
    assert date(2027,3,29) not in sc
    assert date(2027,12,27) in ew and date(2027,12,28) in ew
    assert date(2027,11,30) in sc
    assert date(2027,7,12) in ni


def test_us_observed_cross_year():
    assert date(2027,6,18) in holiday_map(2027,'US','EN')
    assert date(2027,7,5) in holiday_map(2027,'US','EN')
    assert date(2027,12,31) in holiday_map(2028,'US','EN')
    assert date(2027,12,31) in holidays_between(date(2027,12,30),date(2028,1,2),'US')


def test_ten_years_all_regions_and_locales():
    start,end=calendar_window(date(2026,11,17))
    assert (start,end)==(date(2026,11,17),date(2036,11,17))
    assert weekend(date(2026,11,21)) and not weekend(date(2026,11,23))
    for region in ('PL','UK-EW','UK-SCT','UK-NIR','US'):
        for language in ('PL','EN'):
            dates=holidays_between(start,end,region,language)
            assert len(dates)>70
            assert all(start<=day<=end for day in dates)
            assert all(isinstance(label,str) and label for label in dates.values())


def test_invalid_region():
    with pytest.raises(ValueError):
        holiday_map(2028,'FR')
