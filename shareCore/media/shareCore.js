// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

var MAP_BACKEND;
var SCRIPT_NAME;
var SERVER_ROOT_URL;
var MEDIA_URL;
var itemsG = [];
var newItemsG = null;
var pageG = null;
var highlightedItemG = null;
var visibleItemsG = [];
var mapViewChangeTimeoutG = null;
var mapG = null;
var debugObjectG = null;

if (MAP_BACKEND == "earth") {
    google.load("earth", "1");
}

var MapViewer = new Class({
	isReady: false,

        initialize: function() {
	    // initialize the map
	    this.isReady = true;
	    setViewIfReady();
        },

        updateItems: function (diff) {
	    // add or delete features when we get an update
        },

        zoomToFit: function () {
	    // zoom map bounds to fit all markers
        },

        getViewport: function () {
	    // get viewport coords as a string, which will be stored in session state.
	    // the format of the string can vary depending on the back end, but
	    // calling setViewport() with the result must return the viewport to the
	    // same place.
	    return "";
        },

        setViewport: function (view) {
	    // set viewport coords (see getViewport)
        },

        getVisibleItems: function (items) {
	    // get the subset of items which are visible within the current map viewport
	    return items;
        },

        highlightItem: function(item) {
	    // highlight the given item in the map view.
        },

        unhighlightItem: function(item) {
	    // unhighlight the given item in the map view
        }

});

var EarthApiMapViewer = new Class({
        Extends: MapViewer,

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

        initialize: function () {

            var self = this;
            google.earth.createInstance('map3d',
                                        function(instance) {
                                            return self.handleCreateInstanceDone(instance);
                                        },
                                        function(instance) {
                                            // ignore error
                                        });
        },

        updateItems: function (diff) {
            var self = this;

            $.each(diff.itemsToDelete,
                   function (i, item) {
                       var parent = item.mapObject.getParentNode();
                       parent.getFeatures().removeChild(item.mapObject);
                   });
            
            if (diff.itemsToAdd.length > 0) {
                if (self.allFeaturesFolder == null) {
                    self.allFeaturesFolder = self.ge.createFolder("allFeatures");
                    self.ge.getFeatures().appendChild(self.allFeaturesFolder);
                }

                $.each(diff.itemsToAdd,
                       function (i, item) {
                           var kml = wrapKml(getItemKml(item));
                           var geItem = self.ge.parseKml(kml);
                           self.allFeaturesFolder.getFeatures().appendChild(geItem);
                           item.mapObject = geItem;
                       });

                this.setListeners(diff.itemsToAdd);
            }

            if (diff.itemsToDelete.length > 0 || diff.itemsToAdd.length > 0) {
                //self.zoomToFit();
                setGalleryToVisibleSubsetOf(itemsG);
            }
        },

        getVisibleItems: function (items) {
            var self = this;
            var globeBounds = self.getViewBounds();
            
            var visibleItems = [];
            $.each(items,
                   function (i, item) {
                       var placemark = item.mapObject;
                       if (self.itemIntersectsBounds(item, globeBounds)) {
                           visibleItems.push(item);
                       }
                   });

            return visibleItems;
        },

        zoomToFit: function () {
            this.gex.util.flyToObject(this.allFeaturesFolder);
        },

        highlightItem: function(item) {
            item.mapObject.getStyleSelector().getIconStyle().setScale(1.5);
        },

        unhighlightItem: function(item) {
            item.mapObject.getStyleSelector().getIconStyle().setScale(1);
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
            
            this.isReady = true;
            setViewIfReady();
        },

        itemIntersectsBounds: function (item, bounds) {
            var lat = item.lat;
	    if (lat == null) {
		return true; // non-geotagged items are always "inside bounds"
	    }
            var lon = item.lon;
            return ((bounds.getSouth() <= lat) && (lat <= bounds.getNorth())
                    && (bounds.getWest() <= lon) && (lon <= bounds.getEast()));
        },

        showBalloonForItem: function(uuid) {
            var item = itemsByUuidG[uuid];
            var balloon = this.ge.createHtmlStringBalloon('');
            
            var placemark = item.mapObject;
            balloon.setFeature(placemark);
            
            balloon.setContentString(getItemBalloonHtml(item));
            this.ge.setBalloon(balloon);
        },

        setListeners: function(items) {
            var self = this;
            $.each(items,
                   function (i, item) {
                       var placemark = item.mapObject;
                       google.earth.addEventListener(placemark, 'mouseover',
                                                     function (uuid) {
                                                         return function(event) {
                                                             highlightItem(uuid, doMapHighlight=false);
                                                         }
                                                     }(item.uuid));
                       google.earth.addEventListener(placemark, 'mouseout',
                                                     function (uuid) {
                                                         return function(event) {
                                                             unhighlightItem(uuid, doMapUnhighlight=false);
                                                         }
                                                     }(item.uuid));
                       google.earth.addEventListener(placemark, 'click',
                                                     function (uuid) {
                                                         return function(event) {
                                                             event.preventDefault();
                                                             self.showBalloonForItem(uuid);
                                                         }
                                                     }(item.uuid));
                   });
            
            if (!this.listenersInitialized) {
                google.earth.addEventListener(this.ge.getView(), 'viewchangeend', handleMapViewChange);
            }
            this.listenersInitialized = true;
        },

        getViewBounds: function() {
            return this.ge.getView().getViewportGlobeBounds();
        }

    });

