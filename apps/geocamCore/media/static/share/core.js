// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

var geocamShare = {};

geocamShare.core = {
    // module variables
    featuresG: [],
    newFeaturesG: null,
    highlightedFeatureG: null,
    visibleFeaturesG: null,
    mapViewChangeTimeoutG: null,
    mapG: null,
    galleryG: null,
    debugObjectG: null,
    widgetManagerG: null,
    viewportG: "",
    viewIndexUuidG: null,
    
    highlightedFeatureUuid: null,
    selectedFeatureUuid: null,
    
    parseFeature: function (feature) {
        // note: destructive

        feature.properties.uuid = feature.id;
        if (feature.geometry.type == "Point") {
            var coords = feature.geometry.coordinates;
            feature.properties.longitude = coords[0];
            feature.properties.latitude = coords[1];
        } else {
            var bbox = feature.bbox;
            var dims = feature.bbox.length / 2;
            feature.properties.minLon = bbox[0];
            feature.properties.minLat = bbox[1];
            feature.properties.maxLon = bbox[dims];
            feature.properties.maxLat = bbox[dims+1];
        }
        feature.properties.geometry = feature.geometry;
        result = new geocamShare.core[feature.properties.subtype](feature.properties);
        return result;
    },

    updateFeature: function (feature) {
        // update one feature whose meta-data has changed

        feature = geocamShare.core.parseFeature(feature);

        var oldFeature = geocamShare.core.featuresByUuidG[feature.uuid];
        if (oldFeature.visibleIndex != null) {
            feature.visibleIndex = oldFeature.visibleIndex;
            geocamShare.core.visibleFeaturesG[oldFeature.visibleIndex] = feature;
        }
        geocamShare.core.featuresByUuidG[feature.uuid] = feature;

        var diff = {featuresToDelete: [oldFeature],
                    featuresToAdd: [feature]};
        geocamShare.core.updateFeatures(geocamShare.core.featuresG, diff);
    },

    reloadFeatures: function (query) {
        var url = geocamShare.core.settings.SCRIPT_NAME + "features.json";
        if (query != null) {
            url += '?q=' + escape(query);
        }
        $.getJSON(url, geocamShare.core.handleNewFeatures);

        return false;
    },

    handleNewFeatures: function (response) {
        if (response.error == null) {
            var jsonFeatures = response.result.features;
            var parsedFeatures = [];
            $.each(jsonFeatures,
                   function (i, feature) {
                       parsedFeatures.push(geocamShare.core.parseFeature(feature));
                   });
            geocamShare.core.newFeaturesG = parsedFeatures;
            geocamShare.core.setViewIfReady();
        } else {
            geocamShare.core.showError('invalid search query', response.error.message);
        }
    },

    showError: function (shortMessage, longMessage) {
        $('#errorMessage').html('<span style="background-color: #ff7; padding: 0.7em; padding-top: 0.3em; padding-bottom: 0.3em;">' + shortMessage + ' <a href="." id="clearError" style="margin-left: 0.5em;">ok</span></span>');
        $('#clearError').click(function () {
            $('#errorMessage').html('')
            return false;
        });

        $(geocamShare.core).trigger('error', [shortMessage, longMessage]);
    },

    runSearch: function (query) {
        geocamShare.core.queryG = query;

        geocamShare.core.clearHighlightedFeature();
        geocamShare.core.clearSelectedFeature();
        geocamShare.core.notifyLoading();
        geocamShare.core.reloadFeatures(query);
        geocamShare.core.setSessionVars({'q': query});
        return false;
    },
    
    bindEvent: function (src, trg, eventName, funcName) {
        if (funcName == null) {
            funcName = eventName;
        }
        
        var func = trg[funcName];
        $(src).bind(eventName, function () {
            Array.shift(arguments);
            func.apply(trg, arguments);
        });
    },

    init: function () {
        // fetch JSON features and start map loading in parallel
        var mapFactory;
        if (geocamShare.core.settings.MAP_BACKEND == "earth") {
            mapFactory = geocamShare.core.EarthApiMapViewer.factory;
        } else if (geocamShare.core.settings.MAP_BACKEND == "maps") {
            mapFactory = geocamShare.core.MapsApiMapViewer.factory;
        } else {
            mapFactory = geocamShare.core.StubMapViewer.factory;
        }
        
        geocamShare.core.widgetManagerG = new geocamShare.core.WidgetManager();
        geocamShare.core.widgetManagerG.setWidgetForDomId("mapContainer", mapFactory);
        geocamShare.core.mapG = geocamShare.core.widgetManagerG.activeWidgets["mapContainer"];
        geocamShare.core.widgetManagerG.setWidgetForDomId("galleryContainer", geocamShare.core.SidebarSwitcher.factory);
        
        if (geocamShare.core.queryG != "") {
            var searchBox = $('#searchBox');
            searchBox.val(geocamShare.core.queryG);
            searchBox.css('color', '#000');
        }
        geocamShare.core.setViewIfReady();
        // set up menus
        //$(function() { $('#jd_menu').jdMenu(); });
    },
    
    uuidMap: function (features) {
        var result = {};
        $.each(features,
               function (i, feature) {
                   result[feature.uuid] = feature;
               });
        return result;
    },
    
    diffFeatures: function (oldFeatures, newFeatures) {
        $.each(oldFeatures,
               function (i, feature) {
                   feature.keep = false;
               });
        
        var oldFeaturesByUuid = geocamShare.core.uuidMap(oldFeatures);
        
        var diff = {};
        diff.featuresToAdd = [];
        $.each(newFeatures,
               function (i, feature) {
                   var matchingOldFeature = oldFeaturesByUuid[feature.uuid];
                   if (matchingOldFeature == null || matchingOldFeature.version != feature.version) {
                       diff.featuresToAdd.push(feature);
                   } else {
                       matchingOldFeature.keep = true;
                       if (matchingOldFeature.mapObject != undefined) {
                           feature.mapObject = matchingOldFeature.mapObject;
                       }
                   }
               });
        
        diff.featuresToDelete = [];
        $.each(oldFeatures,
               function (i, feature) {
                   if (!feature.keep) {
                       diff.featuresToDelete.push(feature);
                   }
               });
        
        return diff;
    },
    
    checkFeaturesInMapViewport: function (features) {
        var filteredFeatures = geocamShare.core.mapG.getFilteredFeatures(features);
        var visibleFeatures = filteredFeatures.inViewportOrNoPosition;

        if (geocamShare.core.visibleFeaturesG != null
            && geocamShare.core.featureListsEqual(geocamShare.core.visibleFeaturesG, visibleFeatures)) return;
        
        // renumber visibleIndex values
        $.each(visibleFeatures,
               function (i, feature) {
                   feature.visibleIndex = i;
               });

        var numFeatures = features.length;
        var numInViewport = filteredFeatures.inViewport.length;
        var numNoPosition = filteredFeatures.inViewportOrNoPosition.length - numInViewport;
        var numFeaturesWithPosition = numFeatures - numNoPosition;
        fhtml = numInViewport + ' of '
	    + numFeaturesWithPosition + ' features in map view';
        $('#featuresOutOfView').html(fhtml);
        
        geocamShare.core.notifyFeaturesInMapViewport(visibleFeatures);

        geocamShare.core.visibleFeaturesG = visibleFeatures;
    },
    
    getHeadingCardinal: function (yaw) {
        var i = Math.round(yaw / 22.5);
        i = i % 16;
        var directions = ['N', 'NNE', 'NE', 'ENE',
                          'E', 'ESE', 'SE', 'SSE',
                          'S', 'SSW', 'SW', 'WSW',
                          'W', 'WNW', 'NW', 'NNW'];
        return directions[i];
    },

    getHostUrl: function (noHostUrl) {
        return window.location.protocol + '//' + window.location.host;
    },
    
    wrapKml: function (text) {
        return '<?xml version="1.0" encoding="UTF-8"?>\n'
	    + '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
            + text
            + '</kml>';
    },
    
    getKmlForFeatures: function (features) {
        var kml = ''
	    + '  <Document id="allFeatures">\n';
        $.each(features,
               function (uuid, feature) {
                   kml += feature.getKml();
               })
            kml += ''
	    + '  </Document>\n';
        return geocamShare.core.wrapKml(kml);
    },
    
    handleMapViewChange0: function () {
        if (geocamShare.core.mapG.boundsAreSet) {
            geocamShare.core.setSessionVars({'v': geocamShare.core.mapG.getViewport()});
        }
	geocamShare.core.checkFeaturesInMapViewport(geocamShare.core.featuresG);
    },

    handleMapViewChange: function () {
        // this is a guarding wrapper around handleMapViewChange0(), which does the real work

        if (geocamShare.core.mapViewChangeTimeoutG != null) {
	    // avoid handling the same move many times -- clear the old timeout first
	    clearTimeout(geocamShare.core.mapViewChangeTimeoutG);
        }
        geocamShare.core.mapViewChangeTimeoutG = setTimeout(function () {
            geocamShare.core.handleMapViewChange0();
	}, 250);
    },
    
    featureListsEqual: function (a, b) {
        // featureLists are defined to be equal if their features have the same uuids.
        // this must be true if they have the same length and the uuids of b
        // are a subset of the uuids of a.
        
        if (a.length != b.length) return false;
        
        var amap = geocamShare.core.uuidMap(a);
        for (var i=0; i < b.length; i++) {
            if (amap[b[i].uuid] == undefined) {
                return false;
            }
        }
        
        return true;
    },
    
    getPagerHtml: function (numPages, pageNum, pageNumToUrl) {
        function pg0(pageNum, text) {
            return '<a href="' + pageNumToUrl(pageNum) + '">' + text + '</a>';
        }
        
        function pg(pageNum) {
            return pg0(pageNum, pageNum);
        }
        
        function disabled(text) {
            return '<span style="color: #999999">' + text + '</span>';
        }
        
        var dotsWidth = 19;
        var numWidth = 15 * Math.ceil(Math.log(numPages)/Math.log(10));
        var divWidth = 2*dotsWidth + 3*numWidth;
        
        if (numPages <= 1) {
            return "&nbsp;";
        }
        
        ret = [];
        if (pageNum > 1) {
	    ret.push(pg0(pageNum-1, '&laquo; previous'));
        } else {
            ret.push(disabled('&laquo; previous'));
        }
        ret.push('<div style="width: ' + divWidth + 'px; text-align: center; display: inline-block;">');
        if (pageNum > 1) {
	    ret.push(pg(1));
        }
        if (pageNum > 2) {
            ret.push('...');
	    /*if (pageNum > 3) {
	      ret.push('...');
	      }
	      ret.push(pg(pageNum-1));*/
        }
        if (numPages > 1) {
            ret.push('<b>' + pageNum + '</b>');
        }
        if (pageNum < numPages-1) {
            ret.push('...');
            /*
	      ret.push(pg(pageNum+1));
	      if (pageNum < numPages-2) {
	      ret.push('...');
              }*/
        }
        if (pageNum < numPages) {
	    ret.push(pg(numPages));
        }
        ret.push('</div>');
        if (pageNum < numPages) {
	    ret.push(pg0(pageNum+1, 'next &raquo;'));
        } else {
	    ret.push(disabled('next &raquo;'));
        }
        return ret.join(' ');
    },
    
    setSessionVars: function (varMap) {
        var url = geocamShare.core.settings.SCRIPT_NAME + 'setVars';
        var sep = '?';
        $.each(varMap,
               function (key, val) {
                   url += sep + key + '=' + escape(val);
                   sep = '&';
               });
        $.get(url);
    },    
    
    setView: function (oldFeatures, newFeatures) {
        var diff = geocamShare.core.diffFeatures(oldFeatures, newFeatures);
        geocamShare.core.updateFeatures(newFeatures, diff);
        geocamShare.core.handleMapViewChange();
    },
    
    setViewIfReady: function () {
        // this is a hack, figure out a cleaner integration of tracking later
        if (geocamShare.core.mapG != null
            && geocamShare.core.settings.USE_TRACKING
            && geocamShare.core.settings.MAP_BACKEND == 'maps'
            && geocamShare.tracking != null) {
            geocamShare.tracking.startTracking();
        }

        if (geocamShare.core.mapG != null && geocamShare.core.mapG.isReady && geocamShare.core.newFeaturesG != null) {
            var oldFeatures = geocamShare.core.featuresG;
            geocamShare.core.featuresG = geocamShare.core.newFeaturesG;
            geocamShare.core.featuresByUuidG = geocamShare.core.uuidMap(geocamShare.core.featuresG);
            geocamShare.core.newFeaturesG = null;
	    geocamShare.core.setView(oldFeatures, geocamShare.core.featuresG);
        }
    },

    getLoadingIcon: function () {
        return '<img src="' + geocamShare.core.settings.MEDIA_URL + 'icons/loading.gif"'
	    +'   width="24" height="24" class="loadingIcon" title="loading icon"/>'
    },

    getPendingStatusHtml: function (message) {
        return '<div style="margin: 10px;">'
            + geocamShare.core.getLoadingIcon()
            + '<span style="vertical-align: middle;">' + message + '</span>'
            + '</div>';
    },

    setHighlightedFeature: function (uuid) {
        if (geocamShare.core.highlightedFeatureUuid == uuid) {
            // do nothing
        } else {
            geocamShare.core.clearHighlightedFeature();
            var feature = geocamShare.core.featuresByUuidG[uuid];
            $(geocamShare.core).trigger("highlightFeature", [feature]);
            geocamShare.core.highlightedFeatureUuid = uuid;
            
            geocamShare.core.viewIndexUuidG = uuid;
        }
    },
    
    clearHighlightedFeature: function () {
        if (geocamShare.core.highlightedFeatureUuid != null) {
            var feature = geocamShare.core.featuresByUuidG[geocamShare.core.highlightedFeatureUuid];
            $(geocamShare.core).trigger("unhighlightFeature", [feature]);
            geocamShare.core.highlightedFeatureUuid = null;
        }
    },

    setSelectedFeature: function (uuid) {
        if (geocamShare.core.selectedFeatureUuid == uuid) {
            // do nothing
        } else {
            geocamShare.core.clearSelectedFeature();
            var feature = geocamShare.core.featuresByUuidG[uuid];
            $(geocamShare.core).trigger("selectFeature", [feature]);
            geocamShare.core.selectedFeatureUuid = uuid;
            
            geocamShare.core.viewIndexUuidG = uuid;
        }
    },

    clearSelectedFeature: function () {
        if (geocamShare.core.selectedFeatureUuid != null) {
            var feature = geocamShare.core.featuresByUuidG[geocamShare.core.selectFeatureUuid];
            $(geocamShare.core).trigger("unselectFeature", [feature]);
            geocamShare.core.selectedFeatureUuid = null;
        }
    },

    updateFeatures: function (newFeatures, diff) {
        $(geocamShare.core).trigger("updateFeatures", arguments);
    },

    notifyLoading: function () {
        $(geocamShare.core).trigger("notifyLoading", arguments);
    },

    notifyFeaturesInMapViewport: function (features) {
        $(geocamShare.core).trigger("notifyFeaturesInMapViewport", arguments);
    },

    setToFeatureDetail: function () {
        $(geocamShare.core).trigger("setToFeatureDetail", arguments);
    },

    setToFeatureEdit: function () {
        $(geocamShare.core).trigger("setToFeatureEdit", arguments);
    }

};
