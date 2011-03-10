// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamAware.WidgetManager = new Class(
{
    activeWidgets: {},
    
    setWidgetForDomId: function (domId, widgetFactory, widgetFactoryArgs) {
        if (widgetFactoryArgs == undefined) {
            widgetFactoryArgs = [];
        }
        this.activeWidgets[domId] = widgetFactory.apply(null, [domId].concat(widgetFactoryArgs));
    }
    
});