var MapsApiMapViewer = new Class({
        Extends: MapViewer,

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

        initialize: function() {
            //var latlng = new google.maps.LatLng(37, -120);
            var myOptions = {
                /*zoom: 4,
                  center: latlng,*/
                mapTypeId: google.maps.MapTypeId.HYBRID
            };
            this.gmap = new google.maps.Map(document.getElementById("map3d_container"), myOptions);
            if (viewportG != "") {
                this.setViewport(viewportG);
                this.boundsAreSet = true;
            }
            this.isReady = true;

            setViewIfReady();
        },

        updateItems: function (diff) {
            var self = this;

            $.each(diff.itemsToDelete,
                   function (i, item) {
                       self.removeItemFromMap(item);
                   });
            
            if (diff.itemsToAdd.length > 0) {
                $.each(diff.itemsToAdd,
                       function (i, item) {
                           self.addItem(item);
                       });
            }
            this.setListeners(diff.itemsToAdd);

            if (diff.itemsToDelete.length > 0 || diff.itemsToAdd.length > 0) {
                if (!this.boundsAreSet) {
                    this.zoomToFit();
                }
                // used to call setGalleryToVisibleSubsetOf(itemsG)
                // here, but handleMapViewChange() gives the map backend
                // some time to adjust after the zoomToFit() call
                handleMapViewChange();
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

        getVisibleItems: function (items) {
            var bounds = this.gmap.getBounds();
            
            var visibleItems = [];
            var self = this;
            $.each(items,
                   function (i, item) {
                       if (self.itemIntersectsBounds(item, bounds)) {
                           visibleItems.push(item);
                       }
                   });
            return visibleItems;
        },

        highlightItem: function(item) {
            if (item.mapObject != null && item.mapObject.current != item.mapObject.highlight) {
                this.addToMap(item.mapObject.highlight);
                this.removeFromMap(item.mapObject.normal);
                item.mapObject.current = item.mapObject.highlight;
            }
        },

        unhighlightItem: function(item) {
            if (item.mapObject != null && item.mapObject.current != item.mapObject.normal) {
                this.addToMap(item.mapObject.normal);
                this.removeFromMap(item.mapObject.highlight);
                item.mapObject.current = item.mapObject.normal;
            }
        },

        /**********************************************************************
         * helper functions
         **********************************************************************/

        removeItemFromMap: function (item) {
            var self = this;
            if (item.mapObject == null) {
                // nothing to remove
            } else if (item.type == "Track") {
                for (var i=0; i < item.mapObject.polylines.length; i++) {
                    var polyline = item.mapObject.polylines[i];
                    self.removeFromMap(polyline);
                }
            } else {
                self.removeFromMap(item.mapObject.normal);
                self.removeFromMap(item.mapObject.highlight);
            }
        },

        itemIntersectsBounds: function (item, bounds) {
            if (item.minLat == null) {
                return true;
            } else {
                var ibounds = new google.maps.LatLngBounds();
                ibounds.extend(new google.maps.LatLng(item.minLat, item.minLon));
                ibounds.extend(new google.maps.LatLng(item.maxLat, item.maxLon));
                return ibounds.intersects(bounds);
            }
        },

        addMarker: function (item) {
            var self = this;

            var iconUrl = getIconMapUrl(item);
            item.mapObject = {normal: self.getMarker(item, 0.7),
                              highlight: self.getMarker(item, 1.0)};

            var markers = [item.mapObject.normal, item.mapObject.highlight];
            $.each
            (markers,
             function (j, marker) {
                google.maps.event.addListener
                    (marker, 'mouseover',
                     function (uuid) {
                        return function () {
                            highlightItem(uuid, doMapHighlight=false);
                        }
                    }(item.uuid));
                google.maps.event.addListener
                    (marker, 'mouseout',
                     function (uuid) {
                        return function () {
                            unhighlightItem(uuid, doMapUnhighlight=false);
                        }
                    }(item.uuid));
                google.maps.event.addListener
                    (marker, 'click',
                     function (uuid) {
                        return function () {
                            self.showBalloonForItem(uuid);
                        }
                    }(item.uuid));
            });

            self.unhighlightItem(item); // add to map in 'normal' state
        },

        addTrack: function (item) {
            var self = this;
            var trackLines = item.geometry.geometry;
            var path = [];
            item.mapObject = {polylines: []};
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
                       item.mapObject.polylines.push(polyline);
                   });
        },

        addItem: function (item) {
            if (item.minLat == null) {
                return; // skip non-geotagged items
            }

            if (isImage(item)) {
                this.addMarker(item);
            } else if (item.type == 'Track') {
                this.addTrack(item);
            }
        },

        getMarker: function (item, scale) {
            var position = new google.maps.LatLng(item.lat, item.lon);
            var iconUrl = getIconMapRotUrl(item);
            var iconSize = new google.maps.Size(item.icon.rotSize[0], item.icon.rotSize[1]);
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
            $.each(itemsG,
                   function (i, item) {
                       if (item.minLat != null) {
                           var itemBounds = new google.maps.LatLngBounds
                               (new google.maps.LatLng(item.minLat, item.minLon),
                                new google.maps.LatLng(item.maxLat, item.maxLon));
                           bounds.union(itemBounds);
                       }
                   });
            return bounds;
        },

        showBalloonForItem: function(uuid) {
            var item = itemsByUuidG[uuid];

            if (this.balloon != null) {
                this.balloon.close();
            }
            this.balloon = new google.maps.InfoWindow({content: getItemBalloonHtml(item)});
            this.balloon.open(this.gmap, item.mapObject.current);
        },

        setListeners: function(items) {
            var self = this;
            /*
            $.each
            (items,
             function (i, item) {
                var markers = [item.mapObject.normal, item.mapObject.highlight];
                $.each
                (markers,
                 function (j, marker) {
                    google.maps.event.addListener
                        (marker, 'mouseover',
                         function (uuid) {
                            return function () {
                                highlightItem(uuid, doMapHighlight=false);
                            }
                        }(item.uuid));
                    google.maps.event.addListener
                        (marker, 'mouseout',
                         function (uuid) {
                            return function () {
                                unhighlightItem(uuid, doMapUnhighlight=false);
                            }
                        }(item.uuid));
                    google.maps.event.addListener
                        (marker, 'click',
                         function (uuid) {
                            return function () {
                                self.showBalloonForItem(uuid);
                            }
                        }(item.uuid));
                });
            });
            */
            if (!this.mainListenerInitialized) {
                google.maps.event.addListener(this.gmap, 'bounds_changed', handleMapViewChange);
                this.mainListenerInitialized = true;
            }
        }

    });

