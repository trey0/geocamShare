// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamCore.FeatureDetailWidget = new Class(
{
    Extends: geocamCore.Widget,

    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.feature = geocamCore.featuresByUuidG[uuid];

        var pagerHtml = geocamCore.getPagerHtml(geocamCore.visibleFeaturesG.length,
                                                      this.feature.visibleIndex + 1,
                                                      function (pageNum) {
                                                          var featureIndex = pageNum-1;
                                                          var uuid = geocamCore.visibleFeaturesG[featureIndex].uuid;
                                                          return 'javascript:geocamCore.setSelectedFeature(\''+uuid+'\')';
                                                      });
        var content =
            '<div style="margin-bottom: 5px;">\n' +
            '<span>' +  pagerHtml + '</span>\n' +
            '<span style="float: right;">\n' +
            '  <a href="javascript:geocamCore.clearSelectedFeature()">view all</a>\n' +
            '</span>\n' +
            '</div>\n';
        content += this.feature.getBalloonHtml();
        $('#'+this.domId).html(content);

        // set ajax handler for edit link, replaces default behavior of opening a new web page
        $('#featureEditLink').click(function () {
            geocamCore.setToFeatureEdit();
            return false;
        });
    }
});

geocamCore.FeatureDetailWidget.factory = function (domId, uuid) {
    return new geocamCore.FeatureDetailWidget(domId, uuid);
}
