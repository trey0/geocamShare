# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import time, datetime, calendar, sys
import re
import iso8601

def localDateTimeToPosix(localDT):
    return time.mktime(localDT.timetuple()) + 1e-6*localDT.microsecond

def utcDateTimeToPosix(utcDT):
    return calendar.timegm(utcDT.timetuple()) + 1e-6*utcDT.microsecond

def posixToUtcDateTime(posixTime):
    return datetime.datetime.utcfromtimestamp(posixTime)

def posixToLocalDateTime(posixTime):
    return datetime.datetime.fromtimestamp(posixTime)
    

def localToUtcTime(localDT):
    """for the record, this is ridiculous"""
    posixTime = localDateTimeToPosix(localDT)
    utcDT = posixToUtcDateTime(posixTime)
    return utcDT

def utcToLocalTime(utcDT):
    """let's see how many time-related modules we can import"""
    posixTime = utcDateTimeToPosix(utcDT)
    localDT = posixToLocalDateTime(posixTime)
    return localDT

def utcNow():
    return posixToUtcDateTime(time.time())

def formatUtcTimeAsAbbreviatedLocalTime(utcDT):
    try:
        utcDT.timetuple()
    except AttributeError:
        return 'undated'
    localDT = utcToLocalTime(utcDT)
    now = datetime.datetime.now()
    if localDT.toordinal() == now.toordinal():
        # if today, leave off date
        return 'Today %s' % localDT.strftime('%H:%M')
    elif localDT.toordinal() == now.toordinal()-1:
        # if yesterday, express date as 'Yesterday'
        return 'Yesterday %s' % localDT.strftime('%H:%M')
    elif localDT.year == now.year:
        # if same year, express date as 'Tue Jan 01'
        return localDT.strftime('%a %b %d %H:%M')
    else:
        # if different year, express date as '2007 Jan 01'
        return localDT.strftime('%Y %b %d %H:%M')

def parse0(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d-%H:%M')
    except ValueError:
        return None

def stringToLocalDT(s, intervalStart=True, now=None):
    """Converts @s to corresponding local datetime.  Legal string
    formats are .  If string specifies only high-order fields (year or
    year/month/day), return start or end of interval if @intervalStart
    is True or False, respectively.  If string specifies only low-order
    fields (month/day/time or time), fill in high-order fields with
    values from @now.  If @now is not specified, it defaults to the
    current time.'"""

    if now == None:
        now = datetime.datetime.now()
    strftime = datetime.datetime.strftime
    bigDefaults = now
    if intervalStart:
        # 1901 is min valid value for strftime
        littleDefaults = datetime.datetime.min.replace(year = 1901)
    else:
        littleDefaults = datetime.datetime.max

    # YYYY-mm-dd-HH:MM
    result = parse0(s)
    if result:
        return result

    # mm-dd-HH:MM
    full = '%s-%s' % (strftime(bigDefaults, '%Y'), s)
    result = parse0(full)
    if result:
        return result

    # HH:MM
    full = '%s-%s' % (strftime(bigDefaults, '%Y-%m-%d'), s)
    result = parse0(full)
    if result:
        return result

    # YYYY-mm-dd
    full = '%s-%s' % (s, strftime(littleDefaults, '%H:%M'))
    result = parse0(full)
    if result:
        return result

    # YYYY
    full = '%s-%s' % (s, strftime(littleDefaults, '%m-%d-%H:%M'))
    result = parse0(full)
    if result:
        return result

    raise ValueError("times must be formatted as YYYY-mm-dd-HH:MM, mm-dd-HH:MM, HH:MM, YYYY-mm-dd, or YYYY")

def stringToUtcDT(s, intervalStart=True, now=None):
    return localToUtcTime(stringToLocalDT(s, intervalStart, now))

def equalUpToSeconds(a, b):
    return (a.replace(second=0, microsecond=0)
            == b.replace(second=0, microsecond=0))

def parseCsvTime(timeStr):
    '''Parse times GeoCam Share 2009 placed in export CSV files.  The
    same format was used in the upload form by GeoCam Mobile 2009'''
    # strip microseconds if present
    timeStr = re.sub(r'\.\d+$', '', timeStr)
    return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S')

def parseUploadTime(timeStr):
    try:
        # format used by GeoCam Mobile 2009
        return parseCsvTime(timeStr)
    except ValueError:
        pass

    try:
        # ISO 8601 format we should probably use in the future
        return iso8601.parse_date(timeStr)
    except iso8601.ParseError:
        pass

    try:
        # POSIX time stamp may be easier to produce for some clients
        posixTimeStamp = float(timeStr)
    except ValueError:
        pass
    else:
        return datetime.datetime.fromtimestamp(posixTimeStamp)

    # hm, nothing worked
    raise ValueError('could not parse datetime from %s' % timeStr)

def testCase(input, now, intervalStart, correct):
    nowDT = datetime.datetime.strptime(now, '%Y-%m-%d-%H:%M')
    correctDT = datetime.datetime.strptime(correct, '%Y-%m-%d-%H:%M')
    resultDT = parseDateTimeString(input, intervalStart, nowDT)
    assert equalUpToSeconds(resultDT, correctDT)

def test():
    testCase(input = '2009-2-4-9:48',
             now = '2009-02-04-09:48',
             intervalStart = True,
             correct = '2009-02-04-09:48')
    testCase(input = '2-4-9:48',
             now = '2009-02-04-09:48',
             intervalStart = True,
             correct = '2009-02-04-09:48')
    testCase(input = '9:48',
             now = '2009-02-04-09:48',
             intervalStart = True,
             correct = '2009-02-04-09:48')

    testCase(input = '2009-2-4',
             now = '2009-02-04-09:48',
             intervalStart = True,
             correct = '2009-02-04-00:00')
    testCase(input = '2009-2-4',
             now = '2009-02-04-09:48',
             intervalStart = False,
             correct = '2009-02-04-23:59')

    testCase(input = '2009',
             now = '2009-02-04-09:48',
             intervalStart = True,
             correct = '2009-01-01-00:00')
    testCase(input = '2009',
             now = '2009-02-04-09:48',
             intervalStart = False,
             correct = '2009-12-31-23:59')