function init() {
    // fetch JSON items and start map loading in parallel
    if (MAP_BACKEND == "earth") {
        mapG = new EarthApiMapViewer();
    } else if (MAP_BACKEND == "maps") {
        mapG = new MapsApiMapViewer();
    } else {
	mapG = new MapViewer();
    }
    if (queryG != "") {
        var searchBox = $('#searchBox');
        searchBox.val(queryG);
        searchBox.css('color', '#000');
    }
    setViewIfReady();
    // set up menus
    //$(function() { $('#jd_menu').jdMenu(); });
}

function reloadItems(query) {
    var url = SCRIPT_NAME + "gallery.json";
    if (query != null) {
        url += '?q=' + escape(query);
    }
    $("#gallery").html('Searching...');
    $.getJSON(url,
	      function (items) {
                  newItemsG = items;
                  setViewIfReady();
              });
    setSessionVars({'q': query});
    return false;
}

function uuidMap(items) {
    var result = {};
    $.each(items,
           function (i, item) {
               result[item.uuid] = item;
           });
    return result;
}

function diffItems(oldItems, newItems) {
    $.each(oldItems,
           function (i, item) {
               item.keep = false;
           });

    var oldItemsByUuid = uuidMap(oldItems);

    var diff = {};
    diff.itemsToAdd = [];
    $.each(newItems,
           function (i, item) {
               var matchingOldItem = oldItemsByUuid[item.uuid];
               if (matchingOldItem == null || matchingOldItem.version != item.version) {
                   diff.itemsToAdd.push(item);
               } else {
                   matchingOldItem.keep = true;
                   if (matchingOldItem.mapObject != undefined) {
                       item.mapObject = matchingOldItem.mapObject;
                   }
               }
           });
    
    diff.itemsToDelete = [];
    $.each(oldItems,
           function (i, item) {
               if (!item.keep) {
                   diff.itemsToDelete.push(item);
               }
           });

    return diff;
}

