
// var map = createMap().fitWorld();
// var clusters = createClusters()
// var tmpMarker = L.marker()
// map.addLayer(clusters)
var baseLayers = {
  "Dark Gray": L.esri.basemapLayer('DarkGray',{detectRetina: true}),
  "Imagery": L.esri.basemapLayer('Imagery',{detectRetina: true}),
  "Oceans": L.esri.basemapLayer('Oceans',{detectRetina: true}),
  "Topographic": L.esri.basemapLayer('Topographic',{detectRetina: true}),
  "Nat Geo": L.esri.basemapLayer('NationalGeographic',{detectRetina: true}),
};

function createMap()  {

  var baseLayers = {
    "Dark Gray": L.esri.basemapLayer('DarkGray',{detectRetina: true}),
    "Imagery": L.esri.basemapLayer('Imagery',{detectRetina: true}),
    "Oceans": L.esri.basemapLayer('Oceans',{detectRetina: true}),
    "Topographic": L.esri.basemapLayer('Topographic',{detectRetina: true}),
    "Nat Geo": L.esri.basemapLayer('NationalGeographic',{detectRetina: true}),
  };

  var map = L.map('map', {
    layers: [baseLayers['Imagery']],
    minZoom: 2,
    worldCopyJump: true,
    fullscreenControl: true,
     });

  L.control.scale().addTo(map);
  L.control.layers(baseLayers).addTo(map);
  return map;
};

function get_color() {
  return '#' + Math.floor(Math.random()*16777215).toString(16);
}

function add_to_map(geojson) {

  let color = get_color();
  var geoJsonLayer  = L.geoJson(geojson,{
    onEachFeature: onEachFeature
    });

  if (geojson.features.length > 250 ) {
    var clusters = L.markerClusterGroup({
      disableClusteringAtZoom: 8,
      spiderfyOnMaxZoom: false,
    });
    clusters.addLayer(geoJsonLayer)
    clusters.addTo(map)
  } else {
    geoJsonLayer.addTo(map)
  }
  map.flyToBounds(geoJsonLayer.getBounds(),{maxZoom: 8})

  return geoJsonLayer 
}

function add_and_zoom(geojson) {
    layer = add_to_map(geojson)
    map.flyToBounds(layer.getBounds(),{maxZoom: 8})
}

function add_shape(geojson) {
  layer = L.geoJson(geojson).addTo(map)
}

function createMarkers(data,type) {

  var lat = data.columns.indexOf('Latitude')
  var lon = data.columns.indexOf('Longitude')
  var val = data.columns.indexOf(type)

  var new_data = [];
  data.data.forEach(el => {
  var m = L.circleMarker([el[lat], el[lon]], {
          radius: 3, 
          fill:true,
          fillOpacity:0.75,
          fillColor: 'rgb(255,0,0,1)',
          stroke:false
      });
    m.value = el[val];
    new_data.push(m);
  });

  return L.featureGroup(new_data)
};

function createClusters() {
  //defines the clusters variable required for decluttering map
  var clusters = L.markerClusterGroup({
    chunkedLoading: true,
    // chunkInterval:100,
    disableClusteringAtZoom: 8,
    spiderfyOnMaxZoom: false,
    // iconCreateFunction: customClusterIcon,
  });
  return clusters;
};

function updateData(){
  map.spin(true);
  $.post({
    url:  $(location).attr('href'),
    data: $("#filter-form").serializeArray(),
    success: updatePage,
    complete: stop_spin,
    error: stop_spin,
  })
};

async function updatePage(data) {
  await new updateTable(data);
  await new updateMap(data);
};
    
function stop_spin() {
  map.spin(false)
}

function updateMap(data) {
  data.columns.push(data.type)

  clusters.clearLayers()
  markers = createMarkers(data, data.type);
  clusters.addLayers(markers, {
      chunkedLoading: true,
  })

  if (data.data.length > 0) {
    map.flyToBounds(markers.getBounds())
  } else {
    map.fitWorld()
  }
}; 

function updateTable(data) {

  var col_headers = {
    heat_flow: 'Heat Flow',
    temperature: 'Temp. Count',
    conductivity: 'Cond. Count',
    gradient: 'Gradient',
    heat_generation: 'Heat Gen. Count',
  }
  var ind = data.columns.indexOf(data.type);

  data.id='#dataTable';
  if ( $.fn.dataTable.isDataTable(data.id) ) {
    table = $(data.id).DataTable();
    table.clear();
  } else {
    table = table_from_values(data) 
  }

  table.rows.add(data.data)
  $(table.column(ind).header()).html(col_headers[data.type])
  table.draw()
}

function customClusterIcon(cluster) {

  var childCount = cluster.getChildCount();
  var markers = cluster.getAllChildMarkers()

  var value_sum = 0;

  markers.forEach(element => {
    value_sum += element.value;
  });

  var average = Math.round((value_sum / markers.length + Number.EPSILON) * 10) / 10;

  color = query_cbar(average,.6)

  html = '<div style="background-color:' +color+'">'+
            '<span>' + average + '</span>'
        '</div>'

  return new L.DivIcon({ html: html, className: 'marker-cluster', iconSize: new L.Point(40, 40) });
};

function onEachFeature(feature, layer) {
  delete feature.properties.model;

  var properties = Object.entries(feature.properties)

  tableContent = "<table><tbody>"

  properties.forEach(el=> {
    if (el[1] && el[0] != 'slug') {
      tableContent += '<tr><td >' + el[0] + ':  </td><td>' + el[1] + '</td></td>'
    }
  })

  tableContent += '</tbody></table>'
  layer.bindPopup(tableContent);
    
};

