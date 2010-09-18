// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.SidebarSwitcher = new Class(
{
    Extends: geocamShare.core.WidgetManager,

    initialize: function (domId) {
        this.domId = domId;
        this.setToGallery();
    },

    selectFeature: function (feature) {
        this.setToFeatureDetailWidget(feature);
    },
    
    unselectFeature: function (feature) {
        this.setToGallery();
    },

    notifyLoading: function () {
        this.setToGallery();
        this.parent(); // pass event on to gallery
    },

    updateFeatures: function (oldFeatures, newFeatures, diff) {
        // todo: if in detail view and selected feature is no longer
        // present, switch to gallery view

        this.parent(); // pass event on to subwidget
    },
    
    /**********************************************************************
     * state and helper functions
     **********************************************************************/

    domId: null,

    setToGallery: function () {
        this.setWidgetForDomId(this.domId,
                               geocamShare.core.GalleryWidget.factory);
    },

    setToFeatureDetailWidget: function (feature) {
        this.setWidgetForDomId(this.domId,
                               geocamShare.core.FeatureDetailWidget.factory,
                               [feature.uuid]);
    }

});

geocamShare.core.SidebarSwitcher.factory = function (domId) {
    return new geocamShare.core.SidebarSwitcher(domId);
}
