$(document).ready(function(){

  // //builds the map
  // var map = buildMap([-90,-360],[90,360],false)

  function refreshMap(data) {

    if (clusters) {clusters.clearLayers()} 
  
    newMarkers = L.geoJSON(data,{onEachFeature: onEachFeature});
    clusters.addLayer(newMarkers)
    
    map.flyToBounds(newMarkers.getBounds());
    map.addLayer(clusters)   

  };  
  

  $("#submit-button").click(function (e) {
    e.preventDefault();

    var formData = $("#myform").serialize();

    $.ajax({
      url: callbackURL,
      data: {
        'myform': formData,
      },
      dataType: 'json',
      success: function (data) {
        refreshMap(data)
      }
    })
  });
});

function buildMap(lat,lon, cluster)  {
  
  // var token = "pk.eyJ1Ijoic3NqZW5ueTkwIiwiYSI6ImNqd2J2d2poeDAzOGk0OXBsZnl6M3hqem0ifQ.f5KsfLty3lJDlZbHf0OeIA"

  // satelliteLayer = new L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  //   attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  //   id: 'mapbox.satellite',
  //   accessToken: token,
  //   });

  // streetLayer =  new L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  //     attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  //     id: 'mapbox.streets',
  //     accessToken: token,
  //     });

  openMaps = new L.tileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
  });

  var map = L.map('map', {
    layers: [openMaps],
    maxBounds: L.latLngBounds(lat, lon),
    minZoom: 2,
    // maxZoom: 12,
    worldCopyJump: true,
    });

  L.control.scale().addTo(map);


  // var baseLayers = {
  //   "Satellite": satelliteLayer,
  //   "Streets": streetLayer
  // };

  // L.control.layers(baseLayers).addTo(map);
  // map.zoomControl.setPosition('topright');


  if (cluster == true) {

    //defines the clusters variable required for decluttering map
    var clusters = L.markerClusterGroup({
      chunkedLoading:true,
      disableClusteringAtZoom: 13,
      spiderfyOnMaxZoom: false,}
    );

    clusters.addLayer(siteMarkers)
    map.addLayer(clusters)

  } else {

    map.addLayer(siteMarkers)

  }

  map.fitBounds(siteMarkers.getBounds());



  return map;
}

function onEachFeature(feature, layer) {
    if (feature.properties && feature.properties.site_name) {
        
      var fp = feature.properties
      // console.log(fp)
      var propertiesList = [fp.site_name,fp.latitude,fp.longitude,fp.elevation]
      var propertyNames = ['Site name:','Latitude:','Longitude:','Elevation:']
      var tableContent = "<table class='table table-striped'><tbody>"

      for (var p in propertiesList) {

        if (propertiesList[p] == null) {
          var propertyValue = ''
        } else {
          var propertyValue = propertiesList[p]
        }

        tableContent += '<tr><td id=popup-data>' + propertyNames[p] + '</td><td id=popup-data>' + propertyValue + '</td></td>'
      }
      
      tableContent += '</tbody></table>'

      layer.bindPopup(tableContent);
    }
  }

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})


function createClusters () {

    //defines the clusters variable required for decluttering map
    var clusters = L.markerClusterGroup({
      chunkedLoading:true,
      disableClusteringAtZoom: 13,
      spiderfyOnMaxZoom: false,}
    );

    clusters.addLayer(siteMarkers)
    map.addLayer(clusters)

    return clusters



}
