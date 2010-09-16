// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

share.core.WidgetManager = new Class({
        activeWidgets: {},

        setWidgetForDomId: function (domId, widgetFactory) {
            this.activeWidgets[domId] = widgetFactory(domId);
        },

        setFeatureSelected: function (uuid, isSelected) {
            $.each(this.activeWidgets,
                   function (domId, widget) {
                       widget.setFeatureSelected(uuid, isSelected);
                   });
        },

        setFeatureHighlighted: function (uuid, isHighlighted) {
            $.each(this.activeWidgets,
                   function (domId, widget) {
                       widget.setFeatureHighlighted(uuid, isHighlighted);
                   });
        }
    });

