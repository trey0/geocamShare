// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

geocamShare.core.getDirUrl = function (feature) {
    ret = geocamShare.core.settings.DATA_URL + feature.subtype.toLowerCase() + '/';
    var idStr = feature.localId + 'p';
    for (var i = 0; i < idStr.length; i += 2) {
        if (i > 0) {
            ret += '/';
        }
        ret += idStr.substr(i, 2);
    }
    ret += "/" + feature.version + "/";
    return ret;
}

geocamShare.core.Feature.prototype.getViewerUrl = function () {
    var name = this.name;
    if (name == "") {
        if (this.subtype == "Photo") {
            name = "untitled.jpg";
        } else if (this.subtype == "Track") {
            name = "untitled.json";
        } else {
            name = "untitled";
        }
    }
    return geocamShare.core.settings.SCRIPT_NAME + this.subtype.toLowerCase() + "/" + this.localId + "/" + name;
}

geocamShare.core.Feature.prototype.getEditUrl = function (widget) {
    var verb;
    if (widget) {
        verb = 'editWidget';
    } else {
        verb = 'edit'
    }
    return geocamShare.core.settings.SCRIPT_NAME + verb + '/' + this.subtype.toLowerCase() + "/" + this.uuid + "/";
}

geocamShare.core.Photo = geocamShare.geocam.Photo;
