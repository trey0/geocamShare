// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.FeatureEditWidget = new Class(
{
    Extends: geocamAware.Widget,

    domId: null,
    feature: null,

    initialize: function (domId, uuid) {
        this.domId = domId;
        this.uuid = uuid;
        this.feature = geocamAware.featuresByUuidG[uuid];

        var self = this;
        $.get(this.feature.getEditUrl(true),
              function (data) { self.formLoadedHandler(data) });

        var content = '<div style="margin: 10px;">'
            + geocamAware.getLoadingIcon()
            + '<span style="vertical-align: middle;">Loading edit form</span>'
            + '</div>';
        $('#' + this.domId).html(content);
    },
    
    formLoadedHandler: function (formHtml) {
        geocamAware.debugObjectG = formHtml;

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
            geocamAware.setToFeatureDetail();
            return false;
        });

        geocamAware.ajaxFormInit('editImage',
                                      function (updatedFeature) {
                                          geocamAware.updateFeature(updatedFeature);
                                          geocamAware.setToFeatureDetail();
                                      });
    }

});

geocamAware.FeatureEditWidget.factory = function (domId, uuid) {
    return new geocamAware.FeatureEditWidget(domId, uuid);
}
