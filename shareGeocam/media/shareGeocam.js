
// can override stuff from shareCore.js here

DATA_URL = SCRIPT_NAME + "/data/";

function getDirUrl(item) {
    return DATA_URL + item.dateText + "/" + item.owner + "/" + item.id + "/" + item.version + "/";
}

function getThumbnailUrl(item, width) {
    return getDirUrl(item) + "th" + width + ".jpg";
}

function getCaptionHtml(item) {
    /*
    return ''
	+ '<table>\n'
	+ '  <tr>\n'
	+ '    <td colspan="2">' + item.id + '&nbsp;&nbsp;</td>\n'
	+ '    <td colspan="2">' + item.timestamp + '</td>\n'
	+ '  </tr>\n'
	+ '  <tr>\n'
  	+ '    <td style="font-style: italic">Task:</td>\n'
	+ '    <td>' + TASK_CHOICES_DICT[item.task] + '</td>\n'
	+ '    <td style="font-style: italic">Params:</td>\n'
	+ '    <td>' + item.params + '</td>\n'
	+ '  </tr>\n'
	+ '  <tr>\n'
  	+ '    <td style="font-style: italic">Tags:</td>\n'
	+ '    <td colspan="3">' + 'not implemented yet' + '</td>\n'
	+ '  </tr>\n'
	+ '  <tr>\n'
  	+ '    <td colspan="4">Comments not implemented yet</td>\n'
	+ '  </tr>\n'
	+ '</table>\n';
    */
    return "this is a caption";
}

