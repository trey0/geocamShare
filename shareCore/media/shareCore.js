var ge; // conventional name for Google Earth plugin instance

var SCRIPT_NAME;
var SERVER_ROOT_URL;
var MEDIA_URL;
var gexG;
var itemsG = [];
var newItemsG = [];
var pageG = null;
var highlightedItemG = null;
var earthLoadedG = false;
var visibleItemsG = [];
var mapViewChangeTimeoutG = null;
var allFeaturesFolderG = null;
var earthListenersInitializedG = false;

/*
var lineStringG;
*/

google.load("earth", "1");

function init() {
    // fetch JSON items and start GE plugin loading in parallel
    google.earth.createInstance('map3d', handleCreateInstanceDone, handleCreateInstanceFailed);
    // set up menus
    $(function() { $('#jd_menu').jdMenu(); });
}

function reloadItems(query) {
    var url = SCRIPT_NAME + "/gallery.json";
    if (query != null) {
        url += '?q=' + query; // FIX: urlencode!
    }
    $.getJSON(url,
	      function (items) {
                  newItemsG = items;
                  setViewIfReady();
              });
    return false;
}

function diffItems(oldItems, newItems) {
    var oldItemsById = {};
    for (var i=0; i < oldItems.length; i++) {
        var item = oldItems[i];
        oldItemsById[item.uuid] = item;
        item.keep = false;
    }

    var diff = {};
    diff.itemsToAdd = [];
    for (var i=0; i < newItems.length; i++) {
        var item = newItems[i];
        var matchingOldItem = oldItemsById[item.uuid];
        if (matchingOldItem == null || matchingOldItem.version != item.version) {
            diff.itemsToAdd.push(item);
        } else {
            matchingOldItem.keep = true;
            item.domObject = matchingOldItem.domObject;
        }
    }
    
    diff.itemsToDelete = [];
    for (var i=0; i < oldItems.length; i++) {
        var item = oldItems[i];
        if (!item.keep) {
            diff.itemsToDelete.push(item);
        }
    }

    return diff;
}

function updateItemsInMap(diff) {
    if (diff.itemsToDelete != []) {
        for (var i=0; i < diff.itemsToDelete.length; i++) {
            var item = diff.itemsToDelete[i];
            var parent = item.domObject.getParentNode();
            parent.getFeatures().removeChild(item.domObject);
        }
    }

    if (diff.itemsToAdd != []) {
        var items = diff.itemsToAdd;

        if (allFeaturesFolderG == null) {
            allFeaturesFolderG = ge.createFolder("allFeatures");
            ge.getFeatures().appendChild(allFeaturesFolderG);
        }
        for (var i=0; i < items.length; i++) {
            var item = items[i];
            var kml = wrapKml(getPlacemarkKml(item));
            var geItem = ge.parseKml(kml);
            allFeaturesFolderG.getFeatures().appendChild(geItem);
            item.domObject = geItem;
        }
        zoomToFit();

        /*
        var kml = getKmlForItems(items);
        var geDomObject = ge.parseKml(kml);
        ge.getFeatures().appendChild(geDomObject);
        gexG.util.flyToObject(geDomObject);

        // cache getObjectById results to minimize walking the DOM
        allFeaturesFolderG = gexG.dom.getObjectById('allFeatures');
        for (var i=0; i < items.length; i++) {
            item = items[i];
            item.domObject = gexG.dom.getObjectById(item.uuid);
            }*/
    }
}

function getMapIconPrefix(item) {
    return item.icon + 'Point';
}

function getGalleryIconPrefix(item) {
    return item.icon;
}

function getGalleryThumbHtml(item) {
    var w0 = GALLERY_THUMB_SIZE[0];
    var h0 = GALLERY_THUMB_SIZE[1];
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
	+ " width: " + item.w + "px;"
	+ " height: " + item.h + "px;"
	+ " margin: 0px 0px 0px 0px;"
	+ " border: 0px 0px 0px 0px;"
	+ " padding: 5px 5px 5px 5px;"
	+ "\">"
	+ "<img"
	+ " src=\"" + MEDIA_URL + "share/" + getGalleryIconPrefix(item)  + ".png\""
	+ " width=\"16\""
	+ " height=\"16\""
	+ " style=\"position: absolute; z-index: 100;\""
	+ "/>"
	+ "<img"
	+ " src=\"" + getThumbnailUrl(item, w0) + "\""
	+ " width=\"" + item.w + "\""
	+ " height=\"" + item.h + "\""
	+ "/>"
	+ "</div>"
	+ "</td>";
}

function getHostUrl(noHostUrl) {
    return window.location.protocol + '//' + window.location.host;
}

