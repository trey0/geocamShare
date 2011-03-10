// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.GalleryWidget = new Class(
{
    Extends: geocamAware.Widget,

    page: null,

    initialize: function (domId) {
        this.domId = domId;
        geocamAware.galleryG = this;

        $("#" + this.domId).html
          ('<div id="geocamAware_gallery"></div>\n' +
           '<div id="geocamAware_galleryCaption"></div>\n');

        if (geocamAware.visibleFeaturesG != null) {
            this.notifyFeaturesInMapViewport(geocamAware.visibleFeaturesG);
        } else {
            $("#geocamAware_gallery").html(geocamAware.getPendingStatusHtml('Loading...'));
        }

        $(geocamAware).bind("error", function (object, shortMessage, longMessage) {
            $("#geocamAware_gallery").html(longMessage);
        });

        geocamAware.bindEvent(geocamAware, this, "highlightFeature");
        geocamAware.bindEvent(geocamAware, this, "unhighlightFeature");
        geocamAware.bindEvent(geocamAware, this, "notifyLoading");
        geocamAware.bindEvent(geocamAware, this, "notifyFeaturesInMapViewport");
    },

    notifyLoading: function () {
        $("#geocamAware_gallery").html(geocamAware.getPendingStatusHtml('Searching...'));
    },

    notifyFeaturesInMapViewport: function (visibleFeatures) {
        var pageNum;
        var viewIndexFeature = geocamAware.featuresByUuidG[geocamAware.viewIndexUuidG];
        if (viewIndexFeature == undefined) {
            pageNum = 1;
        } else {
            pageNum = this.getFeaturePage(viewIndexFeature, visibleFeatures);
        }
        this.renderPage(visibleFeatures, pageNum);
    },

    highlightFeature: function (feature) {
        this.renderPage(geocamAware.visibleFeaturesG, this.getFeaturePage(feature, geocamAware.visibleFeaturesG));
        $("td#" + feature.uuid + " div").css({backgroundColor: 'red'});
	
        // add the rest of the preview data
        $("#geocamAware_galleryCaption").html(feature.getCaptionHtml());
    },
    
    unhighlightFeature: function (feature) {
        $("td#" + feature.uuid + " div").css({backgroundColor: ''});
	
        $("#geocamAware_galleryCaption").html('');
    },
    
    getNumPages: function (numFeatures) {
        const pageSize = geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_ROWS*geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_COLS;
        return Math.ceil(numFeatures / pageSize);
    },

    getIndex: function (page, row, col) {
        return ((page-1)*geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_ROWS + row)*geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_COLS + col;
    },

    getGalleryHtml: function (features, pageNum) {
        html = "<table style=\"margin: 0px 0px 0px 0px; padding: 0px 0px 0px 0px; background-color: #ddd;\">";
        html += '<tr><td colspan="3">';
        html += geocamAware.getPagerHtml
          (this.getNumPages(features.length),
           pageNum,
           function (pageNum) {
               return 'javascript:geocamAware.galleryG.setPage(' + pageNum + ')';
           });
        //html += '<div style="float: right;">Hide</div>';
        html += '</td></tr>';
        for (var r=0; r < geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_ROWS; r++) {
	    html += "<tr>";
	    for (var c=0; c < geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_COLS; c++) {
	        var i = this.getIndex(pageNum, r, c);
	        if (i < features.length) {
		    var feature = features[i];
		    html += feature.getGalleryThumbHtml();
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
        const pageSize = geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_ROWS*geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_COLS;
        return Math.floor(feature.visibleIndex / pageSize) + 1;
    },

    setPage: function (pageNum) {
        if (this.page != pageNum) {
            this.renderPage(geocamAware.visibleFeaturesG, pageNum);

            // record a uuid to help us return later to this page
            var firstFeatureIndex = this.getIndex(pageNum, 0, 0);
            geocamAware.viewIndexUuidG = geocamAware.visibleFeaturesG[firstFeatureIndex].uuid;
        }
    },

    renderPage: function (visibleFeatures, pageNum) {
        if (visibleFeatures.length == 0) {
            if (geocamAware.featuresG.length == 0) {
                if (geocamAware.queryG == "") {
                    $("#geocamAware_gallery").html("No features in DB yet.");
                } else {
                    $("#geocamAware_gallery").html("No matches found.");
                }
            } else {
                $("#geocamAware_gallery").html("No matching features within map viewport.  Try zoom to fit.");
            }
        } else {
            // set gallery html
            $("#geocamAware_gallery").html(this.getGalleryHtml(visibleFeatures, pageNum));
            
            // set gallery listeners
            const pageSize = geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_ROWS*geocamAware.settings.GEOCAM_AWARE_GALLERY_PAGE_COLS;
            for (var j=0; j < pageSize; j++) {
                var i = (pageNum-1)*pageSize + j;
                if (i < visibleFeatures.length) {
                    var feature = visibleFeatures[i];
                    $("td#" + feature.uuid).hover(
                        function(uuid) {
                            return function() {
                                geocamAware.setHighlightedFeature(uuid);
                            }
                        }(feature.uuid),
                        function(uuid) {
                            return function() {
                                geocamAware.clearHighlightedFeature();
                            }
                        }(feature.uuid)
                    );
                    $("td#" + feature.uuid).click(
                        function(uuid) {
                            return function() {
                                geocamAware.setSelectedFeature(uuid);
                            }
                        }(feature.uuid)
                    );
                }
            }
        }
        
        this.page = pageNum;
    }
    
});

geocamAware.GalleryWidget.factory = function (domId) {
    return new geocamAware.GalleryWidget(domId);
}
