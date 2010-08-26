
// can override stuff from shareCore.js here

DATA_URL = SCRIPT_NAME + "/data/";

function isImage(item) {
    return item.type == "Photo";
}

function getDirUrl(item) {
    return DATA_URL + item.dateText + "/" + item.author + "/" + item.uuid + "/" + item.version + "/";
}

function getThumbnailUrl(item, width) {
    return getDirUrl(item) + "th" + width + ".jpg";
}

function getViewerUrl(item) {
    return SCRIPT_NAME + "/" + item.type + "/" + item.uuid + "/" + item.version + "/";
}

function getCaptionHtml(item) {
    var timeSummary;
    if (item.type == "Track") {
        timeSummary = (getTimeShort(item.minTime)
                       + " .. " + getTimeShort(item.maxTime));
    } else {
        timeSummary = getTimeShort(item.timestamp);
    }

    caption = ''
        + '<table>\n';
    if (item.notes != '') {
        caption += ''
            + '  <tr>\n'
            + '    <td colspan="4" style="font-size: 1.5em;">' + item.notes + '</td>\n'
            + '  </tr>\n';
    }
    caption += ''
        + '  <tr>\n'
        + '    <td colspan="2" style="color: #007; font-weight: bold;">' + item.name + '&nbsp;&nbsp;</td>\n'
        + '    <td colspan="2" style="color: #777;">' + timeSummary + '</td>\n'
        + '  </tr>\n';
    if (item.lat != null) {
        caption += ''
            + '  <tr>\n'
            + '    <td style="font-style: italic">Lat,Lon,Heading:&nbsp;&nbsp;</td>\n'
            + '    <td colspan="3">' + item.lat + ', ' + item.lon + ', ' + Math.floor(item.yaw) + '&nbsp;&nbsp;</td>\n'
            + '  </tr>\n'
            + '  <tr>\n'
            + '    <td style="font-style: italic">USNG:</td>\n'
            + '    <td colspan="3">' + LLtoUSNG(item.lat, item.lon, 5) + '&nbsp;&nbsp;</td>\n'
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
        + '    <td>' + item.author + '</td>\n'
        + '    <td style="font-style: italic">Tags:</td>\n'
        + '    <td>' + item.tags + '</td>\n'
        + '  </tr>\n'
        + '  <tr>\n'
        + '  </tr>\n'
        + '</table>\n';
    return caption;
}

