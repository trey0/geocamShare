// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.PointFeature = new Class(
{
    Extends: geocamShare.core.Feature,

    getKml: function () {
        var iconUrl = geocamShare.core.getHostUrl() + this.getIconMapUrl();
        return ''
	    + '<Placemark id="' + this.uuid + '">\n'
	    + '  <Style>\n'
	    + '    <IconStyle>\n'
	    + '      <Icon>\n'
	    + '        <href>' + iconUrl + '</href>\n'
	    + '      </Icon>\n'
	    + '      <heading>' + this.yaw + '</heading>\n'
	    + '    </IconStyle>\n'
	    + '  </Style>\n'
	    + '  <Point>\n'
	    + '    <coordinates>' + this.longitude + ',' + this.latitude + '</coordinates>\n'
	    + '  </Point>\n'
	    + '</Placemark>\n';
    }

});

