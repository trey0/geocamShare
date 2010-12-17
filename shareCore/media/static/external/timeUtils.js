// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

/**********************************************************************
 * From "Dan's Network"
 **********************************************************************/

/* Blog post contents: In need of a JavaScript function that would parse
 * an ISO8601 compliant date, I came across an attempt
 * (http://delete.me.uk/2005/03/iso8601.html) and rewrote it (because
 * I'm all about reinventing the wheel). My function extends the Date
 * object and allows you to pass in an ISO8601 date
 * (2008-11-01T20:39:57.78-06:00). The function will then return the
 * Date. In the date string argument the dashes and colons are
 * optional. The decimal point for milliseconds is mandatory (although
 * specifying milliseconds t). If a timezone offset sign must be
 * included. This function should also work with iCalendar(RFC2445)
 * formatted dates. If a the date string t match the format, there will
 * be a final attempt to parse it with the built in Date.parse()
 * method.
 *
 * http://dansnetwork.com/2008/11/01/javascript-iso8601rfc3339-date-parser/
 */

// Lightly modified to keep the time in the specified local time zone
// and store its UTC offset explicitly in the tzinfo and utcoffset
// fields, sort of like Python datetime. -Trey

Date.prototype.setIso8601 = function (dString) {
    var regexp = /(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))/;
    if (dString.toString().match(new RegExp(regexp))) {
        var d = dString.match(new RegExp(regexp));
        this.setDate(1);
        this.setFullYear(parseInt(d[1],10));
        this.setMonth(parseInt(d[3],10) - 1);
        this.setDate(parseInt(d[5],10));
        this.setHours(parseInt(d[7],10));
        this.setMinutes(parseInt(d[9],10));
        this.setSeconds(parseInt(d[11],10));
        if (d[12]) {
            this.setMilliseconds(parseFloat(d[12]) * 1000);
        } else {
            this.setMilliseconds(0);
        }
        if (d[13] == 'Z') {
            this.tzinfo = 'UTC';
            this.utcoffset = 0;
        } else {
            this.tzinfo = d[14] + d[15] + d[17];
            this.utcoffset = (d[15] * 60) + parseInt(d[17],10);
            this.utcoffset *= ((d[14] == '-') ? -1 : 1);
        }
    } else {
        this.setTime(Date.parse(dString));
    }
    return this;
};

/**********************************************************************
 * From Daniel Rench
 **********************************************************************/

// version 0.11 by Daniel Rench
// More information: http://dren.ch/strftime/
// This is public domain software

Number.prototype.pad =
    function (n,p) {
    var s = '' + this;
    p = p || '0';
    while (s.length < n) s = p + s;
    return s;
};

Date.prototype.months = [
                         'January', 'February', 'March', 'April', 'May', 'June', 'July',
                         'August', 'September', 'October', 'November', 'December'
                         ];
Date.prototype.weekdays = [
                           'Sunday', 'Monday', 'Tuesday', 'Wednesday',
                           'Thursday', 'Friday', 'Saturday'
                           ];
Date.prototype.dpm = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

Date.prototype.strftime_f = {
    A: function (d) { return d.weekdays[d.getDay()] },
    a: function (d) { return d.weekdays[d.getDay()].substring(0,3) },
    B: function (d) { return d.months[d.getMonth()] },
    b: function (d) { return d.months[d.getMonth()].substring(0,3) },
    C: function (d) { return Math.floor(d.getFullYear()/100); },
    c: function (d) { return d.toString() },
    D: function (d) {
        return d.strftime_f.m(d) + '/' +
        d.strftime_f.d(d) + '/' + d.strftime_f.y(d);
    },
    d: function (d) { return d.getDate().pad(2,'0') },
    e: function (d) { return d.getDate().pad(2,' ') },
    F: function (d) {
        return d.strftime_f.Y(d) + '-' + d.strftime_f.m(d) + '-' +
        d.strftime_f.d(d);
    },
    H: function (d) { return d.getHours().pad(2,'0') },
    I: function (d) { return ((d.getHours() % 12 || 12).pad(2)) },
    j: function (d) {
        var t = d.getDate();
        var m = d.getMonth() - 1;
        if (m > 1) {
            var y = d.getYear();
            if (((y % 100) == 0) && ((y % 400) == 0)) ++t;
            else if ((y % 4) == 0) ++t;
        }
        while (m > -1) t += d.dpm[m--];
        return t.pad(3,'0');
    },
    k: function (d) { return d.getHours().pad(2,' ') },
    l: function (d) { return ((d.getHours() % 12 || 12).pad(2,' ')) },
    M: function (d) { return d.getMinutes().pad(2,'0') },
    m: function (d) { return (d.getMonth()+1).pad(2,'0') },
    n: function (d) { return "\n" },
    p: function (d) { return (d.getHours() > 11) ? 'PM' : 'AM' },
    R: function (d) { return d.strftime_f.H(d) + ':' + d.strftime_f.M(d) },
    r: function (d) {
        return d.strftime_f.I(d) + ':' + d.strftime_f.M(d) + ':' +
        d.strftime_f.S(d) + ' ' + d.strftime_f.p(d);
    },
    S: function (d) { return d.getSeconds().pad(2,'0') },
    s: function (d) { return Math.floor(d.getTime()/1000) },
    T: function (d) {
        return d.strftime_f.H(d) + ':' + d.strftime_f.M(d) + ':' +
        d.strftime_f.S(d);
    },
    t: function (d) { return "\t" },
    /*U: function (d) { return false }, */
    u: function (d) { return(d.getDay() || 7) },
    /*V: function (d) { return false }, */
    v: function (d) {
        return d.strftime_f.e(d) + '-' + d.strftime_f.b(d) + '-' +
        d.strftime_f.Y(d);
    },
    /*W: function (d) { return false }, */
    w: function (d) { return d.getDay() },
    X: function (d) { return d.toTimeString() }, // wrong?
    x: function (d) { return d.toDateString() }, // wrong?
    Y: function (d) { return d.getFullYear() },
    y: function (d) { return (d.getYear() % 100).pad(2) },
    //Z: function (d) { return d.toString().match(/\((.+)\)$/)[1]; },
    //z: function (d) { return d.getTimezoneOffset() }, // wrong
    //z: function (d) { return d.toString().match(/\sGMT([+-]\d+)/)[1]; },
    '%': function (d) { return '%' }
};

