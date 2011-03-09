// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

var geocamTrack = {
    markersById: {},
    markerCount: 0,

    handleResourcePositionsResponse: function (response) {
        if (response.result != null) {
            $.each(response.result.features,
                   function (i, feature) {
                       var pos = new google.maps.LatLng(feature.geometry.coordinates[1],
                                                        feature.geometry.coordinates[0]);
                       var marker = geocamTrack.markersById[feature.id];
                       if (marker == null) {
                           if (geocamTrack.markerCount < 26) {
                               var letter = String.fromCharCode(65 + geocamTrack.markerCount);
                               var icon = 'http://maps.google.com/mapfiles/marker' + letter + '.png';
                           } else {
                               var icon = 'http://maps.google.com/mapfiles/marker.png';
                           }
                           if (feature.properties.displayName != null) {
                               var title = feature.properties.displayName;
                           } else {
                               var title = feature.properties.userName;
                           }
                           
                           marker = new google.maps.Marker({
                                   position: pos,
                                   title: title,
                                   icon: icon
                               });
                           marker.setMap(geocamCore.mapG.gmap);
                           geocamTrack.markersById[feature.id] = marker;
                           geocamTrack.markerCount++;
                       }
                       if (!pos.equals(marker.position)) {
                           marker.setPosition(pos);
                       }
                   });
        }
    },

    updateResourcePositions: function () {
        $.getJSON(geocamCore.settings.SCRIPT_NAME + "tracking/resources.json",
                  geocamTrack.handleResourcePositionsResponse);
    },

    updateResourcePositionsLoop: function () {
        geocamTrack.updateResourcePositions();
        setTimeout(geocamTrack.updateResourcePositionsLoop, 5000);
    },

    startTracking: function () {
        geocamTrack.updateResourcePositionsLoop();
    }
};
