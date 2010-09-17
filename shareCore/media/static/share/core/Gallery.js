// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.Gallery = new Class(
{
    Extends: geocamShare.core.Widget,

    initialize: function (domId) {
        this.domId = domId;
        $("#" + this.domId).html
          ('<div id="geocamShare_core_gallery"></div>\n' +
           '<div id="geocamShare_core_galleryCaption"></div>\n');
        $("#geocamShare_core_gallery").html('Loading...');
    },

    updateFeatures: function (oldFeatures, newFeatures, diff) {
        // wait for notifyFeaturesInMapViewport()
    },

    notifyLoading: function () {
        $("#geocamShare_core_gallery").html('Searching...');
    },

    notifyFeaturesInMapViewport: function (visibleFeatures) {
        this.setPage(visibleFeatures, 1, force=true);
    },

    highlightFeature: function (feature) {
        this.setPage(geocamShare.core.visibleFeaturesG, this.getFeaturePage(feature, geocamShare.core.visibleFeaturesG));
        $("td#" + feature.uuid + " div").css({backgroundColor: 'red'});
	
        // add the rest of the preview data
        $("#geocamShare_core_galleryCaption").html(geocamShare.core.getCaptionHtml(feature));
    },
    
    unhighlightFeature: function (feature) {
        $("td#" + feature.uuid + " div").css({backgroundColor: ''});
	
        $("#caption").html('');
    },
    
    selectFeature: function (feature) {
        // currently a no-op
    },
    
    unselectFeature: function (feature) {
        // currently a no-op
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
        
        const pageSize = geocamShare.core.GALLERY_PAGE_ROWS*geocamShare.core.GALLERY_PAGE_COLS;
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
        html += this.getPagerHtml(features.length, pageNum,
                             function (pageNum) {
                                 return 'javascript:geocamShare.core.galleryG.setPage(geocamShare.core.visibleFeaturesG,' + pageNum + ')';
                             });
        //html += '<div style="float: right;">Hide</div>';
        html += '</td></tr>';
        for (var r=0; r < geocamShare.core.GALLERY_PAGE_ROWS; r++) {
	    html += "<tr>";
	    for (var c=0; c < geocamShare.core.GALLERY_PAGE_COLS; c++) {
	        var i = ((pageNum-1)*geocamShare.core.GALLERY_PAGE_ROWS + r)*geocamShare.core.GALLERY_PAGE_COLS + c;
	        if (i < features.length) {
		    var feature = features[i];
		    html += geocamShare.core.getGalleryThumbHtml(feature);
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
        const pageSize = geocamShare.core.GALLERY_PAGE_ROWS*geocamShare.core.GALLERY_PAGE_COLS;
        return Math.floor(visibleIndex / pageSize) + 1;
    },

    setPage: function (visibleFeatures, pageNum, force) {
        if (geocamShare.core.pageG == pageNum && !force) return;
        
        if (visibleFeatures.length == 0) {
            if (geocamShare.core.featuresG.length == 0) {
                if (geocamShare.core.queryG == "") {
                    $("#geocamShare_core_gallery").html("No features in DB yet.");
                } else {
                    $("#geocamShare_core_gallery").html("No matches found.");
                }
            } else {
                $("#geocamShare_core_gallery").html("No matching features within map viewport.  Try zoom to fit.");
            }
        } else {
            // set gallery html
            $("#geocamShare_core_gallery").html(this.getGalleryHtml(visibleFeatures, pageNum));
            
            // set gallery listeners
            const pageSize = geocamShare.core.GALLERY_PAGE_ROWS*geocamShare.core.GALLERY_PAGE_COLS;
            for (var j=0; j < pageSize; j++) {
                var i = (pageNum-1)*pageSize + j;
                if (i < visibleFeatures.length) {
                    var feature = visibleFeatures[i];
                    $("td#" + feature.uuid).hover(
                        function(uuid) {
                            return function() {
                                geocamShare.core.widgetManagerG.setFeatureHighlighted(uuid, true);
                            }
                        }(feature.uuid),
                        function(uuid) {
                            return function() {
                                geocamShare.core.widgetManagerG.setFeatureHighlighted(uuid, false);
                            }
                        }(feature.uuid)
                    );
                    $("td#" + feature.uuid).click(
                        function(uuid) {
                            return function() {
                                geocamShare.core.widgetManagerG.setFeatureSelected(uuid, true);
                            }
                        }(feature.uuid)
                    );
                }
            }
        }
        
        geocamShare.core.pageG = pageNum;
    }
    
});

geocamShare.core.Gallery.factory = function (domId) {
    return new geocamShare.core.Gallery(domId);
}
