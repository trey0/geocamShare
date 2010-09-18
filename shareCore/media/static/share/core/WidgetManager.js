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
    
    updateFeatures: function (oldFeatures, newFeatures, diff) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.updateFeatures(oldFeatures, newFeatures, diff);
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

    setFeatureSelected: function (uuid, isSelected) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.setFeatureSelected(uuid, isSelected);
               });
    },
    
    setFeatureHighlighted: function (uuid, isHighlighted) {
        $.each(this.activeWidgets,
               function (domId, widget) {
                   widget.setFeatureHighlighted(uuid, isHighlighted);
               });
    },
    
    /**********************************************************************
     * guard logic for top-level manager
     **********************************************************************/

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

                geocamShare.core.viewIndexUuidG = uuid;
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

                geocamShare.core.viewIndexUuidG = uuid;
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

