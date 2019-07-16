
//builds the map
var map = initMap([-100,-360],[100,360],true).fitWorld()


// $(document).ready(function(){

// })



$(document).ready(function(){
   
  //build the marker clusters
  var clusters = createClusters(siteMarkers);
  map.addLayer(clusters);


  function refreshMap(data) {


    // console.log(clusters)
    clusters.clearLayers()
    newMarkers = L.geoJSON(data,{onEachFeature: onEachFeature});
    clusters.addLayer(newMarkers)
    
    map.flyToBounds(newMarkers.getBounds());
    map.addLayer(clusters)   
  
  }; 


  $("#submit-button").click(function (e) {
    e.preventDefault();
    map.spin(true);
  
    var formData = $("#myform").serializeArray();

    var filtered = formData.filter(function (el) {
        return el.value !== "";
    });

    var queryString = $.param(filtered);

    $.ajax({
      url: callbackURL,
      data: {
        'myform': queryString,
      },
      dataType: 'json',
      success: function (data) {
        try {
          refreshMap(data);
        }
        catch(err) {
          console.log(err)
          map.spin(false);
        }
        map.spin(false);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        map.spin(false);
        console.log(textStatus, errorThrown)
      }
    })
  });





  });

function initMap(lat,lon, cluster)  {

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

  return map;}

function onEachFeature(feature, layer) {
    // console.log(feature.properties)

    if (feature.properties && feature.properties.site_name) {
        
      var fp = feature.properties
      var propertiesList = [fp.site_name,fp.year]
      var propertyNames = ['Site name:','Year:']
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


function createMarkers (geojsonObject) {
  map.spin(true);

  return L.geoJSON(geojsonObject, {
      onEachFeature: onEachFeature
    });
}


function createClusters (markers) {

    //defines the clusters variable required for decluttering map
    var clusters = L.markerClusterGroup({
      chunkedLoading:true,
      disableClusteringAtZoom: 13,
      spiderfyOnMaxZoom: false,}
    );

    clusters.addLayer(markers)
    map.spin(false);


    return clusters

  }
