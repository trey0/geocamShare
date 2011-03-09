// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamCore.StubMapViewer = new Class(
{
    Extends: geocamCore.MapViewer,

    domId: null,

    initialize: function (domId) {
        this.parent(domId);
        this.domId = domId;
    },

    selectFeature: function (feature) {
        $('#' + this.domId).html(feature.getBalloonHtml());
    },
    
    unselectFeature: function (feature) {
        // no-op
    }

});

geocamCore.StubMapViewer.factory = function (domId) {
    return new geocamCore.StubMapViewer(domId);
}
