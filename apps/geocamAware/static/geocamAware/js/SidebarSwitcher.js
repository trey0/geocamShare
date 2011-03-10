// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.SidebarSwitcher = new Class(
{
    Extends: geocamAware.WidgetManager,

    initialize: function (domId) {
        this.domId = domId;
        this.setToGallery();

        geocamAware.bindEvent(geocamAware, this, "selectFeature");
        geocamAware.bindEvent(geocamAware, this, "unselectFeature");
        geocamAware.bindEvent(geocamAware, this, "notifyLoading");
        geocamAware.bindEvent(geocamAware, this, "updateFeatures");
        geocamAware.bindEvent(geocamAware, this, "setToFeatureDetail");
        geocamAware.bindEvent(geocamAware, this, "setToFeatureEdit");
    },

    selectFeature: function (feature) {
        this.setToFeatureDetail(feature);
    },
    
    unselectFeature: function (feature) {
        this.setToGallery();
    },

    notifyLoading: function () {
        this.setToGallery();
    },

    updateFeatures: function (newFeatures, diff) {
        // todo: if in detail view and selected feature is no longer
        // present, switch to gallery view
    },
    
    /**********************************************************************
     * state and helper functions
     **********************************************************************/

    domId: null,

    getDefaultFeature: function () {
        return geocamAware.featuresByUuidG[geocamAware.selectedFeatureUuid];
    },

    setToGallery: function () {
        this.setWidgetForDomId(this.domId,
                               geocamAware.GalleryWidget.factory);
    },

    setToFeatureDetail: function (feature) {
        if (feature == undefined) {
            feature = this.getDefaultFeature();
        }
        this.setWidgetForDomId(this.domId,
                               geocamAware.FeatureDetailWidget.factory,
                               [feature.uuid]);
    },

    setToFeatureEdit: function (feature) {
        if (feature == undefined) {
            feature = this.getDefaultFeature();
        }
        this.setWidgetForDomId(this.domId,
                               geocamAware.FeatureEditWidget.factory,
                               [feature.uuid]);
    }

});

geocamAware.SidebarSwitcher.factory = function (domId) {
    return new geocamAware.SidebarSwitcher(domId);
}
