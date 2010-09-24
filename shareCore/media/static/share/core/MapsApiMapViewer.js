// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.MapsApiMapViewer = new Class(
{
    Extends: geocamShare.core.MapViewer,

    /**********************************************************************
     * variables
     **********************************************************************/
    
    isReady: false,
    
    gmap: null,
    
    mainListenerInitialized: false,
    
    balloon: null,
    
    boundsAreSet: false,
    
    /**********************************************************************
     * implement MapViewer interface
     **********************************************************************/
    
    initialize: function(domId) {
        //var latlng = new google.maps.LatLng(37, -120);
        var myOptions = {
            /*zoom: 4,
              center: latlng,*/
            mapTypeId: google.maps.MapTypeId.HYBRID
        };
        this.gmap = new google.maps.Map(document.getElementById(domId), myOptions);
        if (geocamShare.core.viewportG != "") {
            this.setViewport(geocamShare.core.viewportG);
            this.boundsAreSet = true;
        }
        this.isReady = true;
        
        geocamShare.core.setViewIfReady();
    },

    updateFeatures: function (oldFeatures, newFeatures, diff) {
        var self = this;
        
        $.each(diff.featuresToDelete,
               function (i, feature) {
                   self.removeFeatureFromMap(feature);
               });
        
        if (diff.featuresToAdd.length > 0) {
            $.each(diff.featuresToAdd,
                   function (i, feature) {
                       self.addFeature(feature);
                   });
        }
        this.setListeners(diff.featuresToAdd);
        
        if (diff.featuresToDelete.length > 0 || diff.featuresToAdd.length > 0) {
            if (!this.boundsAreSet) {
                this.zoomToFit();
            }
            // used to call geocamShare.core.setGalleryToVisibleSubsetOf(geocamShare.core.featuresG)
            // here, but geocamShare.core.handleMapViewChange() gives the map backend
            // some time to adjust after the zoomToFit() call
            geocamShare.core.handleMapViewChange();
        }
    },
    
    zoomToFit: function () {
        this.gmap.fitBounds(this.getMarkerBounds());
        this.boundsAreSet = true;
    },
    
    getViewport: function () {
        var c = this.gmap.getCenter();
        return c.lat() + ',' + c.lng() + ',' + this.gmap.getZoom();
    },
    
    setViewport: function (view) {
        var v = view.split(',');
        this.gmap.setCenter(new google.maps.LatLng(v[0], v[1]));
        this.gmap.setZoom(parseInt(v[2]));
    },
    
    getFilteredFeatures: function (features) {
        var bounds = this.gmap.getBounds();
        
        var inViewportFeatures = [];
        var inViewportOrNoPositionFeatures = [];
        var self = this;
        $.each(features,
               function (i, feature) {
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
    
    highlightFeature: function(feature) {
        if (feature.mapObject != null && feature.mapObject.current != feature.mapObject.highlight) {
            this.addToMap(feature.mapObject.highlight);
            this.removeFromMap(feature.mapObject.normal);
            feature.mapObject.current = feature.mapObject.highlight;
        }
    },
    
    unhighlightFeature: function(feature) {
        if (feature.mapObject != null && feature.mapObject.current != feature.mapObject.normal) {
            this.addToMap(feature.mapObject.normal);
            this.removeFromMap(feature.mapObject.highlight);
            feature.mapObject.current = feature.mapObject.normal;
        }
    },
    
    /**********************************************************************
     * helper functions
     **********************************************************************/
    
    removeFeatureFromMap: function (feature) {
        var self = this;
        if (feature.mapObject == null) {
            // nothing to remove
        } else if (feature.type == "Track") {
            for (var i=0; i < feature.mapObject.polylines.length; i++) {
                var polyline = feature.mapObject.polylines[i];
                self.removeFromMap(polyline);
            }
        } else {
            self.removeFromMap(feature.mapObject.normal);
            self.removeFromMap(feature.mapObject.highlight);
        }
    },
    
    featureIntersectsBounds: function (feature, bounds) {
        if (feature.latitude != null) {
            return bounds.contains(new google.maps.LatLng(feature.latitude, feature.longitude));
        } else if (feature.minLat != null) {
            var ibounds = new google.maps.LatLngBounds();
            ibounds.extend(new google.maps.LatLng(feature.minLat, feature.minLon));
            ibounds.extend(new google.maps.LatLng(feature.maxLat, feature.maxLon));
            return ibounds.intersects(bounds);
        } else {
            throw 'huh? got feature with no position';
        }
    },
    
    addMarker: function (feature) {
        var self = this;
        
        var iconUrl = geocamShare.core.getIconMapUrl(feature);
        feature.mapObject = {normal: self.getMarker(feature, 0.7),
                             highlight: self.getMarker(feature, 1.0)};
        
        var markers = [feature.mapObject.normal, feature.mapObject.highlight];
        $.each
            (markers,
             function (j, marker) {
                 google.maps.event.addListener
                 (marker, 'mouseover',
                  function (uuid) {
                      return function () {
                          geocamShare.core.widgetManagerG.setFeatureHighlighted(uuid, true);
                      }
                  }(feature.uuid));
                 google.maps.event.addListener
                 (marker, 'mouseout',
                  function (uuid) {
                      return function () {
                          geocamShare.core.widgetManagerG.setFeatureHighlighted(uuid, false);
                      }
                  }(feature.uuid));
                 google.maps.event.addListener
                 (marker, 'click',
                  function (uuid) {
                      return function () {
                          geocamShare.core.widgetManagerG.setFeatureSelected(uuid, true);
                      }
                  }(feature.uuid));
             });
        
        self.unhighlightFeature(feature); // add to map in 'normal' state
    },
    
    addTrack: function (feature) {
        var self = this;
        var trackLines = feature.geometry.geometry;
        var path = [];
        feature.mapObject = {polylines: []};
        $.each(trackLines,
               function (i, trackLine) {
                   var path = [];
                   $.each(trackLine,
                          function (j, pt) {
                              path.push(new google.maps.LatLng(pt[1], pt[0]));
                          });
                   var polyline = new google.maps.Polyline({map: self.gmap,
                                                            path: path,
                                                            strokeColor: '#FF0000',
                                                            strokeOpacity: 1.0,
                                                            strokeWidth: 4,
                                                            zIndex: 50});
                   feature.mapObject.polylines.push(polyline);
               });
    },
    
    addFeature: function (feature) {
        if (geocamShare.core.isImage(feature)) {
            if (feature.latitude == null) {
                return; // skip non-geotagged features
            }
            this.addMarker(feature);
        } else if (feature.type == 'Track') {
            if (feature.minLat == null) {
                return; // skip non-geotagged features
            }
            this.addTrack(feature);
        }
    },
    
    getMarker: function (feature, scale) {
        var position = new google.maps.LatLng(feature.latitude, feature.longitude);
        var iconUrl = geocamShare.core.getIconMapRotUrl(feature);
        var iconSize = new google.maps.Size(feature.rotatedIcon.size[0], feature.rotatedIcon.size[1]);
        var origin = new google.maps.Point(0, 0);
        var scaledSize = new google.maps.Size(scale*iconSize.width, scale*iconSize.height);
        var anchor = new google.maps.Point(0.5*scaledSize.width, 0.5*scaledSize.height);
        
        var markerImage = new google.maps.MarkerImage(iconUrl, iconSize, origin, anchor, scaledSize);
        
        return new google.maps.Marker({position: position,
                                       icon: markerImage
                                      });
    },
    
    addToMap: function (marker) {
        marker.setMap(this.gmap);
    },
    
    removeFromMap: function (marker) {
        marker.setMap(null);
    },
    
    getMarkerBounds: function () {
        var bounds = new google.maps.LatLngBounds();
        $.each(geocamShare.core.featuresG,
               function (i, feature) {
                   if (feature.latitude != null) {
                       bounds.extend(new google.maps.LatLng(feature.latitude, feature.longitude));
                   } else if (feature.minLat != null) {
                       var featureBounds = new google.maps.LatLngBounds
                         (new google.maps.LatLng(feature.minLat, feature.minLon),
                          new google.maps.LatLng(feature.maxLat, feature.maxLon));
                       bounds.union(featureBounds);
                   }
               });
        return bounds;
    },
    
    showBalloonForFeature: function (feature) {
        if (this.balloon != null) {
            this.balloon.close();
        }
        this.balloon = new google.maps.InfoWindow({content: geocamShare.core.getFeatureBalloonHtml(feature)});
        this.balloon.open(this.gmap, feature.mapObject.current);
    },

    selectFeature: function(feature) {
        // this.showBalloonForFeature(feature);
    },
    
    setListeners: function(features) {
        var self = this;
        if (!this.mainListenerInitialized) {
            google.maps.event.addListener(this.gmap, 'bounds_changed', geocamShare.core.handleMapViewChange);
            this.mainListenerInitialized = true;
        }
    }
    
});

geocamShare.core.MapsApiMapViewer.factory = function (domId) {
    return new geocamShare.core.MapsApiMapViewer(domId);
}
