// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.FeatureDetailWidget = new Class(
{
    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.feature = geocamShare.core.featuresByUuidG[uuid];

        var content = '<div style="float: right;"><a href="javascript:geocamShare.core.widgetManagerG.setFeatureSelected(\''+this.feature.uuid+'\', false);">View all</a></div><br/>\n'
        content += geocamShare.core.getFeatureBalloonHtml(this.feature);
        $('#'+this.domId).html(content);
    },
    
    highlightFeature: function (feature) {
        // todo: may want to show highlighting if uuid matches
    },
    
    unhighlightFeature: function (feature) {
        // todo: may want to remove highlighting
    }
    
});

geocamShare.core.FeatureDetailWidget.factory = function (domId, uuid) {
    return new geocamShare.core.FeatureDetailWidget(domId, uuid);
}
