// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.geocam.Photo = new Class(
{
    Extends: geocamShare.core.Image,

    getThumbnailUrl: function (width) {
        return geocamShare.core.getDirUrl(this) + "th" + width + ".jpg";
    }

});

