None = ''
table_link_url = '';
False = false

function columnHeaders(keys) {
  var columns = [];
  keys.forEach(el => {
    columns.push({
      // title: titleize(el),
      title: el,
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

function ref_link( data, type, row, meta ) {
    // data = '<i class="fas fa-binoculars fa-lg text-dark bg-light"></i>';
    return '<a target="_blank" href="/thermoglobe/publications/' + data.toLowerCase() + '">'+data+'</a>';
    }

function site_link( data, type, row, meta ) {
    icon = '<i class="fas fa-binoculars fa-lg text-dark bg-light"></i>';
    return '<a target="_blank" href="/thermoglobe/sites/' + data + '">'+icon+'</a>';
    }

function link_slug( data, type, row, meta ) {
   data = '<i class="fas fa-binoculars fa-lg text-dark bg-light"></i>';
   return '<a target="_blank" href="' + table_options.link_url + row.slug + '">'+data+'</a>';

}

function link_doi( data, type, row, meta ) {
  if (data == undefined) {
    return " "
  }
  return "<a href=http://www.doi.org/"+data+"><i class='fas fa-globe fa-lg text-dark bg-light'></i></a>"
}

function bibtex_columnDefs(table) {

  if (typeof table.options.columnDefs == "undefined") {
    table.options.columnDefs = [];
 }
  
  if (table.columns.includes('slug')) {
    // render the first column as a link to the slug
    table.options.columnDefs.push({
      "targets": table.columns.indexOf('slug'),
      "render": link_slug,
    })
  }

  if (table.columns.includes('year')) {

    table.options.columnDefs.push({
      "targets": table.columns.indexOf('year'),
      "data": "issued",
      "render": display_year,
    },
    )
  }

  if (table.columns.includes('author')) {

    table.options.columnDefs.push({
      "targets": table.columns.indexOf('author'),
      "data": "author",
      "render": display_author,
    },
    )

  }

  if (table.columns.includes('doi')) {
    table.options.columnDefs.push({
      "targets": table.columns.indexOf('doi'),
      "data": "doi",
      "render": link_doi,
    })

  } 

  if (table.columns.includes('bibtex')) {
    table.options.columnDefs.push({
      "targets": table.columns.indexOf('bibtex'),
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

function table_from_values_list(table) {
    table.options = table_options
    table.options.columnDefs = []
    if (table.columns.includes('site_slug')) {
        // render the first column as a link to the slug
        table.options.columnDefs.push({
          "targets": table.columns.indexOf('site_slug'),
          "render": site_link,
        })
        table.columns[table.columns.indexOf('site_slug')] = ' '
      }

    if (table.columns.includes('Reference')) {
    // render the first column as a link to the slug
    table.options.columnDefs.push({
        "targets": table.columns.indexOf('Reference'),
        "render": ref_link,
    })
    }

  return create_table(table)
}

function create_table(table) {
    var table = $('#' + table.id).DataTable( {
        dom: '<"top d-flex justify-content-around align-items-center"lpf>t<"bottom"ip><"clear">',
        data: table.data,
        columns:columnHeaders(table.columns),
        ...table.options,
        });
        return table
}

function create_table_from_bibtex(table){

    var Cite = require('citation-js') 
   
    var bib = [];
    table.data.forEach(row => {
      bib.push(row.bibtex)
    });
    
    // convert bibtex list to a cite instance
    var cite = new Cite(bib)   
  
    // merge data from the cite instance with any extra columns from dataSet
    var data = []
    for (let index = 0; index < table.data.length; index++) {
      data.push({...table.data[index],...cite.data[index]})
    }
  
     var key_replacements = {
      'id':'id',
      'doi':['DOI',''],
      'year': 'issued',
      'journal': 'container-title',
    };
  
    var columns = []
    table.columns.forEach(element=> {
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
      } else if (element == 'slug') {
        //   remove "slug" from column headers
        columns.push({
            data: element,
            title: '',
            "defaultContent": "",
              })
      } else {
        columns.push({
          data: element,
          title: titleize(element),
          "defaultContent": "",
        })
      }
    });
  
    table = bibtex_columnDefs(table)
  
    var table = $('#' + table.id).DataTable( {
      dom: '<"top d-flex justify-content-around align-items-center"lpf>t<"bottom"ip><"clear">',
      data: data,
      columns:columns,
      ...table.options,
    });
    return table
    // return create_table(table,columns)
  }



// $('tbody tr').hover(function () {
//   var data = site.row( this ).data();
//   console.log(data)
//   var coordinates = new L.LatLng(data.latitude,data.longitude);
//   marker.setLatLng(coordinates);
//   marker.addTo(map)
// });


// $('#tableNav>button').click(function(e) {
//   if ($(this).hasClass('disabled')) {
//     return
//   }
//   var idClicked = e.target.id;
//   var table = $('#dataTable').DataTable();
//   table.destroy();
//   $('#dataTable>thead').empty();
//   $('#dataTable>tbody').remove();
//   table_from_values_list(dataSet[idClicked])
//   $('#dataTable th:contains("Value")').html(titleize(idClicked))
//   }
// )
