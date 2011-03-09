// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

var geocamCore = {
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
        result = new geocamCore[feature.properties.subtype](feature.properties);
        return result;
    },

    updateFeature: function (feature) {
        // update one feature whose meta-data has changed

        feature = geocamCore.parseFeature(feature);

        var oldFeature = geocamCore.featuresByUuidG[feature.uuid];
        if (oldFeature.visibleIndex != null) {
            feature.visibleIndex = oldFeature.visibleIndex;
            geocamCore.visibleFeaturesG[oldFeature.visibleIndex] = feature;
        }
        geocamCore.featuresByUuidG[feature.uuid] = feature;

        var diff = {featuresToDelete: [oldFeature],
                    featuresToAdd: [feature]};
        geocamCore.updateFeatures(geocamCore.featuresG, diff);
    },

    reloadFeatures: function (query) {
        var url = geocamCore.settings.SCRIPT_NAME + "features.json";
        if (query != null) {
            url += '?q=' + escape(query);
        }
        $.getJSON(url, geocamCore.handleNewFeatures);

        return false;
    },

    handleNewFeatures: function (response) {
        if (response.error == null) {
            var jsonFeatures = response.result.features;
            var parsedFeatures = [];
            $.each(jsonFeatures,
                   function (i, feature) {
                       parsedFeatures.push(geocamCore.parseFeature(feature));
                   });
            geocamCore.newFeaturesG = parsedFeatures;
            geocamCore.setViewIfReady();
        } else {
            geocamCore.showError('invalid search query', response.error.message);
        }
    },

    showError: function (shortMessage, longMessage) {
        $('#errorMessage').html('<span style="background-color: #ff7; padding: 0.7em; padding-top: 0.3em; padding-bottom: 0.3em;">' + shortMessage + ' <a href="." id="clearError" style="margin-left: 0.5em;">ok</span></span>');
        $('#clearError').click(function () {
            $('#errorMessage').html('')
            return false;
        });

        $(geocamCore).trigger('error', [shortMessage, longMessage]);
    },

    runSearch: function (query) {
        geocamCore.queryG = query;

        geocamCore.clearHighlightedFeature();
        geocamCore.clearSelectedFeature();
        geocamCore.notifyLoading();
        geocamCore.reloadFeatures(query);
        geocamCore.setSessionVars({'q': query});
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
        if (geocamCore.settings.MAP_BACKEND == "earth") {
            mapFactory = geocamCore.EarthApiMapViewer.factory;
        } else if (geocamCore.settings.MAP_BACKEND == "maps") {
            mapFactory = geocamCore.MapsApiMapViewer.factory;
        } else {
            mapFactory = geocamCore.StubMapViewer.factory;
        }
        
        geocamCore.widgetManagerG = new geocamCore.WidgetManager();
        geocamCore.widgetManagerG.setWidgetForDomId("mapContainer", mapFactory);
        geocamCore.mapG = geocamCore.widgetManagerG.activeWidgets["mapContainer"];
        geocamCore.widgetManagerG.setWidgetForDomId("galleryContainer", geocamCore.SidebarSwitcher.factory);
        
        if (geocamCore.queryG != "") {
            var searchBox = $('#searchBox');
            searchBox.val(geocamCore.queryG);
            searchBox.css('color', '#000');
        }
        geocamCore.setViewIfReady();
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
        
        var oldFeaturesByUuid = geocamCore.uuidMap(oldFeatures);
        
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
        var filteredFeatures = geocamCore.mapG.getFilteredFeatures(features);
        var visibleFeatures = filteredFeatures.inViewportOrNoPosition;

        if (geocamCore.visibleFeaturesG != null
            && geocamCore.featureListsEqual(geocamCore.visibleFeaturesG, visibleFeatures)) return;
        
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
        
        geocamCore.notifyFeaturesInMapViewport(visibleFeatures);

        geocamCore.visibleFeaturesG = visibleFeatures;
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
        return geocamCore.wrapKml(kml);
    },
    
    handleMapViewChange0: function () {
        if (geocamCore.mapG.boundsAreSet) {
            geocamCore.setSessionVars({'v': geocamCore.mapG.getViewport()});
        }
	geocamCore.checkFeaturesInMapViewport(geocamCore.featuresG);
    },

    handleMapViewChange: function () {
        // this is a guarding wrapper around handleMapViewChange0(), which does the real work

        if (geocamCore.mapViewChangeTimeoutG != null) {
	    // avoid handling the same move many times -- clear the old timeout first
	    clearTimeout(geocamCore.mapViewChangeTimeoutG);
        }
        geocamCore.mapViewChangeTimeoutG = setTimeout(function () {
            geocamCore.handleMapViewChange0();
	}, 250);
    },
    
    featureListsEqual: function (a, b) {
        // featureLists are defined to be equal if their features have the same uuids.
        // this must be true if they have the same length and the uuids of b
        // are a subset of the uuids of a.
        
        if (a.length != b.length) return false;
        
        var amap = geocamCore.uuidMap(a);
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
        var url = geocamCore.settings.SCRIPT_NAME + 'setVars';
        var sep = '?';
        $.each(varMap,
               function (key, val) {
                   url += sep + key + '=' + escape(val);
                   sep = '&';
               });
        $.get(url);
    },    
    
    setView: function (oldFeatures, newFeatures) {
        var diff = geocamCore.diffFeatures(oldFeatures, newFeatures);
        geocamCore.updateFeatures(newFeatures, diff);
        geocamCore.handleMapViewChange();
    },
    
    setViewIfReady: function () {
        // this is a hack, figure out a cleaner integration of tracking later
        if (geocamCore.mapG != null
            && geocamCore.settings.USE_TRACKING
            && geocamCore.settings.MAP_BACKEND == 'maps'
            && geocamTrack != null) {
            geocamTrack.startTracking();
        }

        if (geocamCore.mapG != null && geocamCore.mapG.isReady && geocamCore.newFeaturesG != null) {
            var oldFeatures = geocamCore.featuresG;
            geocamCore.featuresG = geocamCore.newFeaturesG;
            geocamCore.featuresByUuidG = geocamCore.uuidMap(geocamCore.featuresG);
            geocamCore.newFeaturesG = null;
	    geocamCore.setView(oldFeatures, geocamCore.featuresG);
        }
    },

    getLoadingIcon: function () {
        return '<img src="' + geocamCore.settings.MEDIA_URL + 'geocamCore/icons/loading.gif"'
	    +'   width="24" height="24" class="loadingIcon" title="loading icon"/>'
    },

    getPendingStatusHtml: function (message) {
        return '<div style="margin: 10px;">'
            + geocamCore.getLoadingIcon()
            + '<span style="vertical-align: middle;">' + message + '</span>'
            + '</div>';
    },

    setHighlightedFeature: function (uuid) {
        if (geocamCore.highlightedFeatureUuid == uuid) {
            // do nothing
        } else {
            geocamCore.clearHighlightedFeature();
            var feature = geocamCore.featuresByUuidG[uuid];
            $(geocamCore).trigger("highlightFeature", [feature]);
            geocamCore.highlightedFeatureUuid = uuid;
            
            geocamCore.viewIndexUuidG = uuid;
        }
    },
    
    clearHighlightedFeature: function () {
        if (geocamCore.highlightedFeatureUuid != null) {
            var feature = geocamCore.featuresByUuidG[geocamCore.highlightedFeatureUuid];
            $(geocamCore).trigger("unhighlightFeature", [feature]);
            geocamCore.highlightedFeatureUuid = null;
        }
    },

    setSelectedFeature: function (uuid) {
        if (geocamCore.selectedFeatureUuid == uuid) {
            // do nothing
        } else {
            geocamCore.clearSelectedFeature();
            var feature = geocamCore.featuresByUuidG[uuid];
            $(geocamCore).trigger("selectFeature", [feature]);
            geocamCore.selectedFeatureUuid = uuid;
            
            geocamCore.viewIndexUuidG = uuid;
        }
    },

    clearSelectedFeature: function () {
        if (geocamCore.selectedFeatureUuid != null) {
            var feature = geocamCore.featuresByUuidG[geocamCore.selectFeatureUuid];
            $(geocamCore).trigger("unselectFeature", [feature]);
            geocamCore.selectedFeatureUuid = null;
        }
    },

    updateFeatures: function (newFeatures, diff) {
        $(geocamCore).trigger("updateFeatures", arguments);
    },

    notifyLoading: function () {
        $(geocamCore).trigger("notifyLoading", arguments);
    },

    notifyFeaturesInMapViewport: function (features) {
        $(geocamCore).trigger("notifyFeaturesInMapViewport", arguments);
    },

    setToFeatureDetail: function () {
        $(geocamCore).trigger("setToFeatureDetail", arguments);
    },

    setToFeatureEdit: function () {
        $(geocamCore).trigger("setToFeatureEdit", arguments);
    }

};
