
// can override stuff from shareCore.js here

DATA_URL = SCRIPT_NAME + "/data/";

function getDirUrl(item) {
    return DATA_URL + item.dateText + "/" + item.owner + "/" + item.id + "/" + item.version + "/";
}

function getThumbnailUrl(item, width) {
    return getDirUrl(item) + "th" + width + ".jpg";
}

function getCaptionHtml(item) {
    return ''
	+ '<table>\n'
	+ '  <tr>\n'
	+ '    <td colspan="2">' + item.name + '&nbsp;&nbsp;</td>\n'
	+ '    <td colspan="2">' + item.timestamp + '</td>\n'
	+ '  </tr>\n'
	+ '  <tr>\n'
  	+ '    <td style="font-style: italic">User:</td>\n'
	+ '    <td>' + item.owner + '</td>\n'
	+ '    <td style="font-style: italic">Notes:</td>\n'
	+ '    <td>' + item.notes + '</td>\n'
	+ '  </tr>\n'
	+ '  <tr>\n'
  	+ '    <td style="font-style: italic">Tags:</td>\n'
	+ '    <td colspan="3">' + item.tags + '</td>\n'
	+ '  </tr>\n'
	+ '</table>\n';
}

