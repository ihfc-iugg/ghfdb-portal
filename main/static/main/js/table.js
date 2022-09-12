
$.fn.create_table = function(options) {
    var detailsUrl = $(this).data('web-url')
    var colDefs = [{targets: [0], render: $.fn.dataTable.render.href(detailsUrl)}];

    this.DataTable( {
        columnDefs: colDefs,
        ajax: {
          type: "GET",
          url: $(this).data("url"),
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
      return '<a href='+href+row.id+'>'+data+'</a>'
  }
};

$.extend( $.fn.dataTable.defaults, {
  dom: '<"top"ipl>rt<"bottom"p><"clear">',
  ordering: false,
  responsive: true,
  processing: true,
  serverSide: true,
  pageLength: 50,
  // hides the length menu and paginator if number of data don't exceed max page rows
  preDrawCallback: function (settings) {
    var api = new $.fn.dataTable.Api(settings);
    // hides paginator
    $(this)
        .closest('.dataTables_wrapper')
        .find('.dataTables_paginate')
        .toggle(api.page.info().pages > 1);

    // hides length menu
    $(this)
        .closest('.dataTables_wrapper')
        .find('.dataTables_length')
        .toggle(settings.aLengthMenu[0][0] != -1 && settings.aLengthMenu[0][0] < api.page.info().recordsTotal);
},
} );

// $('tbody tr').hover(function () {
//   var data = site.row( this ).data();
//   console.log(data)
//   var coordinates = new L.LatLng(data.lat,data.lng);
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
//     if (column.innerHTML.toLowerCase() === 'lat') {
//       lat = data[index]
//     } else if (column.innerHTML.toLowerCase() === 'lng')  {
//       lon = data[index]
//     }
//     popup += `<tr><td>${column.innerHTML}:</td><td>${data[index]}</td></tr>`
//   })
//   var coordinates = new L.LatLng(lat, lon);
//   new L.marker(coordinates).addTo(map).bindPopup(popup + '</table>');

// } );


