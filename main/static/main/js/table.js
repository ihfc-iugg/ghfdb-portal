None = ''

function tabulate_geojson(features) {
  var dataSet = [];

  features.forEach(element => {
    dataSet.push(element.properties)
  });

  return dataSet
}
function columnHeaders(keys) {

  var columns = [];
  for (let index = 0; index < keys.length; index++) {
    const element = keys[index];
    var col = {
      data: element,
      title: titleize(element),
    }
    columns.push(col)
  }

  return columns
}
function add_complex_header(headers) {
  var header = '<tr>'
  $('th').addClass('border-0')

  headers.forEach(element => {
    if (element[1]) {
      header += "<th class='text-center border-bottom' colspan=" + element[0] + ">" + element[1] + "</th>"
    } else{
      header += "<th class='border-0' colspan=" + element[0] + ">" + element[1] + "</th>"
    }
  });

  header += '</tr>'

  // $('#dataTable>thead').prepend(header)
  $('#geoTable>thead').prepend(header)


}
function titleize(sentence) {
  if(!sentence.split) return sentence;
  var _titleizeWord = function(string) {
          return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
      },
  result = [];
  sentence = sentence.split('__')[0]
  sentence.split("_").forEach(function(w) {
      result.push(_titleizeWord(w));
  });
  return result.join(" ");
}
function convert_bibtex( data, type, row, meta ) {

  var Cite = require('citation-js') 
  var opt = {
    format: 'string',
    style:'citation-apa',
    type: 'html',
    lang: 'en-US',
}    
 
  var cite = new Cite(data)   
 
  return cite.get(opt)

}
function link_slug( data, type, row, meta ) {
  if (data == undefined) {
    data = '<i class="fas fa-binoculars fa-lg text-dark bg-light"></i>';
  }
  return '<a target="_blank" href=' + link_url + row.slug + '>'+data+'</a>';
}

function link_doi( data, type, row, meta ) {
  if (data == undefined) {
    return " "
  }
  return "<a href=http://www.doi.org/"+data+"><i class='fas fa-globe fa-lg text-dark bg-light'></i></a>"
}

function add_columnDefs(keys,columnDefs) {

  if (typeof columnDefs == "undefined") {
    var columnDefs = []
 }

  if (keys.includes('slug')) {
    // render the first column as a link to the slug
    columnDefs.push({
      "targets": 0,
      "render": link_slug
    })

    // Set the original slug column to be invisible 
    columnDefs.push({
      "targets":keys.indexOf('slug'),
      'visible':false,
    })
  }

  if (keys.includes('year')) {

    columnDefs.push({
      "targets": keys.indexOf('year'),
      "data": "issued",
      "render": display_year,
    },
    )
  }

  if (keys.includes('author')) {

    columnDefs.push({
      "targets": keys.indexOf('author'),
      "data": "author",
      "render": display_author,
    },
    )

  }

  if (keys.includes('doi')) {
    columnDefs.push({
      "targets": keys.indexOf('doi'),
      "data": "doi",
      "render": link_doi,
    })

  } 

  if (keys.includes('bibtex')) {
    columnDefs.push({
      "targets": keys.indexOf('bibtex'),
      'visible': false,
    })

  }

  return columnDefs

}

function display_year( data, type, row, meta ) {
  if (data == undefined) {return ''}
  return data['date-parts'][0][0]
}

function author_display_format(author) {
  var keys = Object.keys(author)
    // console.log(author)

  if (keys.includes('literal')) {
    return author['literal']
  } else if (keys.includes('given')) {
    return author['family'] + ', ' + author['given'][0] +'.'
  } else {
    return author['family']
  }

}

