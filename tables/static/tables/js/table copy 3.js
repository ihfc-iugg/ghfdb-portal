None = ''
table_link_url = '';


function columnHeaders(keys) {
  var columns = [];
  keys.forEach(el => {
    columns.push({
      title: titleize(el),
    })
  });

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
  return '<a target="_blank" href=' + table_link_url + row.slug + '>'+data+'</a>';
}

function link_doi( data, type, row, meta ) {
  if (data == undefined) {
    return " "
  }
  return "<a href=http://www.doi.org/"+data+"><i class='fas fa-globe fa-lg text-dark bg-light'></i></a>"
}

function add_columnDefs(table) {

  if (typeof table.options.columnDefs == "undefined") {
    table.options.columnDefs = [];
 }
  
  if (table.headers.includes('slug')) {
    // render the first column as a link to the slug
    table.options.columnDefs.push({
      "targets": 0,
      "render": link_slug
    })

    // Set the original slug column to be invisible 
    table.options.columnDefs.push({
      "targets":table.headers.indexOf('slug'),
      'visible':false,
    })
  }

  if (table.headers.includes('year')) {

    table.options.columnDefs.push({
      "targets": table.headers.indexOf('year'),
      "data": "issued",
      "render": display_year,
    },
    )
  }

  if (table.headers.includes('author')) {

    table.options.columnDefs.push({
      "targets": table.headers.indexOf('author'),
      "data": "author",
      "render": display_author,
    },
    )

  }

  if (table.headers.includes('doi')) {
    table.options.columnDefs.push({
      "targets": table.headers.indexOf('doi'),
      "data": "doi",
      "render": link_doi,
    })

  } 

  if (table.headers.includes('bibtex')) {
    table.options.columnDefs.push({
      "targets": table.headers.indexOf('bibtex'),
      'visible': false,
    })

  }

  return table

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

function get_table_options() {
    if (table_options == undefined) {
        return table_options
    } else {
        return {}
    }
}

function table_from_bibtex(table){

  var Cite = require('citation-js') 
 
  // create a list of only the bibtex data

  var ind = table.headers.indexOf('bibtex')
  var bib = [];
  table.data.forEach(row => {
    bib.push(row[ind])
  });
  
  // convert bibtex list to a cite instance
  var cite = new Cite(bib)   

  // merge data from the cite instance with any extra columns from dataSet
  var data = []
  for (let index = 0; index < table.data.length; index++) {
    data.push(...table.data[index],...Object.values(cite.data[index]))
    // data.push({...dataSet[index],...cite.data[index]})
  }


  // create a list of column headers from dataSet
//   var tmp = dataSet[0];
//   var keys = Object.keys(tmp);


  // provide an extra column at the start of table for slug links
  if (table.headers.includes('slug')) {
    table.headers.unshift('')
  }

  table.headers = [...table.headers, ...Object.keys(cite.data[0])]

   var key_replacements = {
    'id':'id',
    'doi':['DOI',''],
    'year': 'issued',
    'journal': 'container-title',
  };

//   var new_headers = []
//   table.headers.forEach(element => {
//     if (Objects.values(key_replacements).includes(element)) {
//         new_headers.push(key_replacements.element)
//     }
//   });
//   need to start replacing citation headers with readable names



  var columns = []
  table.headers.forEach(element=> {
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

  table = add_columnDefs(table)

  return create_table(table,table.headers)
}

function table_from_geojson(dataSet) {
  var keys = Object.keys(dataSet.features[0].properties)
  var dataSet = tabulate_geojson(dataSet.features)

  keys, table_options.columnDefs = add_columnDefs(keys,table_options.columnDefs)
  return create_table(dataSet,keys,table_options,'#geoTable')
}

function table_from_values(data) {

  var table_headers = Object.keys(data[0])
  new_data = []
  data.forEach(el => {
    new_data.push(Object.values(el))
  });
  table_from_values_list(table_headers, new_data)
}

function table_from_values_list(table, headers, data, id) {
  options = get_table_options()
  headers, options.columnDefs = add_columnDefs(headers,options.columnDefs)
  return create_table(data,headers,options,id)
}

function create_table(table, columns) {

  if (typeof(columns[0]) == 'string') {
    columns = columnHeaders(columns)
  }

  var table = $('#' + table.id).DataTable( {
    dom: '<"top d-flex justify-content-around align-items-center"lpf>t<"bottom"ip><"clear">',
    data: table.data,
    columns:columns,
    ...table.options,
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
  table_from_values_list(dataSet[idClicked])
  $('#dataTable th:contains("Value")').html(titleize(idClicked))
  }
)
