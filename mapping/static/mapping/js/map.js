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

  $("#filter-submit-button").click(function (e) {
    map.spin(true);
    var formData = $("form#filter-form").serializeArray();
    $.ajax({
      url: filterURL,
      data: formData,
      dataType: 'json',
      success: function (data) {
        try {
          refreshMap(data['points']);
          update_info_table(data['info']['count'],'#info-counts-table')
          update_info_table(data['info']['average'],'#info-average-table')
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

  var openMaps = new L.tileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
  });


  var Esri_OceanBasemap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri',
    maxZoom: 13
  });


  var map = L.map('map', {
    layers: [Esri_OceanBasemap],
    maxBounds: L.latLngBounds(lat, lon),
    minZoom: 2,
    // maxZoom: 12,
    worldCopyJump: true,
    });

  L.control.scale().addTo(map);

  return map;
  }

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

function update_info_table(data, table_id) {

  var tableContent = ""

  for (var item in data) {
    tableContent += '<tr><td class="text-left">' + item + '</td><td>' + data[item] + '</td></tr>'
  }

  $(table_id +' tbody').html(tableContent)

}



var mapPanelOpen = false;

$('.close-btn').click(function() {
  mapPanelOpen = false;

  $('.map-panel').css('left', '-400px');
  $('.db-map').css('left', '56px');

});

$('#sideBar a').click(function(event) {

  var parent =  $(this).parent()

  console.log(parent.attr('class'))


  var target = $(this).attr('data-target');

  if (!mapPanelOpen) {
    // open map panel
    $(target).css({ 'left': '56px',});
    $('.db-map').css('left', '456px');

    parent.css('box-shadow', '0 .5rem 1rem rgba(0,0,0,.15) inset')


    mapPanelOpen = target;
  }

  else if (!(mapPanelOpen==target)) {
    // open map panel
    $(mapPanelOpen).css({ 
      'z-index':4,
    });
    
    parent.css('box-shadow', '')

    $(target).css({ 
      'z-index':5,
      'left': '56px',
    });

    $('.db-map').css('left', '456px');

    $(mapPanelOpen).css({ 
      'left':'-400px',
    });

    mapPanelOpen = target;
  }
  else {
    // close map panel 
    mapPanelOpen = false;
    $('.map-panel').css('left','-400px');
    $('.db-map').css('left', '56px');

    parent.css('box-shadow', '')


  }
});



// $('#filter-form').on('keypress', false);