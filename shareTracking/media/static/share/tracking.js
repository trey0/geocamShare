
geocamShare.tracking = {
    markersById: {},
    markerCount: 0,

    handleResourcePositionsResponse: function (response) {
        if (response.result != null) {
            $.each(response.result.features,
                   function (i, feature) {
                       var pos = new google.maps.LatLng(feature.geometry.coordinates[1],
                                                        feature.geometry.coordinates[0]);
                       var marker = geocamShare.tracking.markersById[feature.id];
                       if (marker == null) {
                           if (geocamShare.tracking.markerCount < 26) {
                               var letter = String.fromCharCode(65 + geocamShare.tracking.markerCount);
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
                           marker.setMap(geocamShare.core.mapG.gmap);
                           geocamShare.tracking.markersById[feature.id] = marker;
                           geocamShare.tracking.markerCount++;
                       }
                       if (!pos.equals(marker.position)) {
                           marker.setPosition(pos);
                       }
                   });
        }
    },

    updateResourcePositions: function () {
        $.getJSON(geocamShare.core.settings.SCRIPT_NAME + "tracking/resources.json",
                  geocamShare.tracking.handleResourcePositionsResponse);
    },

    updateResourcePositionsLoop: function () {
        geocamShare.tracking.updateResourcePositions();
        setTimeout(geocamShare.tracking.updateResourcePositionsLoop, 5000);
    },

    startTracking: function () {
        geocamShare.tracking.updateResourcePositionsLoop();
    }
};
