// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.Image = new Class(
{
    Extends: geocamShare.core.PointFeature,

    getThumbSize: function () {
        return [this.w, this.h];
    }

});

