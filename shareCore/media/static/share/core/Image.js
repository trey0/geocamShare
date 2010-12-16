// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.Image = new Class(
{
    Extends: geocamShare.core.PointFeature,

    getThumbnailUrl: function (width) {
        return geocamShare.core.getDirUrl(this) + "th" + width + ".jpg";
    },

    getSizePixels: function () {
        return this.sizePixels;
    },

    getCaptionHeading: function () {
        var heading = ''
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
            heading += '    <td>' + cardinal + ' ' + Math.floor(this.yaw) + '&deg; (ref. ' + ref + ')&nbsp;&nbsp;</td>\n';
        } else {
            heading += '    <td>(unknown)</td>\n'
        }
        heading += '  </tr>\n';
        
        return heading;
    }

});

