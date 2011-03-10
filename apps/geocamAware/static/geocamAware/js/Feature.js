// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.Feature = new Class(
{

    initialize: function (opts) {
        $extend(this, opts);
    },

    getThumbSize: function (constraint) {
        /* return the right size of thumbnail to fit snugly in the
           constraint box, preserving the aspect ratio of the full size
           image */

        var full = this.getSizePixels();
        if ((constraint[0] / full[0]) < (constraint[1] / full[1])) {
            return [constraint[0],
                    Math.floor(constraint[0] / full[0] * full[1])];
        } else {
            return [Math.floor(constraint[1] / full[1] * full[0]),
                    constraint[1]];
        }
    },

    getDetailImageHtml: function () {
        var w0 = geocamAware.settings.GEOCAM_CORE_DESC_THUMB_SIZE[0];
        var thumbSize = this.getThumbSize(geocamAware.settings.GEOCAM_CORE_DESC_THUMB_SIZE);
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
            + '    width="' + thumbSize[0] + '"\n'
            + '    height="' + thumbSize[1] + '"\n'
            + '    border="0"'
            + '  />\n'
            + '</a>\n';
    },

    getFullResLinkHtml: function () {
        return ''
            + '  <div style="margin-top: 10px;"><a href="' + this.getViewerUrl() + '" target="_blank">\n'
            + '    View full-res image'
            + '  </a></div>\n'
    },

    getEditLinkHtml: function () {
        return ''
            + '  <div style="margin-top: 10px;">\n'
            + '    <a id="featureEditLink" href="' + this.getEditUrl() + '" target="_blank">\n'
            + '      Edit photo information'
            + '    </a>\n'
            + '  </div>\n';
    },

    getDetailLinksHtml: function () {
        return this.getFullResLinkHtml() + this.getEditLinkHtml();
    },

    getBalloonHtml: function () {
        return ''
            + '<div>\n'
            + '  ' + this.getDetailImageHtml()
            + '  ' + this.getCaptionHtml()
            + '  ' + this.getDetailLinksHtml()
            + '</div>\n';
    },
    
    getGalleryThumbHtml: function () {
        var w0 = geocamAware.settings.GEOCAM_CORE_GALLERY_THUMB_SIZE[0];
        var h0 = geocamAware.settings.GEOCAM_CORE_GALLERY_THUMB_SIZE[1];
        var galThumbSize = this.getThumbSize(geocamAware.settings.GEOCAM_CORE_GALLERY_THUMB_SIZE);
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
        return this.icon.url;
    },
    
    getIconMapUrl: function () {
        return this.pointIcon.url;
    },
    
    getIconMapRotUrl: function () {
        return this.rotatedIcon.url;
    },

    getCaptionNotes: function () {
        if (this.notes == null) {
            return ''
                + '  <tr>\n'
                + '    <td colspan="2" style="font-size: 1.5em; color: #999;">(no notes)</td>\n'
                + '  </tr>\n';
        } else {
            return ''
                + '  <tr>\n'
                + '    <td colspan="2" style="font-size: 1.5em;">' + this.notes + '</td>\n'
                + '  </tr>\n';
        }
    },
    
    getCaptionTags: function () {
        var tags = '  <tr>\n';
        if (this.tags == '') {
            tags += '    <td colspan="2" style="color: #777">(no tags)</td>';
        } else {
            tags += '    <td colspan="2">';
            $.each(this.tags,
                   function (i, tag) {
                       tags += '#' + tag + ' &nbsp;';
                   });
            tags += '    </td>\n';
        }
        tags += '  </tr>\n';
        
        return tags;
    },

    getCaptionMisc: function () {
        var maxTime = this.getMaxTime();
        
        // timeShort, author, name
        return ''
            + '  <tr>\n'
            + '    <td style="padding-top: 10px; padding-bottom: 10px;" colspan="2">'
            + '      <span style="color: #007; font-weight: bold; margin-right: 10px;">' + getTimeShort(maxTime) + '</span>\n'
            + '      <span style="margin-right: 10px;">' + this.author.displayName + '</span>\n'
            + '      <span>' + this.name + '</span>\n'
            + '    </td>\n'
            + '  </tr>\n';
    },

    getCaptionTimePrecise: function () {
        var maxTime = this.getMaxTime();
        return ''
            + '  <tr>\n'
            + '    <td class="captionHeader">time</td>\n'
            + '    <td>' + getTimePrecise(maxTime) + '</td>\n'
            + '  </tr>\n';
    },

    getCaptionHtml: function () {
        caption = ''
            + '<table>\n';
        
        caption += this.getCaptionNotes();
        caption += this.getCaptionTags();
        caption += this.getCaptionMisc(); // relative time, author, name
        if (this.getCaptionLatLon != null) {
            caption += this.getCaptionLatLon();
        }
        if (this.getCaptionAltitude != null) {
            caption += this.getCaptionAltitude();
        }
        if (this.getCaptionHeading != null) {
            caption += this.getCaptionHeading();
        }
        caption += this.getCaptionTimePrecise();
        
        caption += '</table>\n';
        return caption;
    }

});

