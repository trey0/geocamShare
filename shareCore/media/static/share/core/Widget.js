// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

share.core.Widget = new Class({
        // functions to implement in derived classes

        initialize: function (domId) {
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
                        this.unhighlightFeature(share.core.featuresByUuidG[this.highlightedFeatureUuid]);
                    }
                    this.highlightFeature(share.core.featuresByUuidG[uuid]);
                    this.highlightedFeatureUuid = uuid;
                }
            } else {
                if (this.highlightedFeatureUuid == uuid) {
                    this.unhighlightFeature(share.core.featuresByUuidG[uuid]);
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
                        this.unselectFeature(share.core.featuresByUuidG[this.selectedFeatureUuid]);
                    }
                    this.selectFeature(share.core.featuresByUuidG[uuid]);
                    this.selectedFeatureUuid = uuid;
                }
            } else {
                if (this.selectedFeatureUuid == uuid) {
                    this.unselectFeature(share.core.featuresByUuidG[uuid]);
                    this.selectedFeatureUuid = null;
                } else {
                    // do nothing
                }
            }
        }
    });

