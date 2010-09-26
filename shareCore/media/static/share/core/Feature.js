// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.Feature = new Class(
{

    initialize: function (opts) {
        $extend(this, opts);
    },

    getDetailImageHtml: function () {
        var w0 = geocamShare.core.settings.DESC_THUMB_SIZE[0];
        var scale = geocamShare.core.settings.DESC_THUMB_SIZE[0] / geocamShare.core.settings.GALLERY_THUMB_SIZE[0];
        var galThumbSize = this.getThumbSize();
        var tw = galThumbSize[0];
        var th = galThumbSize[1];
        return ''
            + '<a href="' + this.getViewerUrl() + '"\n'
            + '   target="_blank"\n'
            + '   title="View full-res image">\n'
	    + '  <img'
	    + '    src="' + this.getIconGalleryUrl()  + '"'
	    + '    width="32"'
	    + '    height="32"'
	    + '    style="border-width: 0px; position: absolute; z-index: 100;"'
	    + '  />'
            + '  <img\n'
            + '    src="' + this.getThumbnailUrl(w0) + '"\n'
            + '    width="' + tw*scale + '"\n'
            + '    height="' + th*scale + '"\n'
            + '    border="0"'
            + '  />\n'
            + '</a>\n';
    },

    getBalloonHtml: function () {
        return ''
            + '<div>\n'
            + '  ' + this.getDetailImageHtml()
            + '  ' + this.getCaptionHtml()
            + '  <div style="margin-top: 10px;"><a href="' + this.getViewerUrl() + '" target="_blank">\n'
            + '    View full-res image'
            + '  </a></div>\n'
            + '  <div style="margin-top: 10px;"><a id="featureEditLink" href="' + this.getEditUrl() + '" target="_blank">\n'
            + '    Edit photo information'
            + '  </a></div>\n'
            + '</div>\n';
    },
    
    getGalleryThumbHtml: function () {
        var w0 = geocamShare.core.settings.GALLERY_THUMB_SIZE[0];
        var h0 = geocamShare.core.settings.GALLERY_THUMB_SIZE[1];
        var galThumbSize = this.getThumbSize();
        var tw = galThumbSize[0];
        var th = galThumbSize[1];
        return "<td"
	    + " id=\"" + this.uuid + "\""
	    + " style=\""
	    + " vertical-align: top;"
	    + " width: " + (w0+10) + "px;"
	    + " height: " + (h0+10) + "px;"
	    + " margin: 0px 0px 0px 0px;"
	    + " border: 0px 0px 0px 0px;"
	    + " padding: 0px 0px 0px 0px;"
	    + "\">"
	    + "<div"
	    + " style=\""
	    + " width: " + tw + "px;"
	    + " height: " + th + "px;"
	    + " margin: 0px 0px 0px 0px;"
	    + " border: 0px 0px 0px 0px;"
	    + " padding: 5px 5px 5px 5px;"
	    + "\">"
	    + "<img"
	    + " src=\"" + this.getIconGalleryUrl()  + "\""
	    + " width=\"16\""
	    + " height=\"16\""
	    + " style=\"position: absolute; z-index: 100;\""
	    + "/>"
	    + "<img"
	    + " src=\"" + this.getThumbnailUrl(w0) + "\""
	    + " width=\"" + tw + "\""
	    + " height=\"" + th + "\""
	    + "/>"
	    + "</div>"
	    + "</td>";
    },
    
    getIconGalleryUrl: function () {
        return geocamShare.core.settings.MEDIA_URL + 'share/map/' + this.icon.name + '.png';
    },
    
    getIconMapUrl: function () {
        return geocamShare.core.settings.MEDIA_URL + 'share/map/' + this.icon.name + 'Point.png';
    },
    
    getIconMapRotUrl: function () {
        return geocamShare.core.settings.MEDIA_URL + 'share/mapr/' + this.rotatedIcon.name + '.png';
    }

    
});

