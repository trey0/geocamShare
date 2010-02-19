var ge; // conventional name for Google Earth plugin instance

var SCRIPT_NAME;
var SERVER_ROOT_URL;
var MEDIA_URL;
var gexG;
var itemsG = null;
var pageG = null;
var highlightedItemG = null;
var earthLoadedG = false;
var visibleItemsG = [];
var mapViewChangeTimeoutG = null;

/*
var lineStringG;
*/

google.load("earth", "1");

function init() {
    // fetch JSON items and start GE plugin loading in parallel
    google.earth.createInstance('map3d', handleCreateInstanceDone, handleCreateInstanceFailed);
    $.getJSON(SCRIPT_NAME + "/share/gallery.json",
	      function(items) {
		  itemsG = items;
		  setViewIfReady();
	      });
    // set up menus
    $(function() { $('#jd_menu').jdMenu(); });
}

function addGeDomObjectToMap(geDomObject) {
    ge.getFeatures().appendChild(geDomObject);
    gexG.util.flyToObject(geDomObject);
}

function addItemsToMap(items) {
    var kml = getKml(items);
    var geDomObject = ge.parseKml(kml);
    addGeDomObjectToMap(geDomObject);
}

function getGalleryThumbHtml(item) {
    var w0 = GALLERY_THUMB_SIZE[0];
    var h0 = GALLERY_THUMB_SIZE[1];
    return "<td"
	+ " id=\"" + item.id + "\""
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
	+ " src=\"" + MEDIA_URL + "share/" + item.icon  + ".png\""
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
    var iconUrl = getHostUrl() + MEDIA_URL + 'share/' + item.icon + 'Point.png';
    return ''
	+ '<Placemark id="' + item.id + '">\n'
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

function getKml(items) {
    var kml = ''
	+ '<?xml version="1.0" encoding="UTF-8"?>\n'
	+ '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
	+ '  <Document id="allFeatures">\n';
    for (var i=0; i < items.length; i++) {
	kml += getPlacemarkKml(items[i]);
    }
    kml += ''
	+ '  </Document>\n'
	+ '</kml>\n';
    return kml;
}

function pg0(page, text) {
    return '<a href="javascript:setPage(visibleItemsG,' + page + ')">' + text + '</a>';
}

function pg(page) {
    return pg0(page, page);
}

function getPagerHtml(items, pageNum) {
    const pageSize = GALLERY_PAGE_ROWS*GALLERY_PAGE_COLS;
    var numPages = Math.ceil(items.length / pageSize);

    ret = [];
    if (pageNum > 1) {
	ret.push(pg0(pageNum-1, '&lt;&lt;'));
	ret.push(pg(1));
    }
    if (pageNum > 2) {
	if (pageNum > 3) {
	    ret.push('...');
	}
	ret.push(pg(pageNum-1));
    }
    ret.push('' + pageNum);
    if (pageNum < numPages-1) {
	ret.push(pg(pageNum+1));
	if (pageNum < numPages-2) {
	    ret.push('...');
	}
    }
    if (pageNum < numPages) {
	ret.push(pg(numPages));
	ret.push(pg0(pageNum+1, '&gt;&gt;'));
    }
    if (ret.length != 0) {
	return 'pages:&nbsp;' + ret.join('&nbsp;');
    } else {
	return '';
    }
}

function getGalleryHtml(items, pageNum) {
    html = "<table style=\"margin: 0px 0px 0px 0px; padding: 0px 0px 0px 0px; background-color: #ddd;\">";
    html += '<tr><td colspan="3">';
    html += getPagerHtml(items, pageNum)
    html += '<div style="float: right;">Hide</div>';
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
    
    var placemark = gexG.dom.getObjectById(item.id);
    balloon.setFeature(placemark);
    
    var w0 = DESC_THUMB_SIZE[0];
    var scale = DESC_THUMB_SIZE[0] / GALLERY_THUMB_SIZE[0];
    var content = ''
	+ '<div>'
	+ '  <img\n'
	+ '    src="' + getThumbnailUrl(item, w0) + '"\n'
	+ '    width="' + item.w*scale + '"\n'
	+ '    height="' + item.h*scale + '"\n'
	+ '  />'
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
	var placemark = gexG.dom.getObjectById(item.id);
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

    google.earth.addEventListener(ge.getView(), 'viewchangeend', handleMapViewChange);
}

function geomIsInsideBounds(geom, bounds) {
    var lat = geom.getLatitude();
    var lon = geom.getLongitude();
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
	var placemark = gexG.dom.getObjectById(item.id);
	if (geomIsInsideBounds(placemark.getGeometry(), globeBounds)) {
	    visibleItems.push(item);
	}
    }
    return visibleItems;
}

function listsHaveDifferentRequestIds(a, b) {
    if (a.length != b.length) return true;

    var adict = {};
    for (var i=0; i < a.length; i++) {
	adict[a[i].id] = true;
    }
    for (var i=0; i < b.length; i++) {
	if (! adict[b[i].id]) {
	    return true;
	}
    }
    return false;
}

function setGalleryToVisibleSubsetOf(items) {
    setGalleryItems(getVisibleItems(items));
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
	    $("td#" + item.id).hover(
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
	    $("td#" + item.id).click(
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

function setGalleryItems(visibleItems, pageNum) {
    if (!listsHaveDifferentRequestIds(visibleItemsG, visibleItems)) return;

    fhtml = (visibleItems.length) + ' of '
	+ (itemsG.length) + ' features in view';
    $('#featuresOutOfView').html(fhtml);

    setPage(visibleItems, 1, force=true);
    visibleItemsG = visibleItems;
}

function setView(items) {
    annotateItems(items);
    addItemsToMap(items);
    setMapListeners(items);
    setGalleryToVisibleSubsetOf(items);
}

function setViewIfReady() {
    if (earthLoadedG && itemsG != null) {
	setView(itemsG);
    }
}

function highlightItem(index, doMapHighlight) {
    if (highlightedItemG != index) {
	if (highlightedItemG != null) {
	    unhighlightItem(highlightedItemG);
	}

	var item = itemsG[index];

	setPage(visibleItemsG, getItemPage(item, visibleItemsG));
	$("td#" + item.id + " div").css({backgroundColor: 'red'});
	
	$("#caption").html(getCaptionHtml(item)); // add the rest of the preview data

	if (doMapHighlight) {
	    placemark = gexG.dom.getObjectById(item.id);
	    placemark.getStyleSelector().getIconStyle().setScale(1.5);
	}

	highlightedItemG = index;
    }
}

function unhighlightItem(index) {
    if (highlightedItemG == index) {
	var item = itemsG[index];
	
	$("td#" + item.id + " div").css({backgroundColor: ''});
	
	$("#caption").html('');

	placemark = gexG.dom.getObjectById(item.id);
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
    var allFeatures = gexG.dom.getObjectById('allFeatures');
    gexG.util.flyToObject(allFeatures);
}
