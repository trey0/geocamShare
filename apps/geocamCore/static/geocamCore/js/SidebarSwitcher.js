// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamCore.SidebarSwitcher = new Class(
{
    Extends: geocamCore.WidgetManager,

    initialize: function (domId) {
        this.domId = domId;
        this.setToGallery();

        geocamCore.bindEvent(geocamCore, this, "selectFeature");
        geocamCore.bindEvent(geocamCore, this, "unselectFeature");
        geocamCore.bindEvent(geocamCore, this, "notifyLoading");
        geocamCore.bindEvent(geocamCore, this, "updateFeatures");
        geocamCore.bindEvent(geocamCore, this, "setToFeatureDetail");
        geocamCore.bindEvent(geocamCore, this, "setToFeatureEdit");
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
        return geocamCore.featuresByUuidG[geocamCore.selectedFeatureUuid];
    },

    setToGallery: function () {
        this.setWidgetForDomId(this.domId,
                               geocamCore.GalleryWidget.factory);
    },

    setToFeatureDetail: function (feature) {
        if (feature == undefined) {
            feature = this.getDefaultFeature();
        }
        this.setWidgetForDomId(this.domId,
                               geocamCore.FeatureDetailWidget.factory,
                               [feature.uuid]);
    },

    setToFeatureEdit: function (feature) {
        if (feature == undefined) {
            feature = this.getDefaultFeature();
        }
        this.setWidgetForDomId(this.domId,
                               geocamCore.FeatureEditWidget.factory,
                               [feature.uuid]);
    }

});

geocamCore.SidebarSwitcher.factory = function (domId) {
    return new geocamCore.SidebarSwitcher(domId);
}