function getObjectThumbnailUrl(item, width) {
    if (item.type == "Track") {
        // FIX: should have thumbnails generated so we can respect width argument
        return MEDIA_URL + "share/gpsTrack.png";
    } else {
        // for images
        return getThumbnailUrl(item, width);
    }
}

function getObjectThumbSize(item) {
    if (item.type == "Track") {
        return [160, 120];
    } else {
        return [item.w, item.h];
    }
}

function getItemBalloonHtml(item) {
    var w0 = DESC_THUMB_SIZE[0];
    var scale = DESC_THUMB_SIZE[0] / GALLERY_THUMB_SIZE[0];
    var galThumbSize = getObjectThumbSize(item);
    var tw = galThumbSize[0];
    var th = galThumbSize[1];
    return ''
        + '<div>'
        + '  <a href="' + getViewerUrl(item) + '"'
        + '     title="Show high-res view">'
        + '  <img\n'
        + '    src="' + getObjectThumbnailUrl(item, w0) + '"\n'
        + '    width="' + tw*scale + '"\n'
        + '    height="' + th*scale + '"\n'
        + '    border="0"'
        + '  />\n'
        + ' </a>\n'
        + '  ' + getCaptionHtml(item)
        + '  <a href="' + getViewerUrl(item) + '">\n'
        + '    Download full-res image'
        + '  </a>\n'
        + '</div>\n';
}

function getIconGalleryUrl(item) {
    return MEDIA_URL + 'share/map/' + item.icon.name + '.png';
}

function getIconMapUrl(item) {
    return MEDIA_URL + 'share/map/' + item.icon.name + 'Point.png';
}

function getIconMapRotUrl(item) {
    return MEDIA_URL + 'share/mapr/' + item.icon.rotName + '.png';
}

function getGalleryThumbHtml(item) {
    var w0 = GALLERY_THUMB_SIZE[0];
    var h0 = GALLERY_THUMB_SIZE[1];
    var galThumbSize = getObjectThumbSize(item);
    var tw = galThumbSize[0];
    var th = galThumbSize[1];
    return "<td"
	+ " id=\"" + item.uuid + "\""
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
	+ " src=\"" + getIconGalleryUrl(item)  + "\""
	+ " width=\"16\""
	+ " height=\"16\""
	+ " style=\"position: absolute; z-index: 100;\""
	+ "/>"
	+ "<img"
	+ " src=\"" + getObjectThumbnailUrl(item, w0) + "\""
	+ " width=\"" + tw + "\""
	+ " height=\"" + th + "\""
	+ "/>"
	+ "</div>"
	+ "</td>";
}

