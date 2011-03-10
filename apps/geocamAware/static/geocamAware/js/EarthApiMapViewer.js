// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.EarthApiMapViewer = new Class(
{
    Extends: geocamAware.MapViewer,
    
    /**********************************************************************
     * variables
     **********************************************************************/
    
    isReady: false,
    
    ge: null, // Google Earth Plugin instance
    
    gex: null, // Google Earth Extensions instance
    
    listenersInitialized: false,
    
    allFeaturesFolder: null,
    
    /**********************************************************************
     * implement MapViewer interface
     **********************************************************************/
    
    initialize: function (domId) {
        $('#'+domId).html('<div id="map3d"></div>');
        
        var self = this;
        google.earth.createInstance('map3d',
                                    function(instance) {
                                        return self.handleCreateInstanceDone(instance);
                                    },
                                    function(instance) {
                                        // ignore error
                                    });
    },
    
    updateFeatures: function (newFeatures, diff) {
        var self = this;
        
        $.each(diff.featuresToDelete,
               function (i, feature) {
                   var parent = feature.mapObject.getParentNode();
                   parent.getFeatures().removeChild(feature.mapObject);
               });
        
        if (diff.featuresToAdd.length > 0) {
            if (self.allFeaturesFolder == null) {
                self.allFeaturesFolder = self.ge.createFolder("allFeatures");
                self.ge.getFeatures().appendChild(self.allFeaturesFolder);
            }
            
            $.each(diff.featuresToAdd,
                   function (i, feature) {
                       var kml = geocamAware.wrapKml(geocamAware.getFeatureKml(feature));
                       var geFeature = self.ge.parseKml(kml);
                       self.allFeaturesFolder.getFeatures().appendChild(geFeature);
                       feature.mapObject = geFeature;
                   });
            
            this.setListeners(diff.featuresToAdd);
        }
        
        if (diff.featuresToDelete.length > 0 || diff.featuresToAdd.length > 0) {
            //self.zoomToFit();
            geocamAware.setGalleryToVisibleSubsetOf(geocamAware.featuresG);
        }
    },
    
    getFilteredFeatures: function (features) {
        var self = this;
        var bounds = self.getViewBounds();
        
        var inViewportFeatures = [];
        var inViewportOrNoPositionFeatures = [];
        $.each(features,
               function (i, feature) {
                   var placemark = feature.mapObject;
                   if (self.getFeatureHasPosition(feature)) {
                       if (self.featureIntersectsBounds(feature, bounds)) {
                           inViewportFeatures.push(feature);                           
                           inViewportOrNoPositionFeatures.push(feature);
                       }
                   } else {
                       inViewportOrNoPositionFeatures.push(feature);
                   }
               });
        
        return {'inViewport': inViewportFeatures,
                'inViewportOrNoPosition': inViewportOrNoPositionFeatures};
    },
    
    zoomToFit: function () {
        this.gex.util.flyToObject(this.allFeaturesFolder);
    },
    
    highlightFeature: function(feature) {
        feature.mapObject.getStyleSelector().getIconStyle().setScale(1.5);
    },
    
    unhighlightFeature: function(feature) {
        feature.mapObject.getStyleSelector().getIconStyle().setScale(1);
    },
    
    /**********************************************************************
     * helper functions
     **********************************************************************/
    
    handleCreateInstanceDone: function (instance) {
        this.ge = instance;
        this.ge.getWindow().setVisibility(true);
        
        // add a navigation control
        this.ge.getNavigationControl().setVisibility(this.ge.VISIBILITY_AUTO);
        
        // add some layers
        this.ge.getLayerRoot().enableLayerById(this.ge.LAYER_BORDERS, true);
        this.ge.getLayerRoot().enableLayerById(this.ge.LAYER_ROADS, true);
        
        this.gex = new GEarthExtensions(this.ge);
        
        geocamAware.bindEvent(geocamAware, this, "highlightFeature");
        geocamAware.bindEvent(geocamAware, this, "unhighlightFeature");
        geocamAware.bindEvent(geocamAware, this, "selectFeature");
        geocamAware.bindEvent(geocamAware, this, "updateFeatures");

        this.isReady = true;
        geocamAware.setViewIfReady();
    },
    
    featureIntersectsBounds: function (feature, bounds) {
        // FIX: support features with extent!
        var lat = feature.latitude;
        var lon = feature.longitude;
        return ((bounds.getSouth() <= lat) && (lat <= bounds.getNorth())
                && (bounds.getWest() <= lon) && (lon <= bounds.getEast()));
    },
    
    selectFeature: function(feature) {
        var balloon = this.ge.createHtmlStringBalloon('');
        
        var placemark = feature.mapObject;
        balloon.setFeature(placemark);
        
        balloon.setContentString(feature.getBalloonHtml());
        this.ge.setBalloon(balloon);
    },
    
    setListeners: function(features) {
        var self = this;
        $.each(features,
               function (i, feature) {
                   var placemark = feature.mapObject;
                   google.earth.addEventListener(placemark, 'mouseover',
                                                 function (uuid) {
                                                     return function(event) {
                                                         geocamAware.setHighlightedFeature(uuid);
                                                     }
                                                 }(feature.uuid));
                   google.earth.addEventListener(placemark, 'mouseout',
                                                 function (uuid) {
                                                     return function(event) {
                                                         geocamAware.clearHighlightedFeature();
                                                     }
                                                 }(feature.uuid));
                   google.earth.addEventListener(placemark, 'click',
                                                 function (uuid) {
                                                     return function(event) {
                                                         event.preventDefault();
                                                         geocamAware.setSelectedFeature(uuid);
                                                     }
                                                 }(feature.uuid));
               });
        
        if (!this.listenersInitialized) {
            google.earth.addEventListener(this.ge.getView(), 'viewchangeend', geocamAware.handleMapViewChange);
        }
        this.listenersInitialized = true;
    },
    
    getViewBounds: function() {
        return this.ge.getView().getViewportGlobeBounds();
    }
    
});

geocamAware.EarthApiMapViewer.factory = function (domId) {
    return new geocamAware.EarthApiMapViewer(domId);
}
