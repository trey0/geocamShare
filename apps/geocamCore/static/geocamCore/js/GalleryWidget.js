// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamCore.GalleryWidget = new Class(
{
    Extends: geocamCore.Widget,

    page: null,

    initialize: function (domId) {
        this.domId = domId;
        geocamCore.galleryG = this;

        $("#" + this.domId).html
          ('<div id="geocamCore_gallery"></div>\n' +
           '<div id="geocamCore_galleryCaption"></div>\n');

        if (geocamCore.visibleFeaturesG != null) {
            this.notifyFeaturesInMapViewport(geocamCore.visibleFeaturesG);
        } else {
            $("#geocamCore_gallery").html(geocamCore.getPendingStatusHtml('Loading...'));
        }

        $(geocamCore).bind("error", function (object, shortMessage, longMessage) {
            $("#geocamCore_gallery").html(longMessage);
        });

        geocamCore.bindEvent(geocamCore, this, "highlightFeature");
        geocamCore.bindEvent(geocamCore, this, "unhighlightFeature");
        geocamCore.bindEvent(geocamCore, this, "notifyLoading");
        geocamCore.bindEvent(geocamCore, this, "notifyFeaturesInMapViewport");
    },

    notifyLoading: function () {
        $("#geocamCore_gallery").html(geocamCore.getPendingStatusHtml('Searching...'));
    },

    notifyFeaturesInMapViewport: function (visibleFeatures) {
        var pageNum;
        var viewIndexFeature = geocamCore.featuresByUuidG[geocamCore.viewIndexUuidG];
        if (viewIndexFeature == undefined) {
            pageNum = 1;
        } else {
            pageNum = this.getFeaturePage(viewIndexFeature, visibleFeatures);
        }
        this.renderPage(visibleFeatures, pageNum);
    },

    highlightFeature: function (feature) {
        this.renderPage(geocamCore.visibleFeaturesG, this.getFeaturePage(feature, geocamCore.visibleFeaturesG));
        $("td#" + feature.uuid + " div").css({backgroundColor: 'red'});
	
        // add the rest of the preview data
        $("#geocamCore_galleryCaption").html(feature.getCaptionHtml());
    },
    
    unhighlightFeature: function (feature) {
        $("td#" + feature.uuid + " div").css({backgroundColor: ''});
	
        $("#geocamCore_galleryCaption").html('');
    },
    
    getNumPages: function (numFeatures) {
        const pageSize = geocamCore.settings.GALLERY_PAGE_ROWS*geocamCore.settings.GALLERY_PAGE_COLS;
        return Math.ceil(numFeatures / pageSize);
    },

    getIndex: function (page, row, col) {
        return ((page-1)*geocamCore.settings.GALLERY_PAGE_ROWS + row)*geocamCore.settings.GALLERY_PAGE_COLS + col;
    },

    getGalleryHtml: function (features, pageNum) {
        html = "<table style=\"margin: 0px 0px 0px 0px; padding: 0px 0px 0px 0px; background-color: #ddd;\">";
        html += '<tr><td colspan="3">';
        html += geocamCore.getPagerHtml
          (this.getNumPages(features.length),
           pageNum,
           function (pageNum) {
               return 'javascript:geocamCore.galleryG.setPage(' + pageNum + ')';
           });
        //html += '<div style="float: right;">Hide</div>';
        html += '</td></tr>';
        for (var r=0; r < geocamCore.settings.GALLERY_PAGE_ROWS; r++) {
	    html += "<tr>";
	    for (var c=0; c < geocamCore.settings.GALLERY_PAGE_COLS; c++) {
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
        const pageSize = geocamCore.settings.GALLERY_PAGE_ROWS*geocamCore.settings.GALLERY_PAGE_COLS;
        return Math.floor(feature.visibleIndex / pageSize) + 1;
    },

    setPage: function (pageNum) {
        if (this.page != pageNum) {
            this.renderPage(geocamCore.visibleFeaturesG, pageNum);

            // record a uuid to help us return later to this page
            var firstFeatureIndex = this.getIndex(pageNum, 0, 0);
            geocamCore.viewIndexUuidG = geocamCore.visibleFeaturesG[firstFeatureIndex].uuid;
        }
    },

    renderPage: function (visibleFeatures, pageNum) {
        if (visibleFeatures.length == 0) {
            if (geocamCore.featuresG.length == 0) {
                if (geocamCore.queryG == "") {
                    $("#geocamCore_gallery").html("No features in DB yet.");
                } else {
                    $("#geocamCore_gallery").html("No matches found.");
                }
            } else {
                $("#geocamCore_gallery").html("No matching features within map viewport.  Try zoom to fit.");
            }
        } else {
            // set gallery html
            $("#geocamCore_gallery").html(this.getGalleryHtml(visibleFeatures, pageNum));
            
            // set gallery listeners
            const pageSize = geocamCore.settings.GALLERY_PAGE_ROWS*geocamCore.settings.GALLERY_PAGE_COLS;
            for (var j=0; j < pageSize; j++) {
                var i = (pageNum-1)*pageSize + j;
                if (i < visibleFeatures.length) {
                    var feature = visibleFeatures[i];
                    $("td#" + feature.uuid).hover(
                        function(uuid) {
                            return function() {
                                geocamCore.setHighlightedFeature(uuid);
                            }
                        }(feature.uuid),
                        function(uuid) {
                            return function() {
                                geocamCore.clearHighlightedFeature();
                            }
                        }(feature.uuid)
                    );
                    $("td#" + feature.uuid).click(
                        function(uuid) {
                            return function() {
                                geocamCore.setSelectedFeature(uuid);
                            }
                        }(feature.uuid)
                    );
                }
            }
        }
        
        this.page = pageNum;
    }
    
});

geocamCore.GalleryWidget.factory = function (domId) {
    return new geocamCore.GalleryWidget(domId);
}
