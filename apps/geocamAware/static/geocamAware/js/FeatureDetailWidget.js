// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.FeatureDetailWidget = new Class(
{
    Extends: geocamAware.Widget,

    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.feature = geocamAware.featuresByUuidG[uuid];

        var pagerHtml = geocamAware.getPagerHtml(geocamAware.visibleFeaturesG.length,
                                                      this.feature.visibleIndex + 1,
                                                      function (pageNum) {
                                                          var featureIndex = pageNum-1;
                                                          var uuid = geocamAware.visibleFeaturesG[featureIndex].uuid;
                                                          return 'javascript:geocamAware.setSelectedFeature(\''+uuid+'\')';
                                                      });
        var content =
            '<div style="margin-bottom: 5px;">\n' +
            '<span>' +  pagerHtml + '</span>\n' +
            '<span style="float: right;">\n' +
            '  <a href="javascript:geocamAware.clearSelectedFeature()">view all</a>\n' +
            '</span>\n' +
            '</div>\n';
        content += this.feature.getBalloonHtml();
        $('#'+this.domId).html(content);

        // set ajax handler for edit link, replaces default behavior of opening a new web page
        $('#featureEditLink').click(function () {
            geocamAware.setToFeatureEdit();
            return false;
        });
    }
});

geocamAware.FeatureDetailWidget.factory = function (domId, uuid) {
    return new geocamAware.FeatureDetailWidget(domId, uuid);
}
