// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

var geocamAware = {
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
        result = new geocamAware[feature.properties.subtype](feature.properties);
        return result;
    },

    updateFeature: function (feature) {
        // update one feature whose meta-data has changed

        feature = geocamAware.parseFeature(feature);

        var oldFeature = geocamAware.featuresByUuidG[feature.uuid];
        if (oldFeature.visibleIndex != null) {
            feature.visibleIndex = oldFeature.visibleIndex;
            geocamAware.visibleFeaturesG[oldFeature.visibleIndex] = feature;
        }
        geocamAware.featuresByUuidG[feature.uuid] = feature;

        var diff = {featuresToDelete: [oldFeature],
                    featuresToAdd: [feature]};
        geocamAware.updateFeatures(geocamAware.featuresG, diff);
    },

    reloadFeatures: function (query) {
        var url = geocamAware.settings.SCRIPT_NAME + "geocamLens/features.json";
        if (query != null) {
            url += '?q=' + escape(query);
        }
        $.getJSON(url, geocamAware.handleNewFeatures);

        return false;
    },

    handleNewFeatures: function (response) {
        if (response.error == null) {
            var jsonFeatures = response.result.features;
            var parsedFeatures = [];
            $.each(jsonFeatures,
                   function (i, feature) {
                       parsedFeatures.push(geocamAware.parseFeature(feature));
                   });
            geocamAware.newFeaturesG = parsedFeatures;
            geocamAware.setViewIfReady();
        } else {
            geocamAware.showError('invalid search query', response.error.message);
        }
    },

    showError: function (shortMessage, longMessage) {
        $('#errorMessage').html('<span style="background-color: #ff7; padding: 0.7em; padding-top: 0.3em; padding-bottom: 0.3em;">' + shortMessage + ' <a href="." id="clearError" style="margin-left: 0.5em;">ok</span></span>');
        $('#clearError').click(function () {
            $('#errorMessage').html('')
            return false;
        });

        $(geocamAware).trigger('error', [shortMessage, longMessage]);
    },

    runSearch: function (query) {
        geocamAware.queryG = query;

        geocamAware.clearHighlightedFeature();
        geocamAware.clearSelectedFeature();
        geocamAware.notifyLoading();
        geocamAware.reloadFeatures(query);
        geocamAware.setSessionVars({'q': query});
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
        if (geocamAware.settings.GEOCAM_AWARE_MAP_BACKEND == "earth") {
            mapFactory = geocamAware.EarthApiMapViewer.factory;
        } else if (geocamAware.settings.GEOCAM_AWARE_MAP_BACKEND == "maps") {
            mapFactory = geocamAware.MapsApiMapViewer.factory;
        } else {
            mapFactory = geocamAware.StubMapViewer.factory;
        }
        
        geocamAware.widgetManagerG = new geocamAware.WidgetManager();
        geocamAware.widgetManagerG.setWidgetForDomId("mapContainer", mapFactory);
        geocamAware.mapG = geocamAware.widgetManagerG.activeWidgets["mapContainer"];
        geocamAware.widgetManagerG.setWidgetForDomId("galleryContainer", geocamAware.SidebarSwitcher.factory);
        
        if (geocamAware.queryG != "") {
            var searchBox = $('#searchBox');
            searchBox.val(geocamAware.queryG);
            searchBox.css('color', '#000');
        }
        geocamAware.setViewIfReady();
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
        
        var oldFeaturesByUuid = geocamAware.uuidMap(oldFeatures);
        
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
        var filteredFeatures = geocamAware.mapG.getFilteredFeatures(features);
        var visibleFeatures = filteredFeatures.inViewportOrNoPosition;

        if (geocamAware.visibleFeaturesG != null
            && geocamAware.featureListsEqual(geocamAware.visibleFeaturesG, visibleFeatures)) return;
        
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
        
        geocamAware.notifyFeaturesInMapViewport(visibleFeatures);

        geocamAware.visibleFeaturesG = visibleFeatures;
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
        return geocamAware.wrapKml(kml);
    },
    
    handleMapViewChange0: function () {
        if (geocamAware.mapG.boundsAreSet) {
            geocamAware.setSessionVars({'v': geocamAware.mapG.getViewport()});
        }
	geocamAware.checkFeaturesInMapViewport(geocamAware.featuresG);
    },

    handleMapViewChange: function () {
        // this is a guarding wrapper around handleMapViewChange0(), which does the real work

        if (geocamAware.mapViewChangeTimeoutG != null) {
	    // avoid handling the same move many times -- clear the old timeout first
	    clearTimeout(geocamAware.mapViewChangeTimeoutG);
        }
        geocamAware.mapViewChangeTimeoutG = setTimeout(function () {
            geocamAware.handleMapViewChange0();
	}, 250);
    },
    
    featureListsEqual: function (a, b) {
        // featureLists are defined to be equal if their features have the same uuids.
        // this must be true if they have the same length and the uuids of b
        // are a subset of the uuids of a.
        
        if (a.length != b.length) return false;
        
        var amap = geocamAware.uuidMap(a);
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
        var url = geocamAware.settings.SCRIPT_NAME + 'geocamAware/setVars';
        var sep = '?';
        $.each(varMap,
               function (key, val) {
                   url += sep + key + '=' + escape(val);
                   sep = '&';
               });
        $.get(url);
    },    
    
    setView: function (oldFeatures, newFeatures) {
        var diff = geocamAware.diffFeatures(oldFeatures, newFeatures);
        geocamAware.updateFeatures(newFeatures, diff);
        geocamAware.handleMapViewChange();
    },
    
    setViewIfReady: function () {
        // this is a hack, figure out a cleaner integration of tracking later
        if (geocamAware.mapG != null
            && geocamAware.settings.GEOCAM_AWARE_USE_TRACKING
            && geocamAware.settings.GEOCAM_AWARE_MAP_BACKEND == 'maps'
            && geocamTrack != null) {
            geocamTrack.startTracking();
        }

        if (geocamAware.mapG != null && geocamAware.mapG.isReady && geocamAware.newFeaturesG != null) {
            var oldFeatures = geocamAware.featuresG;
            geocamAware.featuresG = geocamAware.newFeaturesG;
            geocamAware.featuresByUuidG = geocamAware.uuidMap(geocamAware.featuresG);
            geocamAware.newFeaturesG = null;
	    geocamAware.setView(oldFeatures, geocamAware.featuresG);
        }
    },

    getLoadingIcon: function () {
        return '<img src="' + geocamAware.settings.MEDIA_URL + 'external/icons/loading.gif"'
	    +'   width="24" height="24" class="loadingIcon" title="loading icon"/>'
    },

    getPendingStatusHtml: function (message) {
        return '<div style="margin: 10px;">'
            + geocamAware.getLoadingIcon()
            + '<span style="vertical-align: middle;">' + message + '</span>'
            + '</div>';
    },

    setHighlightedFeature: function (uuid) {
        if (geocamAware.highlightedFeatureUuid == uuid) {
            // do nothing
        } else {
            geocamAware.clearHighlightedFeature();
            var feature = geocamAware.featuresByUuidG[uuid];
            $(geocamAware).trigger("highlightFeature", [feature]);
            geocamAware.highlightedFeatureUuid = uuid;
            
            geocamAware.viewIndexUuidG = uuid;
        }
    },
    
    clearHighlightedFeature: function () {
        if (geocamAware.highlightedFeatureUuid != null) {
            var feature = geocamAware.featuresByUuidG[geocamAware.highlightedFeatureUuid];
            $(geocamAware).trigger("unhighlightFeature", [feature]);
            geocamAware.highlightedFeatureUuid = null;
        }
    },

    setSelectedFeature: function (uuid) {
        if (geocamAware.selectedFeatureUuid == uuid) {
            // do nothing
        } else {
            geocamAware.clearSelectedFeature();
            var feature = geocamAware.featuresByUuidG[uuid];
            $(geocamAware).trigger("selectFeature", [feature]);
            geocamAware.selectedFeatureUuid = uuid;
            
            geocamAware.viewIndexUuidG = uuid;
        }
    },

    clearSelectedFeature: function () {
        if (geocamAware.selectedFeatureUuid != null) {
            var feature = geocamAware.featuresByUuidG[geocamAware.selectFeatureUuid];
            $(geocamAware).trigger("unselectFeature", [feature]);
            geocamAware.selectedFeatureUuid = null;
        }
    },

    updateFeatures: function (newFeatures, diff) {
        $(geocamAware).trigger("updateFeatures", arguments);
    },

    notifyLoading: function () {
        $(geocamAware).trigger("notifyLoading", arguments);
    },

    notifyFeaturesInMapViewport: function (features) {
        $(geocamAware).trigger("notifyFeaturesInMapViewport", arguments);
    },

    setToFeatureDetail: function () {
        $(geocamAware).trigger("setToFeatureDetail", arguments);
    },

    setToFeatureEdit: function () {
        $(geocamAware).trigger("setToFeatureEdit", arguments);
    }

};