function getHostUrl(noHostUrl) {
    return window.location.protocol + '//' + window.location.host;
}

function getImageKml(item) {
    var iconUrl = getHostUrl() + getIconMapUrl(item);
    return ''
	+ '<Placemark id="' + item.uuid + '">\n'
	+ '  <Style>\n'
	+ '    <IconStyle>\n'
	+ '      <Icon>\n'
	+ '        <href>' + iconUrl + '</href>\n'
	+ '      </Icon>\n'
	+ '      <heading>' + item.yaw + '</heading>\n'
	+ '    </IconStyle>\n'
	+ '  </Style>\n'
	+ '  <Point>\n'
	+ '    <coordinates>' + item.lon + ',' + item.lat + '</coordinates>\n'
	+ '  </Point>\n'
	+ '</Placemark>\n';
}

function getTrackLine(track) {
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
}

function getTrackKml(item) {
    var iconUrl = getHostUrl() + getIconMapUrl(item);
    result = ''
	+ '<Placemark id="' + item.uuid + '">\n'
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
    var coords = item.geometry.geometry;
    for (var i=0; i < coords.length; i++) {
        result += getTrackLine(coords[i]);
    }
    result += ''
        + '  </MultiGeometry>\n'
	+ '</Placemark>\n';

    return result;
}

function getItemKml(item) {
    if (isImage(item)) {
        return getImageKml(item);
    } else if (item.type == "Track") {
        return getTrackKml(item);
    } else {
        return "";
    }
}

function wrapKml(text) {
    return '<?xml version="1.0" encoding="UTF-8"?>\n'
	+ '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        + text
        + '</kml>';
}

function getKmlForItems(items) {
    var kml = ''
	+ '  <Document id="allFeatures">\n';
    $.each(items,
           function (uuid, item) {
               kml += getItemKml(item);
           })
    kml += ''
	+ '  </Document>\n';
    return wrapKml(kml);
}

function getPagerHtml(numItems, pageNum, pageNumToUrl) {
    function pg0(pageNum, text) {
        return '<a href="' + pageNumToUrl(pageNum) + '">' + text + '</a>';
    }
    
    function pg(pageNum) {
        return pg0(pageNum, pageNum);
    }
    
    function disabled(text) {
        return '<span style="color: #999999">' + text + '</span>';
    }

    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    var numPages = Math.ceil(numItems / pageSize);
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
}

function getGalleryHtml(items, pageNum) {
    html = "<table style=\"margin: 0px 0px 0px 0px; padding: 0px 0px 0px 0px; background-color: #ddd;\">";
    html += '<tr><td colspan="3">';
    html += getPagerHtml(items.length, pageNum,
                         function (pageNum) {
                             return 'javascript:setPage(visibleItemsG,' + pageNum + ')';
                         });
    //html += '<div style="float: right;">Hide</div>';
    html += '</td></tr>';
    for (var r=0; r < GALLERY_PAGE_ROWS; r++) {
	html += "<tr>";
	for (var c=0; c < GALLERY_PAGE_COLS; c++) {
	    var i = ((pageNum-1)*GALLERY_PAGE_ROWS + r)*GALLERY_PAGE_COLS + c;
	    if (i < items.length) {
		var item = items[i];
		html += getGalleryThumbHtml(item);
	    }
	}
	html += "</tr>";
    }
    html += "</table>";
    return html;
}

function getItemPage(item, visibleItems) {
    // get the page that this item appears on among the
    // visible items -- we use this to set the page before
    // we try to highlight the item in the gallery
    var index = item.index;
    var visibleIndex = 0;
    var i = 0;
    $.each(visibleItems,
           function (uuid, item) {
               if (item.index >= index) {
                   visibleIndex = i;
                   return false; // (breaks .each)
               }
               i++;
           });
    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    return Math.floor(visibleIndex / pageSize) + 1;
}

function handleMapViewChange() {
    if (mapViewChangeTimeoutG != null) {
	// avoid handling the same move many times -- clear the old timeout first
	clearTimeout(mapViewChangeTimeoutG);
    }
    mapViewChangeTimeoutG = setTimeout(function () {
	    setGalleryToVisibleSubsetOf(itemsG);
	}, 250);
}

