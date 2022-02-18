$.extend( $.fn.dataTable.defaults, {
  dom: '<"top"il>rt<"bottom"p><"clear">',
  ordering: false,
  responsive: true,
  processing: true,
  serverSide: true,
  pageLength: 50,
} );

$.fn.create_table = function(options) {
    colDefs = [];
    // web_url = $(this).attr("data-weburl");
    // console.log(web_url)
    // prepend = $(this).attr("data-linkPrepend");

    // if (link) {
      // colDefs.push({targets: [0], render: $.fn.dataTable.render.href(prepend,web_url)})
    var colDefs = [{targets: [0], render: $.fn.dataTable.render.href()}];
    // }

    this.DataTable( {
        columnDefs: colDefs,
        ajax: {
          type: "GET",
          url: $(this).attr("data-url"),
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
      return '<a href='+row.site.web_url+'>'+data+'</a>'
      // return '<a href='+href+row.site.id+'>'+data+'</a>'
  }
};

// $('tbody tr').hover(function () {
//   var data = site.row( this ).data();
//   console.log(data)
//   var coordinates = new L.LatLng(data.latitude,data.longitude);
//   marker.setLatLng(coordinates);
//   marker.addTo(map)
// });

// $('#dataTable').on( 'mouseenter', 'tbody tr', function () {
//   var data = table.row( this ).data();
//   var coordinates = new L.LatLng(data[2],data[3]);
//   tmpMarker.setLatLng(coordinates);
//   tmpMarker.addTo(map)
// } );

// $('#dataTable').on( 'click', 'tbody tr', function () {
//   var data = table.cells( this, '' ).render( 'display' );

//   var lat, lon = none,none;

//   var popup = '<table>'
//   table.columns().header().each(function(column, index){
//     if (column.innerHTML.toLowerCase() === 'latitude') {
//       lat = data[index]
//     } else if (column.innerHTML.toLowerCase() === 'longitude')  {
//       lon = data[index]
//     }
//     popup += `<tr><td>${column.innerHTML}:</td><td>${data[index]}</td></tr>`
//   })
//   var coordinates = new L.LatLng(lat, lon);
//   new L.marker(coordinates).addTo(map).bindPopup(popup + '</table>');

// } );


