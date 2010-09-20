// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

// can override stuff from shareCore.js here

geocamShare.core.isImage = function (feature) {
    return feature.type == "Photo";
}

geocamShare.core.getDirUrl = function (feature) {
    ret = geocamShare.core.DATA_URL + feature.dateText + "/" + feature.author.userName + "/" + feature.uuid + "/" + feature.version + "/";
    return ret;
}

geocamShare.core.getThumbnailUrl = function (feature, width) {
    return geocamShare.core.getDirUrl(feature) + "th" + width + ".jpg";
}

geocamShare.core.getViewerUrl = function (feature) {
    var name = feature.name;
    if (name == "") {
        if (feature.type == "Photo") {
            name = "untitled.jpg";
        } else if (feature.type == "Track") {
            name = "untitled.json";
        } else {
            name = "untitled";
        }
    }
    return geocamShare.core.SCRIPT_NAME + feature.type.toLowerCase() + "/" + feature.uuid + "/" + feature.version + "/" + name;
}

geocamShare.core.getCaptionHtml = function (feature) {
    caption = ''
        + '<table>\n';

    // notes
    if (feature.notes == '') {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="2" style="font-size: 1.5em; color: #999;">(no notes)</td>\n'
            + '  </tr>\n';
    } else {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="2" style="font-size: 1.5em;">' + feature.notes + '</td>\n'
            + '  </tr>\n';
    }
    
    // tags
    caption += '  <tr>\n';
    if (feature.tags == '') {
        caption += '    <td colspan="2" style="color: #777">(no tags)</td>';
    } else {
        caption += '    <td colspan="2">';
        $.each(feature.tags,
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
        + '      <span style="color: #007; font-weight: bold; margin-right: 10px;">' + getTimeShort(feature.maxTime) + '</span>\n'
        + '      <span style="margin-right: 10px;">' + feature.author.displayName + '</span>\n'
        + '      <span>' + feature.name + '</span>\n'
        + '    </td>\n'
        + '  </tr>\n';

    // lat, lon
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">lat, lon</td>\n';
    if (feature.lat != null) {
        caption += '    <td>' + feature.lat.toFixed(6) + ', ' + feature.lon.toFixed(6) + '</td>\n';
    } else {
        caption += '    <td>(unknown)</td>\n';
    }
    caption += ''
        + '  </tr>\n';
    
    // usng
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">usng</td>\n';
    if (feature.lat != null) {
        caption += '    <td>' + LLtoUSNG(feature.lat, feature.lon, 5) + '&nbsp;&nbsp;</td>\n'
    } else {
        caption += '    <td>(unknown)</td>\n'
    }
    caption += '  </tr>\n';

    // heading
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">heading</td>\n'
    if (feature.yaw != null) {
        var cardinal = geocamShare.core.getHeadingCardinal(feature.yaw);
        caption += '    <td>' + cardinal + ' ' + Math.floor(feature.yaw) + '&nbsp;&nbsp;</td>\n';
    } else {
        caption += '    <td>(unknown)</td>\n'
    }
    caption += '  </tr>\n';

    // timePrecise
    caption += ''
        + '  <tr>\n'
        + '    <td class="captionHeader">time</td>\n'
        + '    <td>' + getTimePrecise(feature.maxTime) + '</td>\n'
        + '  </tr>\n';

    caption += '</table>\n';
    return caption;
}