function getPlacemarkKml(item) {
    var iconUrl = getHostUrl() + MEDIA_URL + 'share/' + getMapIconPrefix(item) + '.png';
    return ''
	+ '<Placemark id="' + item.uuid + '">\n'
	+ '  <Style>\n'
	+ '    <IconStyle>\n'
	+ '      <Icon>\n'
	+ '        <href>' + iconUrl + '</href>'
	+ '      </Icon>\n'
	+ '      <heading>' + item.yaw + '</heading>\n'
	+ '    </IconStyle>\n'
	+ '  </Style>\n'
	+ '  <Point>\n'
	+ '    <coordinates>' + item.lon + ',' + item.lat + '</coordinates>\n'
	+ '  </Point>\n'
	+ '</Placemark>\n';
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
    for (var i=0; i < items.length; i++) {
	kml += getPlacemarkKml(items[i]);
    }
    kml += ''
	+ '  </Document>\n';
    return wrapKml(kml);
}

function pg0(page, text) {
    return '<a href="javascript:setPage(visibleItemsG,' + page + ')">' + text + '</a>';
}

function pg(page) {
    return pg0(page, page);
}

function disabled(text) {
    return '<span style="color: #999999">' + text + '</span>';
}

function getPagerHtml(items, pageNum) {
    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    var numPages = Math.ceil(items.length / pageSize);
    var maxDisplayPages = Math.min(numPages, 8);
    var divWidth = maxDisplayPages * 15;

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
	if (pageNum > 3) {
	    ret.push('...');
	}
	ret.push(pg(pageNum-1));
    }
    if (numPages > 1) {
        ret.push('' + pageNum);
    }
    if (pageNum < numPages-1) {
	ret.push(pg(pageNum+1));
	if (pageNum < numPages-2) {
	    ret.push('...');
	}
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
    html += getPagerHtml(items, pageNum);
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
    for (var i=0; i < visibleItems.length; i++) {
	if (visibleItems[i].index >= index) {
	    visibleIndex = i;
	    break;
	}
    }
    //console.log('visibleIndex ' + visibleIndex);
    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    return Math.floor(visibleIndex / pageSize) + 1;
}

function annotateItems(items) {
    for (var i=0; i < items.length; i++) {
	items[i].index = i;
    }

    /*
    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    for (var p=1; p <= Math.ceil(items.length / pageSize); p++) {
	for (var j=0; j < pageSize; j++) {
	    var i = (p-1)*pageSize + j;
	    if (i < items.length) {
		items[i].page = p;
	    }
	}
	}*/
}

