// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.geocam.Photo = new Class(
{
    Extends: geocamShare.core.Image,

    getCaptionUsng: function () {
        var usng = ''
            + '  <tr>\n'
            + '    <td class="captionHeader">usng</td>\n';
        if (this.latitude != null) {
            usng += '    <td>' + LLtoUSNG(this.latitude, this.longitude, 5) + '&nbsp;&nbsp;</td>\n'
        } else {
            usng += '    <td>(unknown)</td>\n'
        }
        usng += '  </tr>\n';
        
        return usng;
    },

    getCaptionLatLon: function () {
        var standardFormat = this.parent();
        var usngFormat = this.getCaptionUsng();
        return standardFormat + usngFormat;
    }
});
