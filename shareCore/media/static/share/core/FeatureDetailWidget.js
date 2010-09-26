// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.FeatureDetailWidget = new Class(
{
    Extends: geocamShare.core.Widget,

    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.feature = geocamShare.core.featuresByUuidG[uuid];

        var pagerHtml = geocamShare.core.getPagerHtml(geocamShare.core.visibleFeaturesG.length,
                                                      this.feature.visibleIndex + 1,
                                                      function (pageNum) {
                                                          var featureIndex = pageNum-1;
                                                          var uuid = geocamShare.core.visibleFeaturesG[featureIndex].uuid;
                                                          return 'javascript:geocamShare.core.setSelectedFeature(\''+uuid+'\')';
                                                      });
        var content =
            '<div style="margin-bottom: 5px;">\n' +
            '<span>' +  pagerHtml + '</span>\n' +
            '<span style="float: right;">\n' +
            '  <a href="javascript:geocamShare.core.clearSelectedFeature()">view all</a>\n' +
            '</span>\n' +
            '</div>\n';
        content += geocamShare.core.getFeatureBalloonHtml(this.feature);
        $('#'+this.domId).html(content);

        // set ajax handler for edit link, replaces default behavior of opening a new web page
        $('#featureEditLink').click(function () {
            geocamShare.core.switcherG.setToFeatureEdit();
            return false;
        });
    }
});

geocamShare.core.FeatureDetailWidget.factory = function (domId, uuid) {
    return new geocamShare.core.FeatureDetailWidget(domId, uuid);
}
