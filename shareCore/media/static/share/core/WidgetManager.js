// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.WidgetManager = new Class(
{
    activeWidgets: {},
    
    setWidgetForDomId: function (domId, widgetFactory, widgetFactoryArgs) {
        if (widgetFactoryArgs == undefined) {
            widgetFactoryArgs = [];
        }
        this.activeWidgets[domId] = widgetFactory.apply(null, [domId].concat(widgetFactoryArgs));
    },
    
    updateFeatures: function (newFeatures, diff) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.updateFeatures(newFeatures, diff);
               });
    },

    notifyLoading: function () {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.notifyLoading();
               });
    },

    notifyFeaturesInMapViewport: function (features) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.notifyFeaturesInMapViewport(features);
               });
    },
    
    highlightFeature: function (feature) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.highlightFeature(feature);
               });
    },
    
    unhighlightFeature: function (feature) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.unhighlightFeature(feature);
               });
    },
    
    selectFeature: function (feature) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.selectFeature(feature);
               });
    },
    
    unselectFeature: function (feature) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.unselectFeature(feature);
               });
    },

    /**********************************************************************
     * guard logic for top-level manager
     **********************************************************************/

    highlightedFeatureUuid: null,
    
    selectedFeatureUuid: null,
    
    setHighlightedFeature: function (uuid) {
        if (this.highlightedFeatureUuid == uuid) {
            // do nothing
        } else {
            this.clearHighlightedFeature();
            this.highlightFeature(geocamShare.core.featuresByUuidG[uuid]);
            this.highlightedFeatureUuid = uuid;
            
            geocamShare.core.viewIndexUuidG = uuid;
        }
    },
    
    clearHighlightedFeature: function () {
        if (this.highlightedFeatureUuid != null) {
            this.unhighlightFeature(geocamShare.core.featuresByUuidG[this.highlightedFeatureUuid]);
            this.highlightedFeatureUuid = null;
        }
    },

    setSelectedFeature: function (uuid) {
        if (this.selectedFeatureUuid == uuid) {
            // do nothing
        } else {
            this.clearSelectedFeature();
            this.selectFeature(geocamShare.core.featuresByUuidG[uuid]);
            this.selectedFeatureUuid = uuid;
            
            geocamShare.core.viewIndexUuidG = uuid;
        }
    },

    clearSelectedFeature: function () {
        if (this.selectedFeatureUuid != null) {
            this.unselectFeature(geocamShare.core.featuresByUuidG[this.selectFeatureUuid]);
            this.selectedFeatureUuid = null;
        }
    }
});