function display_author(data, type, row, meta) {
  if (data == undefined) {return ''}
  if (data.length == 1) {
    return author_display_format(data[0])
  } else if (data.length == 2) {
    return author_display_format(data[0]) + ' & ' + author_display_format(data[1])
  } else {
    return author_display_format(data[0]) + ' et. al.'
  }

}
function table_from_bibtex(dataSet,headers,options){

  if (options == undefined) {
    options = {};
  }

  var Cite = require('citation-js') 
 
  // create a list of only the bibtex data
  var bib = [];
  dataSet.forEach(element => {
    bib.push(element.bibtex)
  });
  
  // convert bibtex list to a cite instance
  var cite = new Cite(bib)   

  // merge data from the cite instance with any extra columns from dataSet
  var data = []
  for (let index = 0; index < dataSet.length; index++) {
    data.push({...dataSet[index],...cite.data[index]})
    // console.log(index,data[index]['id'],data[index]['slug'])
    // if (index == 111) {
    //   x=9
    // }
  }

  // create a list of column headers from dataSet but exclude the bibtex key
  var tmp = dataSet[0];
  var keys = Object.keys(tmp);

  // provide an extra column at the start of table for slug links
  if (keys.includes('slug')) {
    headers.unshift('')
  }
  // combine the given headers and the extra keys from dataset
  headers = [...headers,...keys]

   var key_replacements = {
    'id':'id',
    'doi':['DOI',''],
    'year': 'issued',
    'journal': 'container-title',
  };

  var columns = []
  headers.forEach(element=> {
    const index = Object.keys(key_replacements).indexOf(element);
    if (index >= 0) {
      if (Array.isArray(key_replacements[element])) {
        columns.push({
          data: key_replacements[element][0],
          title: key_replacements[element][1],
          "defaultContent": "",
        })
      } else {
        columns.push({
          data: key_replacements[element],
          title: titleize(element),
          "defaultContent": "",
        })
      }
    } else{
      columns.push({
        data: element,
        title: titleize(element),
        "defaultContent": "",

      })
    }
  });

  keys, options.columnDefs = add_columnDefs(headers)

  return create_table(data,columns,options,'#dataTable')
}

function table_from_geojson(dataSet) {
  var keys = Object.keys(dataSet.features[0].properties)
  var dataSet = tabulate_geojson(dataSet.features)

  keys, table_options.columnDefs = add_columnDefs(keys,table_options.columnDefs)
  return create_table(dataSet,keys,table_options,'#geoTable')
}

function table_from_list(dataSet) {
  var keys = Object.keys(dataSet[0])
  table_options = {};
  keys, table_options.columnDefs = add_columnDefs(keys,table_options.columnDefs)
  return create_table(dataSet,keys,table_options,'#dataTable')
}

function create_table(data,columns,options,table_id) {

  if (typeof(columns[0]) == 'string') {
    columns = columnHeaders(columns)
  }

  var table = $(table_id).DataTable( {
    dom: '<"top d-flex justify-content-around align-content-center"lpf>t<"bottom"ip><"clear">',
    data: data,
    columns:columns,
    ...options,
  });

  return table

}


$('tbody tr').hover(function () {
  var data = table.row( this ).data();
  var coordinates = new L.LatLng(data.latitude,data.longitude);
  marker.setLatLng(coordinates);
  marker.addTo(map)
});


$('#tableNav>button').click(function(e) {
  if ($(this).hasClass('disabled')) {
    return
  }
  var idClicked = e.target.id;
  var table = $('#dataTable').DataTable();
  table.destroy();
  $('#dataTable>thead').empty();
  $('#dataTable>tbody').remove();
  table_from_list(dataSet[idClicked])
  $('#dataTable th:contains("Value")').html(titleize(idClicked))



  }
)






// var table = $('#dataTable').DataTable( {
//   dom: '<"top d-flex justify-content-around align-content-center"lpf>t<"bottom"ip><"clear">',
//   data: dataSet,
//   columns:columns,
//   columnDefs:table_options.columnDefs,
//   ...table_options,
//   createdRow: function ( row, data, index ) {
//     if ( data.slug ) {
//         $('td', row).eq(0).wrapInner('<a href=' + link_url + data.slug + '/>');
//         }
//     }
// } );