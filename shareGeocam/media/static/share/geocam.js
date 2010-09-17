// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

// can override stuff from shareCore.js here

share.core.isImage = function (feature) {
    return feature.type == "Photo";
}

share.core.getDirUrl = function (feature) {
    ret = share.core.DATA_URL + feature.dateText + "/" + feature.author + "/" + feature.uuid + "/" + feature.version + "/";
    return ret;
}

share.core.getThumbnailUrl = function (feature, width) {
    return share.core.getDirUrl(feature) + "th" + width + ".jpg";
}

share.core.getViewerUrl = function (feature) {
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
    return share.core.SCRIPT_NAME + feature.type.toLowerCase() + "/" + feature.uuid + "/" + feature.version + "/" + name;
}

share.core.getCaptionHtml = function (feature) {
    var timeSummary;
    if (feature.type == "Track") {
        timeSummary = (getTimeShort(feature.minTime)
                       + " .. " + getTimeShort(feature.maxTime));
    } else {
        timeSummary = getTimeShort(feature.timestamp);
    }

    caption = ''
        + '<table>\n';
    if (feature.notes != '') {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="4" style="font-size: 1.5em;">' + feature.notes + '</td>\n'
            + '  </tr>\n';
    }
    caption += ''
        + '  <tr>\n'
        + '    <td colspan="2" style="color: #007; font-weight: bold;">' + feature.name + '&nbsp;&nbsp;</td>\n'
        + '    <td colspan="2" style="color: #777;">' + timeSummary + '</td>\n'
        + '  </tr>\n';
    if (feature.lat != null) {
        caption += ''
            + '  <tr>\n'
            + '    <td style="font-style: italic">Lat,Lon,Heading:&nbsp;&nbsp;</td>\n'
            + '    <td colspan="3">' + feature.lat.toFixed(6) + ', ' + feature.lon.toFixed(6) + ', ' + Math.floor(feature.yaw) + '&nbsp;&nbsp;</td>\n'
            + '  </tr>\n'
            + '  <tr>\n'
            + '    <td style="font-style: italic">USNG:</td>\n'
            + '    <td colspan="3">' + LLtoUSNG(feature.lat, feature.lon, 5) + '&nbsp;&nbsp;</td>\n'
            + '  </tr>\n';
    } else {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="4">(No position information)</td>\n'
            + '  </tr>\n';        
    }
    caption += ''
        + '  <tr>\n'
        + '    <td style="font-style: italic">User:</td>\n'
        + '    <td>' + feature.author + '</td>\n'
        + '    <td style="font-style: italic">Tags:</td>\n'
        + '    <td>' + feature.tags + '</td>\n'
        + '  </tr>\n'
        + '  <tr>\n'
        + '  </tr>\n'
        + '</table>\n';
    return caption;
}

