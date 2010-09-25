// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.GalleryWidget = new Class(
{
    Extends: geocamShare.core.Widget,

    page: null,

    initialize: function (domId) {
        this.domId = domId;
        geocamShare.core.galleryG = this;

        $("#" + this.domId).html
          ('<div id="geocamShare_core_gallery"></div>\n' +
           '<div id="geocamShare_core_galleryCaption"></div>\n');

        if (geocamShare.core.visibleFeaturesG != null) {
            this.notifyFeaturesInMapViewport(geocamShare.core.visibleFeaturesG);
        } else {
            $("#geocamShare_core_gallery").html(geocamShare.core.getPendingStatusHtml('Loading...'));
        }

        $(geocamShare.core).bind("error", function (object, shortMessage, longMessage) {
            $("#geocamShare_core_gallery").html(longMessage);
        });
    },

    updateFeatures: function (newFeatures, diff) {
        // wait for notifyFeaturesInMapViewport()
    },

    notifyLoading: function () {
        $("#geocamShare_core_gallery").html(geocamShare.core.getPendingStatusHtml('Searching...'));
    },

    notifyFeaturesInMapViewport: function (visibleFeatures) {
        var pageNum;
        var viewIndexFeature = geocamShare.core.featuresByUuidG[geocamShare.core.viewIndexUuidG];
        if (viewIndexFeature == undefined) {
            pageNum = 1;
        } else {
            pageNum = this.getFeaturePage(viewIndexFeature, visibleFeatures);
        }
        this.renderPage(visibleFeatures, pageNum);
    },

    highlightFeature: function (feature) {
        this.renderPage(geocamShare.core.visibleFeaturesG, this.getFeaturePage(feature, geocamShare.core.visibleFeaturesG));
        $("td#" + feature.uuid + " div").css({backgroundColor: 'red'});
	
        // add the rest of the preview data
        $("#geocamShare_core_galleryCaption").html(geocamShare.core.getCaptionHtml(feature));
    },
    
    unhighlightFeature: function (feature) {
        $("td#" + feature.uuid + " div").css({backgroundColor: ''});
	
        $("#geocamShare_core_galleryCaption").html('');
    },
    
    selectFeature: function (feature) {
        // currently a no-op
    },
    
    unselectFeature: function (feature) {
        // currently a no-op
    },
    
    getNumPages: function (numFeatures) {
        const pageSize = geocamShare.core.GALLERY_PAGE_ROWS*geocamShare.core.GALLERY_PAGE_COLS;
        return Math.ceil(numFeatures / pageSize);
    },

    getIndex: function (page, row, col) {
        return ((page-1)*geocamShare.core.GALLERY_PAGE_ROWS + row)*geocamShare.core.GALLERY_PAGE_COLS + col;
    },

    getGalleryHtml: function (features, pageNum) {
        html = "<table style=\"margin: 0px 0px 0px 0px; padding: 0px 0px 0px 0px; background-color: #ddd;\">";
        html += '<tr><td colspan="3">';
        html += geocamShare.core.getPagerHtml
          (this.getNumPages(features.length),
           pageNum,
           function (pageNum) {
               return 'javascript:geocamShare.core.galleryG.setPage(' + pageNum + ')';
           });
        //html += '<div style="float: right;">Hide</div>';
        html += '</td></tr>';
        for (var r=0; r < geocamShare.core.GALLERY_PAGE_ROWS; r++) {
	    html += "<tr>";
	    for (var c=0; c < geocamShare.core.GALLERY_PAGE_COLS; c++) {
	        var i = this.getIndex(pageNum, r, c);
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
        const pageSize = geocamShare.core.GALLERY_PAGE_ROWS*geocamShare.core.GALLERY_PAGE_COLS;
        return Math.floor(feature.visibleIndex / pageSize) + 1;
    },

    setPage: function (pageNum) {
        if (this.page != pageNum) {
            this.renderPage(geocamShare.core.visibleFeaturesG, pageNum);

            // record a uuid to help us return later to this page
            var firstFeatureIndex = this.getIndex(pageNum, 0, 0);
            geocamShare.core.viewIndexUuidG = geocamShare.core.visibleFeaturesG[firstFeatureIndex].uuid;
        }
    },

    renderPage: function (visibleFeatures, pageNum) {
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
                                geocamShare.core.widgetManagerG.setHighlightedFeature(uuid);
                            }
                        }(feature.uuid),
                        function(uuid) {
                            return function() {
                                geocamShare.core.widgetManagerG.clearHighlightedFeature();
                            }
                        }(feature.uuid)
                    );
                    $("td#" + feature.uuid).click(
                        function(uuid) {
                            return function() {
                                geocamShare.core.widgetManagerG.setSelectedFeature(uuid);
                            }
                        }(feature.uuid)
                    );
                }
            }
        }
        
        this.page = pageNum;
    }
    
});

geocamShare.core.GalleryWidget.factory = function (domId) {
    return new geocamShare.core.GalleryWidget(domId);
}
