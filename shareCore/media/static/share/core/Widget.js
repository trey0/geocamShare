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
    },
    
    // wrapper functions and associated member variables
    
    highlightedFeatureUuid: null,
    
    selectedFeatureUuid: null,
    
    setFeatureHighlighted: function (uuid, isHighlighted) {
        if (isHighlighted) {
            if (this.highlightedFeatureUuid == uuid) {
                // do nothing
            } else {
                if (this.highlightedFeatureUuid != null) {
                    this.unhighlightFeature(geocamShare.core.featuresByUuidG[this.highlightedFeatureUuid]);
                }
                this.highlightFeature(geocamShare.core.featuresByUuidG[uuid]);
                this.highlightedFeatureUuid = uuid;
            }
        } else {
            if (this.highlightedFeatureUuid == uuid) {
                this.unhighlightFeature(geocamShare.core.featuresByUuidG[uuid]);
                this.highlightedFeatureUuid = null;
            } else {
                // do nothing
            }
        }
    },
    
    setFeatureSelected: function (uuid, isSelected) {
        if (isSelected) {
            if (this.selectedFeatureUuid == uuid) {
                // do nothing
            } else {
                if (uuid != null) {
                    this.unselectFeature(geocamShare.core.featuresByUuidG[this.selectedFeatureUuid]);
                }
                this.selectFeature(geocamShare.core.featuresByUuidG[uuid]);
                this.selectedFeatureUuid = uuid;
            }
        } else {
            if (this.selectedFeatureUuid == uuid) {
                this.unselectFeature(geocamShare.core.featuresByUuidG[uuid]);
                this.selectedFeatureUuid = null;
            } else {
                // do nothing
            }
        }
    }
});

