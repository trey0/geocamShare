
// can override stuff from shareCore.js here

DATA_URL = SCRIPT_NAME + "/data/";

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

    return ''
        + '<table>\n'
        + '  <tr>\n'
        + '    <td colspan="2">' + item.name + '&nbsp;&nbsp;</td>\n'
        + '    <td colspan="2">' + timeSummary + '</td>\n'
        + '  </tr>\n'
        + '  <tr>\n'
        + '    <td style="font-style: italic">User:</td>\n'
        + '    <td>' + item.author + '</td>\n'
        + '    <td style="font-style: italic">Notes:</td>\n'
        + '    <td>' + item.notes + '</td>\n'
        + '  </tr>\n'
        + '  <tr>\n'
        + '    <td style="font-style: italic">Tags:</td>\n'
        + '    <td colspan="3">' + item.tags + '</td>\n'
        + '  </tr>\n'
        + '</table>\n';
}

