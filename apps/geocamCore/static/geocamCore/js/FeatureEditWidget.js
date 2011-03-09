// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamCore.FeatureEditWidget = new Class(
{
    Extends: geocamCore.Widget,

    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.uuid = uuid;
        this.feature = geocamCore.featuresByUuidG[uuid];

        var self = this;
        $.get(this.feature.getEditUrl(true),
              function (data) { self.formLoadedHandler(data) });

        var content = '<div style="margin: 10px;">'
            + geocamCore.getLoadingIcon()
            + '<span style="vertical-align: middle;">Loading edit form</span>'
            + '</div>';
        $('#' + this.domId).html(content);
    },
    
    formLoadedHandler: function (formHtml) {
        geocamCore.debugObjectG = formHtml;

        var content = ''
            + '<div>\n'
            + '  <div style="margin-bottom: 10px;">\n'
            + '    ' + this.feature.getDetailImageHtml()
            + '  </div>\n'
            + '  ' + formHtml
            + '</div>\n'

        $('#' + this.domId).html(content);

        // connect formHtml elements to handlers
        $('#editImage').attr('action',
                             this.feature.getEditUrl(true));

        $('#editImageCancel').click(function () {
            geocamCore.setToFeatureDetail();
            return false;
        });

        geocamCore.ajaxFormInit('editImage',
                                      function (updatedFeature) {
                                          geocamCore.updateFeature(updatedFeature);
                                          geocamCore.setToFeatureDetail();
                                      });
    }

});

geocamCore.FeatureEditWidget.factory = function (domId, uuid) {
    return new geocamCore.FeatureEditWidget(domId, uuid);
}