function showBalloonForItem(index) {
    var item = itemsG[index];
    var balloon = ge.createHtmlStringBalloon('');
    
    var placemark = item.domObject;
    balloon.setFeature(placemark);
    
    var w0 = DESC_THUMB_SIZE[0];
    var scale = DESC_THUMB_SIZE[0] / GALLERY_THUMB_SIZE[0];
    var content = ''
	+ '<div>'
	+ '  <a href="' + SCRIPT_NAME + '/' + item.task + '/' + item.uuid
	+ '" title="Show high-res view">'
	+ '  <img\n'
	+ '    src="' + getThumbnailUrl(item, w0) + '"\n'
	+ '    width="' + item.w*scale + '"\n'
	+ '    height="' + item.h*scale + '"\n'
	+ '  />'
	+ ' </a>'
	+ '  ' + getCaptionHtml(item)
	+ '</div>\n';
    balloon.setContentString(content);
    ge.setBalloon(balloon);
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

function setMapListeners(items) {
    for (var i=0; i < items.length; i++) {
	var item = items[i];
	var placemark = item.domObject;
	google.earth.addEventListener(placemark, 'mouseover',
				      function(index) {
					  return function(event) {
					      highlightItem(index, doMapHighlight=false);
					  }
				      }(item.index));
	google.earth.addEventListener(placemark, 'mouseout',
				      function(index) {
					  return function(event) {
					      unhighlightItem(index);
					  }
				      }(item.index));
	google.earth.addEventListener(placemark, 'click',
				      function(index) {
					  return function(event) {
					      event.preventDefault();
					      showBalloonForItem(index);
					  }
				      }(item.index));
    }

    if (!earthListenersInitializedG) {
        google.earth.addEventListener(ge.getView(), 'viewchangeend', handleMapViewChange);
    }
    earthListenersInitializedG = true;
}

function itemIsInsideBounds(item, bounds) {
    var lat = item.lat;
    var lon = item.lon;
    return ((bounds.getSouth() <= lat) && (lat <= bounds.getNorth())
	    && (bounds.getWest() <= lon) && (lon <= bounds.getEast()));
}

function getVisibleItems(items) {
    var globeBounds = ge.getView().getViewportGlobeBounds();
    /*
    console.log('globeBounds [' + globeBounds.getSouth() + ' .. ' + globeBounds.getNorth() + ']'
		+ ' [' + globeBounds.getWest() + ' .. ' + globeBounds.getEast() + ']');
    */

    var visibleItems = [];
    for (var i=0; i < items.length; i++) {
	var item = items[i];
	var placemark = item.domObject;
	if (itemIsInsideBounds(item, globeBounds)) {
	    visibleItems.push(item);
	}
    }
    return visibleItems;
}

function listsHaveDifferentIds(a, b) {
    if (a.length != b.length) return true;

    var adict = {};
    for (var i=0; i < a.length; i++) {
	adict[a[i].uuid] = true;
    }
    for (var i=0; i < b.length; i++) {
	if (! adict[b[i].uuid]) {
	    return true;
	}
    }
    return false;
}

function setGalleryToVisibleSubsetOf(items) {
    setGalleryItems(getVisibleItems(items), items);
}

function setPage(visibleItems, pageNum, force) {
    if (pageG == pageNum && !force) return;

    // set gallery html
    $("#gallery").html(getGalleryHtml(visibleItems, pageNum));
    
    // set gallery listeners
    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    for (var j=0; j < pageSize; j++) {
	var i = (pageNum-1)*pageSize + j;
	if (i < visibleItems.length) {
	    var item = visibleItems[i];
	    $("td#" + item.uuid).hover(
					    function(index) {
						return function() {
						    highlightItem(index, doMapHighlight=true);
						}
					    }(item.index),
					    function(index) {
						return function() {
						    unhighlightItem(index);
						}
					    }(item.index)
					    );
	    $("td#" + item.uuid).click(
					    function(index) {
						return function() {
						    showBalloonForItem(index);
						}
					    }(item.index)
					    );
	}
    }

    pageG = pageNum;
}

function setGalleryItems(visibleItems, allItems) {
    if (!listsHaveDifferentIds(visibleItemsG, visibleItems)) return;

    fhtml = (visibleItems.length) + ' of '
	+ (allItems.length) + ' features in view';
    $('#featuresOutOfView').html(fhtml);

    setPage(visibleItems, 1, force=true);
    visibleItemsG = visibleItems;
}

function setView(oldItems, newItems) {
    var diff = diffItems(oldItems, newItems);
    annotateItems(newItems);
    updateItemsInMap(diff);
    setMapListeners(diff.itemsToAdd);
    setGalleryToVisibleSubsetOf(newItems);
}

function setViewIfReady() {
    if (earthLoadedG && newItemsG != null) {
	setView(itemsG, newItemsG);
        itemsG = newItemsG;
    }
}

function highlightItem(index, doMapHighlight) {
    if (highlightedItemG != index) {
	if (highlightedItemG != null) {
	    unhighlightItem(highlightedItemG);
	}

	var item = itemsG[index];

	setPage(visibleItemsG, getItemPage(item, visibleItemsG));
	$("td#" + item.uuid + " div").css({backgroundColor: 'red'});
	
	$("#caption").html(getCaptionHtml(item)); // add the rest of the preview data

	if (doMapHighlight) {
	    var placemark = item.domObject;
	    placemark.getStyleSelector().getIconStyle().setScale(1.5);
	}

	highlightedItemG = index;
    }
}

function unhighlightItem(index) {
    if (highlightedItemG == index) {
	var item = itemsG[index];
	
	$("td#" + item.uuid + " div").css({backgroundColor: ''});
	
	$("#caption").html('');

	placemark = item.domObject;
	placemark.getStyleSelector().getIconStyle().setScale(1);

	highlightedItemG = null;
    }
}

function handleCreateInstanceDone(instance) {
    ge = instance;
    ge.getWindow().setVisibility(true);

    // add a navigation control
    ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);

    // add some layers
    ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, true);
    ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, true);

    gexG = new GEarthExtensions(ge);

    earthLoadedG = true;

    setViewIfReady();

    /*
    var url = SERVER_ROOT_URL + "share/data.kml";
    //google.earth.fetchKml(ge, url, addKmlToMap);
    gexG.util.displayKml(url, {flyToView: true});

    setTimeout(
	       function () {
		   $.getJSON(SERVER_ROOT_URL + "share/gallery.json", setView);
	       }, 1000); // hack, wait for placemarks to load
    */
}

function handleCreateInstanceFailed(errorCode) {
}

function newPlan() {
    setTimeout(function() { alert('newPlan'); }, 0);
}

function openPlan() {
    setTimeout(function() { alert('openPlan'); }, 0);
}

function zoomToFit() {
    gexG.util.flyToObject(allFeaturesFolderG);
}
