// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.FeatureEditWidget = new Class(
{
    Extends: geocamShare.core.Widget,

    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.uuid = uuid;
        this.feature = geocamShare.core.featuresByUuidG[uuid];

        var self = this;
        $.get(geocamShare.core.getFeatureEditUrl(this.feature, true),
              function (data) { self.formLoadedHandler(data) });

        var content = '<div style="margin: 10px;">'
            + geocamShare.core.ajaxFormGetLoadingIcon()
            + '<span style="vertical-align: middle;">Loading edit form</span>'
            + '</div>';
        $('#' + this.domId).html(content);
    },
    
    formLoadedHandler: function (formHtml) {
        geocamShare.core.debugObjectG = formHtml;

        var content = ''
            + '<div>\n'
            + '  <div style="margin-bottom: 10px;">\n'
            + '    ' + geocamShare.core.getFeatureDetailImageHtml(this.feature)
            + '  </div>\n'
            + '  ' + formHtml
            + '</div>\n'

        $('#' + this.domId).html(content);

        // fix default form post url since we are using ajax
        $('#editImage').attr('action',
                             geocamShare.core.getFeatureEditUrl(this.feature, true));

        geocamShare.core.ajaxFormInit('editImage',
                                      function () { geocamShare.core.switcherG.setToFeatureDetail(); });
    }

});

geocamShare.core.FeatureEditWidget.factory = function (domId, uuid) {
    return new geocamShare.core.FeatureEditWidget(domId, uuid);
}
