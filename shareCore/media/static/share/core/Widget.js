// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.Widget = new Class(
{
    // functions to implement in derived classes
    
    initialize: function (domId) {
    },
    
    updateFeatures: function (oldFeatures, newFeatures, diff) {
    },
    
    notifyLoading: function () {
    },
    
    notifyFeaturesInMapViewport: function (visibleFeatures) {
    },
    
    highlightFeature: function (feature) {
    },
    
    unhighlightFeature: function (feature) {
    },
    
    selectFeature: function (feature) {
    },
    
    unselectFeature: function (feature) {
    }
    
});