function itemListsEqual(a, b) {
    // itemLists are defined to be equal if their items have the same uuids.
    // this must be true if they have the same length and the uuids of b
    // are a subset of the uuids of a.

    if (a.length != b.length) return false;

    var amap = uuidMap(a);
    for (var i=0; i < b.length; i++) {
        if (amap[b[i].uuid] == undefined) {
            return false;
        }
    }

    return true;
}

function setSessionVars(varMap) {
    var url = SCRIPT_NAME + 'setVars';
    var sep = '?';
    $.each(varMap,
           function (key, val) {
               url += sep + key + '=' + escape(val);
               sep = '&';
           });
    $.get(url);
}

function setGalleryToVisibleSubsetOf(items) {
    if (mapG.boundsAreSet) {
        setSessionVars({'v': mapG.getViewport()});
    }
    setGalleryItems(mapG.getVisibleItems(items), items);
}

function setPage(visibleItems, pageNum, force) {
    if (pageG == pageNum && !force) return;

    if (visibleItems.length != 0) {
        // set gallery html
        $("#gallery").html(getGalleryHtml(visibleItems, pageNum));
    
        // set gallery listeners
        const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
        for (var j=0; j < pageSize; j++) {
            var i = (pageNum-1)*pageSize + j;
            if (i < visibleItems.length) {
                var item = visibleItems[i];
                $("td#" + item.uuid).hover(
                                           function(uuid) {
                                               return function() {
                                                   highlightItem(uuid, doMapHighlight=true);
                                               }
                                           }(item.uuid),
                                           function(uuid) {
                                               return function() {
                                                   unhighlightItem(uuid, doMapUnhighlight=true);
                                               }
                                           }(item.uuid)
                                           );
                $("td#" + item.uuid).click(
                                           function(uuid) {
                                               return function() {
                                                   mapG.showBalloonForItem(uuid);
                                               }
                                           }(item.uuid)
                                           );
            }
        }
    }

    pageG = pageNum;
}

function setGalleryItems(visibleItems, allItems) {
    if (itemListsEqual(visibleItemsG, visibleItems)) return;

    fhtml = (visibleItems.length) + ' of '
	+ (allItems.length) + ' features in view';
    $('#featuresOutOfView').html(fhtml);

    setPage(visibleItems, 1, force=true);
    visibleItemsG = visibleItems;
}

function setView(oldItems, newItems) {
    if (newItems.length == 0) {
        if (queryG == "") {
            $("#gallery").html("No features in DB yet.");
        } else {
            $("#gallery").html("No matches found.");
        }
    }
    var diff = diffItems(oldItems, newItems);
    mapG.updateItems(diff);
}

function setViewIfReady() {
    if (mapG != null && mapG.isReady && newItemsG != null) {
        $.each(newItemsG,
               function (i, item) {
                   item.index = i;
               });
        var oldItems = itemsG;
        itemsG = newItemsG;
        itemsByUuidG = uuidMap(itemsG);
        newItemsG = null;
	setView(oldItems, itemsG);
    }
}

function highlightItem(uuid, doMapHighlight) {
    if (highlightedItemG != uuid) {
	if (highlightedItemG != null) {
	    unhighlightItem(highlightedItemG, doMapHighlight);
	}

	var item = itemsByUuidG[uuid];

	setPage(visibleItemsG, getItemPage(item, visibleItemsG));
	$("td#" + item.uuid + " div").css({backgroundColor: 'red'});
	
	$("#caption").html(getCaptionHtml(item)); // add the rest of the preview data

	if (doMapHighlight) {
            mapG.highlightItem(item);
	}

	highlightedItemG = uuid;
    }
}

function unhighlightItem(uuid, doMapUnhighlight) {
    if (highlightedItemG == uuid) {
	var item = itemsByUuidG[uuid];
	
	$("td#" + item.uuid + " div").css({backgroundColor: ''});
	
	$("#caption").html('');

        if (doMapUnhighlight) {
            mapG.unhighlightItem(item);
        }

	highlightedItemG = null;
    }
}

