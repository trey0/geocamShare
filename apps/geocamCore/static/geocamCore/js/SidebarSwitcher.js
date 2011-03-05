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

        geocamShare.core.bindEvent(geocamShare.core, this, "selectFeature");
        geocamShare.core.bindEvent(geocamShare.core, this, "unselectFeature");
        geocamShare.core.bindEvent(geocamShare.core, this, "notifyLoading");
        geocamShare.core.bindEvent(geocamShare.core, this, "updateFeatures");
        geocamShare.core.bindEvent(geocamShare.core, this, "setToFeatureDetail");
        geocamShare.core.bindEvent(geocamShare.core, this, "setToFeatureEdit");
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
        return geocamShare.core.featuresByUuidG[geocamShare.core.selectedFeatureUuid];
    },

    setToGallery: function () {
        this.setWidgetForDomId(this.domId,
                               geocamShare.core.GalleryWidget.factory);
    },

    setToFeatureDetail: function (feature) {
        if (feature == undefined) {
            feature = this.getDefaultFeature();
        }
        this.setWidgetForDomId(this.domId,
                               geocamShare.core.FeatureDetailWidget.factory,
                               [feature.uuid]);
    },

    setToFeatureEdit: function (feature) {
        if (feature == undefined) {
            feature = this.getDefaultFeature();
        }
        this.setWidgetForDomId(this.domId,
                               geocamShare.core.FeatureEditWidget.factory,
                               [feature.uuid]);
    }

});

geocamShare.core.SidebarSwitcher.factory = function (domId) {
    return new geocamShare.core.SidebarSwitcher(domId);
}