Date.prototype.strftime_f['+'] = Date.prototype.strftime_f.c;
Date.prototype.strftime_f.h = Date.prototype.strftime_f.b;

Date.prototype.strftime =
    function (fmt) {
    var r = '';
    var n = 0;
    while(n < fmt.length) {
        var c = fmt.substring(n, n+1);
        if (c == '%') {
            c = fmt.substring(++n, n+1);
            r += (this.strftime_f[c]) ? this.strftime_f[c](this) : c;
        } else r += c;
        ++n;
    }
    return r;
};

/**********************************************************************
 * Our code
 **********************************************************************/

Date.prototype.isoformat = function () {
    var tzStr;
    if (this.utcoffset == 0) {
        tzStr = 'Z';
    } else {
        var posOffset, sign;
        if (this.utcoffset < 0) {
            sign = '-';
            posOffset = -this.utcoffset;
        } else {
            sign = '+';
            posOffset = this.utcoffset;
        }
        var mins = '' + posOffset % 60;
        if (mins.length == 1) {
            mins = '0' + mins;
        }
        var hours = '' + Math.floor(posOffset / 60);
        if (hours.length == 1) {
            hours = '0' + hours;
        }
        tzStr = sign + hours + mins;
    }
    return this.strftime("%Y-%m-%dT%H:%M:%S") + tzStr;
}

function getNowInTimestampLocalTime(timestamp) {
    var now = new Date();
    // convert now from browser local time to timestamp local time
    // (using '- -' because '+' gives string concatenation, ugh.)
    now.setTime(now - -60000 * (now.getTimezoneOffset() + timestamp.utcoffset));
    now.utcoffset = timestamp.utcoffset;
    return now;
}

// returns human-readable time in formats like:
//   Today 12:16 (-0700)
//   Yesterday 12:16 (-0700)
//   Mar  7 12:16 (-0700)
//   2009-05-07 12:16 (-0700)
function getTimePrecise(timestampStr) {
    var timestamp = new Date();
    timestamp.setIso8601(timestampStr);
    var now = getNowInTimestampLocalTime(timestamp);

    var dayStr;
    if (timestamp.getFullYear() == now.getFullYear()) {
        if (timestamp.getMonth() == now.getMonth() && timestamp.getDate() == now.getDate()) {
            dayStr = 'Today';
        } else if (timestamp.getMonth() == now.getMonth() && timestamp.getDate() == (now.getDate() - 1)) {
            dayStr = 'Yesterday';
        } else {
            dayStr = timestamp.strftime('%b %e');
        }
    } else {
        dayStr = timestamp.strftime('%Y-%m-%d');
    }
    //console.log('getReadableTime timestamp='+timestamp + ' ret='+ret);
    return dayStr + ' ' + timestamp.strftime('%H:%M') + ' (' + timestamp.tzinfo + ')';
}

function getTimeSince(timestampStr) {
    var timestamp = new Date();
    timestamp.setIso8601(timestampStr);
    var now = getNowInTimestampLocalTime(timestamp);
    return now - timestamp;
}

// returns human-readable time in formats like:
//   5 minutes ago
//   2 hours ago
//   3 days ago
//   Mar  7
//   2009-05-07
function getTimeShort(timestampStr) {
    var timestamp = new Date();
    timestamp.setIso8601(timestampStr);
    var now = getNowInTimestampLocalTime(timestamp);

    var diffMs = now - timestamp;
    var diffMins = diffMs / 60000;
    if (diffMins < 2) {
        return '1 minute ago';
    } else if (diffMins < 60) {
        return Math.floor(diffMins) + ' minutes ago';
    } else {
        var diffHours = diffMins / 60;
        if (diffHours < 2) {
            return '1 hour ago';
        } else if (diffHours < 24) {
            return Math.floor(diffHours) + ' hours ago';
        } else {
            // zero out times so difference in days is right
            timestamp.setHours(0);
            timestamp.setMinutes(0);
            timestamp.setSeconds(0);
            now.setHours(0);
            now.setMinutes(0);
            now.setSeconds(0);
            var diffDays = (now - timestamp)/(1000*60*60*24);
            if (diffDays < 2) {
                return 'Yesterday';
            } else if (diffDays < 5) {
                return Math.floor(diffDays) + ' days ago';
            } else if (timestamp.getFullYear() == now.getFullYear()) {
                return timestamp.strftime('%b %e');
            } else {
                return timestamp.strftime('%Y-%m-%d');
            }
        }
    }
}
