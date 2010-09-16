// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

var share = {};

share.core = {

    // these variables will be initialized to constant values derived from django settings
    MAP_BACKEND: null,
    SCRIPT_NAME: null,
    SERVER_ROOT_URL: null,
    MEDIA_URL: null,
    DATA_URL: null,

    // globals
    featuresG: [],
    newFeaturesG: null,
    pageG: null,
    highlightedFeatureG: null,
    visibleFeaturesG: [],
    mapViewChangeTimeoutG: null,
    mapG: null,
    galleryG: null,
    debugObjectG: null,
    widgetManagerG: null,
    viewportG: "",
    
    reloadFeatures: function (query) {
        var url = share.core.SCRIPT_NAME + "gallery.json";
        if (query != null) {
            url += '?q=' + escape(query);
        }
        $("#gallery").html('Searching...');
        $.getJSON(url,
	          function (features) {
                      share.core.newFeaturesG = features;
                      share.core.setViewIfReady();
                  });
        share.core.setSessionVars({'q': query});
        return false;
    },
    
    init: function () {
        // fetch JSON features and start map loading in parallel
        var mapFactory;
        if (share.core.MAP_BACKEND == "earth") {
            mapFactory = share.core.EarthApiMapViewer.factory;
        } else if (share.core.MAP_BACKEND == "maps") {
            mapFactory = share.core.MapsApiMapViewer.factory;
        } else {
            mapFactory = share.core.StubMapViewer.factory;
        }
        
        share.core.widgetManagerG = new share.core.WidgetManager();
        share.core.widgetManagerG.setWidgetForDomId("mapContainer", mapFactory);
        share.core.mapG = share.core.widgetManagerG.activeWidgets["mapContainer"];
        share.core.widgetManagerG.setWidgetForDomId("galleryContainer", share.core.Gallery.factory);
        share.core.galleryG = share.core.widgetManagerG.activeWidgets["galleryContainer"];
        
        if (share.core.queryG != "") {
            var searchBox = $('#searchBox');
            searchBox.val(share.core.queryG);
            searchBox.css('color', '#000');
        }
        share.core.setViewIfReady();
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
        
        var oldFeaturesByUuid = share.core.uuidMap(oldFeatures);
        
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
    
    getFeatureThumbnailUrl: function (feature, width) {
        if (feature.type == "Track") {
            // FIX: should have thumbnails generated so we can respect width argument
            return share.core.MEDIA_URL + "share/gpsTrack.png";
        } else {
            // for images
            return share.core.getThumbnailUrl(feature, width);
        }
    },
    
    getFeatureThumbSize: function (feature) {
        if (feature.type == "Track") {
            return [160, 120];
        } else {
            return [feature.w, feature.h];
        }
    },
    
    getFeatureBalloonHtml: function (feature) {
        var w0 = share.core.DESC_THUMB_SIZE[0];
        var scale = share.core.DESC_THUMB_SIZE[0] / share.core.GALLERY_THUMB_SIZE[0];
        var galThumbSize = share.core.getFeatureThumbSize(feature);
        var tw = galThumbSize[0];
        var th = galThumbSize[1];
        return ''
            + '<div>'
            + '  <a href="' + share.core.getViewerUrl(feature) + '"'
            + '     title="Show high-res view">'
            + '  <img\n'
            + '    src="' + share.core.getFeatureThumbnailUrl(feature, w0) + '"\n'
            + '    width="' + tw*scale + '"\n'
            + '    height="' + th*scale + '"\n'
            + '    border="0"'
            + '  />\n'
            + ' </a>\n'
            + '  ' + share.core.getCaptionHtml(feature)
            + '  <a href="' + share.core.getViewerUrl(feature) + '">\n'
            + '    Download full-res image'
            + '  </a>\n'
            + '</div>\n';
    },
    
    getIconGalleryUrl: function (feature) {
        return share.core.MEDIA_URL + 'share/map/' + feature.icon.name + '.png';
    },
    
    getIconMapUrl: function (feature) {
        return share.core.MEDIA_URL + 'share/map/' + feature.icon.name + 'Point.png';
    },
    
    getIconMapRotUrl: function (feature) {
        return share.core.MEDIA_URL + 'share/mapr/' + feature.icon.rotName + '.png';
    },
    
    getGalleryThumbHtml: function (feature) {
        var w0 = share.core.GALLERY_THUMB_SIZE[0];
        var h0 = share.core.GALLERY_THUMB_SIZE[1];
        var galThumbSize = share.core.getFeatureThumbSize(feature);
        var tw = galThumbSize[0];
        var th = galThumbSize[1];
        return "<td"
	    + " id=\"" + feature.uuid + "\""
	    + " style=\""
	    + " vertical-align: top;"
	    + " width: " + (w0+10) + "px;"
	    + " height: " + (h0+10) + "px;"
	    + " margin: 0px 0px 0px 0px;"
	    + " border: 0px 0px 0px 0px;"
	    + " padding: 0px 0px 0px 0px;"
	    + "\">"
	    + "<div"
	    + " style=\""
	    + " width: " + tw + "px;"
	    + " height: " + th + "px;"
	    + " margin: 0px 0px 0px 0px;"
	    + " border: 0px 0px 0px 0px;"
	    + " padding: 5px 5px 5px 5px;"
	    + "\">"
	    + "<img"
	    + " src=\"" + share.core.getIconGalleryUrl(feature)  + "\""
	    + " width=\"16\""
	    + " height=\"16\""
	    + " style=\"position: absolute; z-index: 100;\""
	    + "/>"
	    + "<img"
	    + " src=\"" + share.core.getFeatureThumbnailUrl(feature, w0) + "\""
	    + " width=\"" + tw + "\""
	    + " height=\"" + th + "\""
	    + "/>"
	    + "</div>"
	    + "</td>";
    },
    
    getHostUrl: function (noHostUrl) {
        return window.location.protocol + '//' + window.location.host;
    },
    
    getImageKml: function (feature) {
        var iconUrl = share.core.getHostUrl() + share.core.getIconMapUrl(feature);
        return ''
	    + '<Placemark id="' + feature.uuid + '">\n'
	    + '  <Style>\n'
	    + '    <IconStyle>\n'
	    + '      <Icon>\n'
	    + '        <href>' + iconUrl + '</href>\n'
	    + '      </Icon>\n'
	    + '      <heading>' + feature.yaw + '</heading>\n'
	    + '    </IconStyle>\n'
	    + '  </Style>\n'
	    + '  <Point>\n'
	    + '    <coordinates>' + feature.lon + ',' + feature.lat + '</coordinates>\n'
	    + '  </Point>\n'
	    + '</Placemark>\n';
    },
    
    getTrackLine: function (track) {
        result = ''
            + '    <LineString>\n'
            + '      <coordinates>\n';
        for (var i=0; i < track.length; i++) {
            var pt = track[i];
            result += '        ' + pt[0] + ',' + pt[1] + ',' + pt[2] + '\n'
        }
        result += ''
            + '      </coordinates>\n'
            + '    </LineString>\n';
        return result;
    },
    
    getTrackKml: function (feature) {
        var iconUrl = share.core.getHostUrl() + share.core.getIconMapUrl(feature);
        result = ''
	    + '<Placemark id="' + feature.uuid + '">\n'
	    + '  <Style>\n'
	    + '    <IconStyle>\n'
	    + '      <Icon>\n'
	    + '        <href>' + iconUrl + '</href>'
	    + '      </Icon>\n'
	    + '    </IconStyle>\n'
	    + '    <LineStyle>\n'
	    + '      <color>ff0000ff</color>\n'
	    + '      <width>4</width>\n'
	    + '    </LineStyle>\n'
	    + '  </Style>\n'
	    + '  <MultiGeometry>\n';
        var coords = feature.geometry.geometry;
        for (var i=0; i < coords.length; i++) {
            result += share.core.getTrackLine(coords[i]);
        }
        result += ''
            + '  </MultiGeometry>\n'
	    + '</Placemark>\n';
        
        return result;
    },
    
    getFeatureKml: function (feature) {
        if (share.core.isImage(feature)) {
            return share.core.getImageKml(feature);
        } else if (feature.type == "Track") {
            return share.core.getTrackKml(feature);
        } else {
            return "";
        }
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
                   kml += share.core.getFeatureKml(feature);
               })
            kml += ''
	    + '  </Document>\n';
        return share.core.wrapKml(kml);
    },
    
    getPagerHtml: function (numFeatures, pageNum, pageNumToUrl) {
        function pg0(pageNum, text) {
            return '<a href="' + pageNumToUrl(pageNum) + '">' + text + '</a>';
        }
        
        function pg(pageNum) {
            return pg0(pageNum, pageNum);
        }
        
        function disabled(text) {
            return '<span style="color: #999999">' + text + '</span>';
        }
        
        const pageSize = share.core.GALLERY_PAGE_ROWS*share.core.GALLERY_PAGE_COLS;
        var numPages = Math.ceil(numFeatures / pageSize);
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
    
    getGalleryHtml: function (features, pageNum) {
        html = "<table style=\"margin: 0px 0px 0px 0px; padding: 0px 0px 0px 0px; background-color: #ddd;\">";
        html += '<tr><td colspan="3">';
        html += share.core.getPagerHtml(features.length, pageNum,
                             function (pageNum) {
                                 return 'javascript:share.core.setPage(share.core.visibleFeaturesG,' + pageNum + ')';
                             });
        //html += '<div style="float: right;">Hide</div>';
        html += '</td></tr>';
        for (var r=0; r < share.core.GALLERY_PAGE_ROWS; r++) {
	    html += "<tr>";
	    for (var c=0; c < share.core.GALLERY_PAGE_COLS; c++) {
	        var i = ((pageNum-1)*share.core.GALLERY_PAGE_ROWS + r)*share.core.GALLERY_PAGE_COLS + c;
	        if (i < features.length) {
		    var feature = features[i];
		    html += share.core.getGalleryThumbHtml(feature);
	        }
	    }
	    html += "</tr>";
        }
        html += "</table>";
        return html;
    },
    
    getFeaturePage: function (feature, visibleFeatures) {
        // get the page that this feature appears on among the
        // visible features -- we use this to set the page before
        // we try to highlight the feature in the gallery
        var index = feature.index;
        var visibleIndex = 0;
        var i = 0;
        $.each(visibleFeatures,
               function (uuid, feature) {
                   if (feature.index >= index) {
                       visibleIndex = i;
                       return false; // (breaks .each)
                   }
                   i++;
               });
        const pageSize = share.core.GALLERY_PAGE_ROWS*share.core.GALLERY_PAGE_COLS;
        return Math.floor(visibleIndex / pageSize) + 1;
    },
    
    handleMapViewChange: function () {
        if (share.core.mapViewChangeTimeoutG != null) {
	    // avoid handling the same move many times -- clear the old timeout first
	    clearTimeout(share.core.mapViewChangeTimeoutG);
        }
        share.core.mapViewChangeTimeoutG = setTimeout(function () {
	    share.core.setGalleryToVisibleSubsetOf(share.core.featuresG);
	}, 250);
    },
    
    featureListsEqual: function (a, b) {
        // featureLists are defined to be equal if their features have the same uuids.
        // this must be true if they have the same length and the uuids of b
        // are a subset of the uuids of a.
        
        if (a.length != b.length) return false;
        
        var amap = share.core.uuidMap(a);
        for (var i=0; i < b.length; i++) {
            if (amap[b[i].uuid] == undefined) {
                return false;
            }
        }
        
        return true;
    },
    
    setSessionVars: function (varMap) {
        var url = share.core.SCRIPT_NAME + 'setVars';
        var sep = '?';
        $.each(varMap,
               function (key, val) {
                   url += sep + key + '=' + escape(val);
                   sep = '&';
               });
        $.get(url);
    },
    
    setGalleryToVisibleSubsetOf: function (features) {
        if (share.core.mapG.boundsAreSet) {
            share.core.setSessionVars({'v': share.core.mapG.getViewport()});
        }
        share.core.setGalleryFeatures(share.core.mapG.getVisibleFeatures(features), features);
    },
    
    setPage: function (visibleFeatures, pageNum, force) {
        if (share.core.pageG == pageNum && !force) return;
        
        if (visibleFeatures.length != 0) {
            // set gallery html
            $("#gallery").html(share.core.getGalleryHtml(visibleFeatures, pageNum));
            
            // set gallery listeners
            const pageSize = share.core.GALLERY_PAGE_ROWS*share.core.GALLERY_PAGE_COLS;
            for (var j=0; j < pageSize; j++) {
                var i = (pageNum-1)*pageSize + j;
                if (i < visibleFeatures.length) {
                    var feature = visibleFeatures[i];
                    $("td#" + feature.uuid).hover(
                        function(uuid) {
                            return function() {
                                share.core.widgetManagerG.setFeatureHighlighted(uuid, true);
                            }
                        }(feature.uuid),
                        function(uuid) {
                            return function() {
                                share.core.widgetManagerG.setFeatureHighlighted(uuid, false);
                            }
                        }(feature.uuid)
                    );
                    $("td#" + feature.uuid).click(
                        function(uuid) {
                            return function() {
                                share.core.widgetManagerG.setFeatureSelected(uuid, true);
                            }
                        }(feature.uuid)
                    );
                }
            }
        }
        
        share.core.pageG = pageNum;
    },
    
    setGalleryFeatures: function (visibleFeatures, allFeatures) {
        if (share.core.featureListsEqual(share.core.visibleFeaturesG, visibleFeatures)) return;
        
        fhtml = (visibleFeatures.length) + ' of '
	    + (allFeatures.length) + ' features in view';
        $('#featuresOutOfView').html(fhtml);
        
        share.core.setPage(visibleFeatures, 1, force=true);
        share.core.visibleFeaturesG = visibleFeatures;
    },
    
    setView: function (oldFeatures, newFeatures) {
        if (newFeatures.length == 0) {
            if (share.core.queryG == "") {
                $("#gallery").html("No features in DB yet.");
            } else {
                $("#gallery").html("No matches found.");
            }
        }
        var diff = share.core.diffFeatures(oldFeatures, newFeatures);
        share.core.mapG.updateFeatures(diff);
    },
    
    setViewIfReady: function () {
        if (share.core.mapG != null && share.core.mapG.isReady && share.core.newFeaturesG != null) {
            $.each(share.core.newFeaturesG,
                   function (i, feature) {
                       feature.index = i;
                   });
            var oldFeatures = share.core.featuresG;
            share.core.featuresG = share.core.newFeaturesG;
            share.core.featuresByUuidG = share.core.uuidMap(share.core.featuresG);
            share.core.newFeaturesG = null;
	    share.core.setView(oldFeatures, share.core.featuresG);
        }
    }
};
