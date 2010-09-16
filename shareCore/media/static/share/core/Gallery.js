// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

share.core.Gallery = new Class({
        Extends: share.core.Widget,

        highlightFeature: function (feature) {
            share.core.setPage(share.core.visibleFeaturesG, share.core.getFeaturePage(feature, share.core.visibleFeaturesG));
            $("td#" + feature.uuid + " div").css({backgroundColor: 'red'});
	
            $("#caption").html(share.core.getCaptionHtml(feature)); // add the rest of the preview data
        },

        unhighlightFeature: function (feature) {
            $("td#" + feature.uuid + " div").css({backgroundColor: ''});
	
            $("#caption").html('');
        },

        selectFeature: function (feature) {
            // currently a no-op
        },

        unselectFeature: function (feature) {
            // currently a no-op
        }

    });

share.core.Gallery.factory = function (domId) {
    return new share.core.Gallery(domId);
}
