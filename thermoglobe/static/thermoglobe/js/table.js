$.fn.create_table = function(options) {

    var fields = [];
    $(options['fields']).each(function (ind, field) {
      if (typeof(field) == "object" ) {
        fields.push(field)
      } else {
        fields.push({"data": field})       
      }
    })

    this.DataTable( {
        dom: '<"top"il>rt<"bottom"p><"clear">',
        ordering: false,
        responsive: true,
        processing: true,
        serverSide: true,
        columns: fields,
        ajax: {
          type: "GET",
          url: options['url'],
          dataSrc: 'results',
          dataFilter: function(data) {
              var json = jQuery.parseJSON( data );
              json.recordsTotal = json.count;
              json.recordsFiltered = json.count;
              return JSON.stringify( json );
          },
        },
    });
  return this;
};

$.fn.dataTable.render.href = function ( href ) {
  return function ( data, type, row ) {
      return '<a href='+href+row.site.id+'>'+data+'</a>'
  }
};

$('tbody tr').hover(function () {
  var data = site.row( this ).data();
  console.log(data)
  var coordinates = new L.LatLng(data.latitude,data.longitude);
  marker.setLatLng(coordinates);
  marker.addTo(map)
});

$('#dataTable').on( 'mouseenter', 'tbody tr', function () {
  var data = table.row( this ).data();
  var coordinates = new L.LatLng(data[2],data[3]);
  tmpMarker.setLatLng(coordinates);
  tmpMarker.addTo(map)
} );

$('#dataTable').on( 'click', 'tbody tr', function () {
  var data = table.cells( this, '' ).render( 'display' );

  var lat, lon = none,none;

  var popup = '<table>'
  table.columns().header().each(function(column, index){
    if (column.innerHTML.toLowerCase() === 'latitude') {
      lat = data[index]
    } else if (column.innerHTML.toLowerCase() === 'longitude')  {
      lon = data[index]
    }
    popup += `<tr><td>${column.innerHTML}:</td><td>${data[index]}</td></tr>`
  })
  var coordinates = new L.LatLng(lat, lon);
  new L.marker(coordinates).addTo(map).bindPopup(popup + '</table>');

} );


