// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.MapViewer = new Class({
    Extends: geocamShare.core.Widget,

    isReady: false,
    
    initialize: function (domId) {
	// initialize the map
	this.isReady = true;
	geocamShare.core.setViewIfReady();
    },
    
    updateFeatures: function (oldFeatures, newFeatures, diff) {
	// add or delete features when we get an update
    },
    
    zoomToFit: function () {
	// zoom map bounds to fit all markers
    },
    
    getViewport: function () {
	// get viewport coords as a string, which will be stored in session state.
	// the format of the string can vary depending on the back end, but
	// calling setViewport() with the result must return the viewport to the
	// same place.
	return "";
    },
    
    setViewport: function (view) {
	// set viewport coords (see getViewport)
    },
    
    getVisibleFeatures: function (features) {
	// get the subset of features which are visible within the current map viewport
	return features;
    },

    getFeatureHasPosition: function (feature) {
        return (feature.latitude != null) || (feature.minLat != null);
    }
});

