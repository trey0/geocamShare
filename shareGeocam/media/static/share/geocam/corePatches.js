// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.isImage = function (feature) {
    return feature.subtype == "Photo";
}

geocamShare.core.getDirUrl = function (feature) {
    ret = geocamShare.core.settings.DATA_URL + feature.subtype.toLowerCase() + '/';
    var idStr = feature.localId + 'p';
    for (var i = 0; i < idStr.length; i += 2) {
        if (i > 0) {
            ret += '/';
        }
        ret += idStr.substr(i, 2);
    }
    ret += "/" + feature.version + "/";
    return ret;
}

geocamShare.core.Feature.prototype.getViewerUrl = function () {
    var name = this.name;
    if (name == "") {
        if (this.subtype == "Photo") {
            name = "untitled.jpg";
        } else if (this.subtype == "Track") {
            name = "untitled.json";
        } else {
            name = "untitled";
        }
    }
    return geocamShare.core.settings.SCRIPT_NAME + this.subtype.toLowerCase() + "/" + this.localId + "/" + name;
}

geocamShare.core.Feature.prototype.getEditUrl = function (widget) {
    var verb;
    if (widget) {
        verb = 'editWidget';
    } else {
        verb = 'edit'
    }
    return geocamShare.core.settings.SCRIPT_NAME + verb + '/' + this.subtype.toLowerCase() + "/" + this.uuid + "/";
}

geocamShare.core.Feature.prototype.getCaptionHtml = function () {
    var timestamp;
    if (this.timestamp != null) {
        timestamp = this.timestamp;
    } else {
        timestamp = this.maxTime;
    }

    caption = ''
        + '<table>\n';

    // notes
    if (this.notes == null) {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="2" style="font-size: 1.5em; color: #999;">(no notes)</td>\n'
            + '  </tr>\n';
    } else {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="2" style="font-size: 1.5em;">' + this.notes + '</td>\n'
            + '  </tr>\n';
    }
    
    // tags
    caption += '  <tr>\n';
    if (this.tags == '') {
        caption += '    <td colspan="2" style="color: #777">(no tags)</td>';
    } else {
        caption += '    <td colspan="2">';
        $.each(this.tags,
               function (i, tag) {
                   caption += '#' + tag + ' &nbsp;';
               });
        caption += '    </td>\n';
    }
    caption += '  </tr>\n';

    // timeShort, author, filename
    caption += ''
        + '  <tr>\n'
        + '    <td style="padding-top: 10px; padding-bottom: 10px;" colspan="2">'
        + '      <span style="color: #007; font-weight: bold; margin-right: 10px;">' + getTimeShort(timestamp) + '</span>\n'
        + '      <span style="margin-right: 10px;">' + this.author.displayName + '</span>\n'
        + '      <span>' + this.name + '</span>\n'
        + '    </td>\n'
        + '  </tr>\n';

    // lat, lon
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">lat, lon</td>\n';
    if (this.latitude != null) {
        caption += '    <td>' + this.latitude.toFixed(6) + ', ' + this.longitude.toFixed(6) + '</td>\n';
    } else {
        caption += '    <td>(unknown)</td>\n';
    }
    caption += ''
        + '  </tr>\n';
    
    // usng
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">usng</td>\n';
    if (this.latitude != null) {
        caption += '    <td>' + LLtoUSNG(this.latitude, this.longitude, 5) + '&nbsp;&nbsp;</td>\n'
    } else {
        caption += '    <td>(unknown)</td>\n'
    }
    caption += '  </tr>\n';

    // altitude
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">altitude</td>\n';
    if (this.altitude != null) {
        var ref;
        if (this.altitudeRef == null) {
            ref = 'unknown';
        } else {
            ref = this.altitudeRef;
        }
        caption += '    <td>' + this.altitude + ' meters (ref. ' + ref + ')&nbsp;&nbsp;</td>\n'
    } else {
        caption += '    <td>(unknown)</td>\n'
    }
    caption += '  </tr>\n';

    // heading
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">heading</td>\n'
    if (this.yaw != null) {
        var cardinal = geocamShare.core.getHeadingCardinal(this.yaw);
        var ref;
        if (this.yawRef == null) {
            ref = 'unknown';
        } else {
            ref = this.yawRef;
        }
        caption += '    <td>' + cardinal + ' ' + Math.floor(this.yaw) + '&deg; (ref. ' + ref + ')&nbsp;&nbsp;</td>\n';
    } else {
        caption += '    <td>(unknown)</td>\n'
    }
    caption += '  </tr>\n';

    // timePrecise
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">time</td>\n'
        + '    <td>' + getTimePrecise(timestamp) + '</td>\n'
        + '  </tr>\n';

    caption += '</table>\n';
    return caption;
}

geocamShare.core.Photo = geocamShare.geocam.Photo;
