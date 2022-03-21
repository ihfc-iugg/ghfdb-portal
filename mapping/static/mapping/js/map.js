$(function(){map.fitWorld();})


var baseLayers = {
  "Dark Gray": L.esri.basemapLayer('DarkGray',{detectRetina: true}),
  "Imagery": L.esri.basemapLayer('Imagery',{detectRetina: true}),
  "Oceans": L.esri.basemapLayer('Oceans',{detectRetina: true}),
  "Topographic": L.esri.basemapLayer('Topographic',{detectRetina: true}),
  "Nat Geo": L.esri.basemapLayer('NationalGeographic',{detectRetina: true}),
};

var map = L.map('map', {
  layers: [baseLayers['Oceans']],
  minZoom: 3,
  maxZoom: 10,
  worldCopyJump: true,
  fullscreenControl: true,
  zoomControl:false,
    })

L.control.layers(baseLayers).addTo(map);
L.control.zoom({position: 'topright'}).addTo(map);
L.control.scale({position: 'bottomright'}).addTo(map);

clusters = L.markerClusterGroup({    
  chunkedLoading: true,
  disableClusteringAtZoom: 6,
  spiderfyOnMaxZoom: false,
});
map.addLayer(clusters);

map.spin(true)
var data = new L.Util.ajax(get_url()).then(processData)


function processData(data) {

  markers = []

  data.forEach(site => {
    var m = L.circleMarker([site[1], site[2]], {
        radius: 5, 
        fill:true,
        fillOpacity:0.75,
        fillColor: 'rgb(255,0,0,1)',
        color:'rgb(200,0,0,1)', //stroke colour
        weight:1, //stroke weight in pixels
        });
    m.on('click',getMarkerPopup)
    m.url = `/api/v1/sites/${site[0]}`
    markers.push(m)
  });

  var sites = L.featureGroup(markers)
  clusters.addLayer(sites);


  map.spin(false)
  map.flyToBounds(sites.getBounds())
  
}



function processLargeArrayAsync(array, fn, chunk, context) {
  context = context || window;
  chunk = chunk || 100;
  var index = 0;
  function doChunk() {
      var cnt = chunk;
      while (cnt-- && index < array.length) {
          // callback called with args (value, index, array)
          fn.call(context, array[index], index, array);
          ++index;
      }
      if (index < array.length) {
          // set Timeout for async iteration
          setTimeout(doChunk, 1);
      }
  }    
  doChunk();    
}

function getMarkerPopup(e) {
  var marker = this;
  if (marker.getPopup() == undefined) {
      $.get(this.url, function(data) {
      var web_url = data.web_url;
      var site_name = data.site_name;

      to_delete = ['site_name','link','url','geom','date_added','description']
      to_delete.forEach(el=> {
          delete data[el]
        })
      var table_content = ""
      Object.entries(data).forEach(el=> {
        table_content += `<tr><td>${el[0]}</td><td>${el[1]}</td></td>`
      })

      var content = `<h2><a href='${web_url}' target="_blank">${site_name}</a></h2>
              <table class='table table-responsive' style='max-height:500px;'><tbody>
                ${table_content}
              </tbody></table>`

    marker.bindPopup(content,{maxHeight: 600, maxWidth:600})
    marker.openPopup()
    })
  }
}

function get_url() {
  url = "/api/v1/sites/coordinates/"

  if ($('#map').data() != {}) {
    url += '?'
    $.each($('#map').data(), function (k,v) {
      if (v != undefined) {
        url += `${k}=${v}`
      }
    })
  }

  return url
}

function updateMap() {

  url = '/api/geojson/site/?'+ encodeURI($('#map-filter-form').serialize()) + encodeURI(reference)
  geojson.refresh(url)
  clusters.clearLayers()
  clusters.addLayer(geojson)
  map.flyToBounds(geojson.getBounds())
}

function filterSites(json) {
  var att=json.properties;
  var lat_gt = $("input[name='latitude__gt']").val();
  return (att.latitude > lat_gt)
}
