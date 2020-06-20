
var map = createMap([-100,-360],[100,360],true).fitWorld()
map.spin(true);
var data = ''
var markers = L.geoJSON()
var clusters = createClusters(markers)
var marker = L.marker()

$(document).ready(function(){
  retrieveData('')
});

function createMap(lat,lon, cluster)  {

  var openMaps = new L.tileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
  });

  var Esri_OceanBasemap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri',
    maxZoom: 13
  });

  var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

  var map = L.map('map', {
    layers: [Esri_WorldImagery],
    minZoom: 2,
    // maxZoom: 12,
    worldCopyJump: true,
    });

  L.control.scale().addTo(map);

  var baseLayers = {
    "Satellite": Esri_WorldImagery,
    "Ocean Basemap": Esri_OceanBasemap,
    "Street": openMaps,
  };

  L.control.layers(baseLayers).addTo(map);

  return map;
  }

function retrieveData(formdata){
  map.spin(true);

  $.ajax({
    url: data_url,
    dataType: 'json',
    data: formdata,
    success: function (data) {
      try {
        refreshMap(data)
      }
      catch(err) {
        map.spin(false);
      }
      map.spin(false);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      map.spin(false);
    }
  })
  
};

function refreshMap(data) {

  var t = new Date()

  if (data.features.length == 0) {
    // alert('Could not find any data matching the current query!')
    throw 'No data found'
  }

  if ( $.fn.dataTable.isDataTable( '#geoTable' ) ) {
    table = $('#geoTable').DataTable();
    table.destroy();
    $('#geoTable>thead').empty();
    $('#geoTable>tbody').remove();
    table_from_geojson(data)
  }
  else {
    table_from_geojson(data)
  }


  // if ( $.fn.dataTable.isDataTable( '#dataTable' ) ) {
  //   table = $('#dataTable').DataTable();
  //   dataTable = tabulate_geojson(data.features)
  //   table.clear();
  //   table.rows.add(dataTable);
  //   table.draw();
  // }
  // else {
  //   table_from_list(data)
  // }

  console.log(new Date() - t)

  // remove the previous data from the map
  map.removeLayer(markers)
  map.removeLayer(clusters)

  // add new data to the map
  markers = L.geoJSON(data, {
    onEachFeature: onEachFeature,
  })
  clusters = createClusters(markers)
  clusters.addLayer(markers)
  console.log(new Date() - t)

  map.flyToBounds(markers.getBounds());
  map.addLayer(clusters)  
  console.log(new Date() - t)

}; 

$("#filter-submit-button").click(function (e) {
  map.spin(true);
  var formData = $("#filter-form").serializeArray();
  retrieveData(formData);
  });

$("#download-button").click(function (e) {
  var formData = $("#filter-form");
  formData.submit()
  });

function create_multiple_layers(data,map) {
    
  data = Object.entries(data)
  map.spin(true);
  
  for (let index = 0; index < data.length; index++) {
    const element = data[index];  
    layer = createMarkers(element[1])
    map.addLayer(layer)
  }
  
  map.spin(false);

}

function createMarkers (geojsonObject) {
  return L.geoJSON(geojsonObject, {
      onEachFeature: onEachFeature,
    });
}

function onEachFeature(feature, layer) {
  var properties = Object.entries(feature.properties)
  
  var first = properties.shift()

  var tableContent = "<div class='h5'>" + first[1] + "</div>"
  tableContent += "<table class='table table-striped'><tbody>"

  properties.forEach(el=> {
    if (el[1] && el[0] != 'slug') {
      tableContent += '<tr><td >' + titleize(el[0]) + ':  </td><td>' + el[1] + '</td></td>'
    }
  })

  tableContent += '</tbody></table>'
  layer.bindPopup(tableContent);
    
  };

function createClusters(markers) {
  //defines the clusters variable required for decluttering map
  var clusters = L.markerClusterGroup({
    chunkedLoading: true,
    chunkInterval:100,
    disableClusteringAtZoom: 8,
    spiderfyOnMaxZoom: false,
  });
  clusters.addLayer(markers);
  map.spin(false);
  return clusters;
};





