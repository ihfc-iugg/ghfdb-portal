var Cite = require('citation-js')

$(document).ready(function(){
    // if (!data) {
    //   //shows the warning sign about a bad reference
    //     $('.d-none').toggleClass('.d-none d-block');
    //     $(".referenceCardTitle").html('Unknown')
    // }

    //download citation button
    $('.export_bibtex').click(function(){
        download(data.id.concat('.bib'),bibtex);
     });

     //fills out the publication card if it exists
     if ($('#publicationInfo').length ) {
      var refData = flattenObj(citation.format('bibtex',{format:'object'})[0])

      $("#refTitle").html(refData.title)
      $("#refLabel").prepend(refData.label)

      exclude = ['date','author','month','title','label']; //otherwise too much clutter
      Object.entries(refData).forEach(function (el) {
        if (el[0] == 'doi') {
          if (el[1].includes('doi.org/')) {
            el[1] = el[1].split('doi.org/')[1]
          }
          $('#article-doi').attr('href',`//www.doi.org/${el[1]}`)         
        } else if (el[0] == 'url') {
          $("#publicationInfo>dl").append(`<dt>${el[0]}:</dt><dd><a href="${el[1]}">${el[1]}</a></dd>`)
        } else if (!exclude.includes(el[0])) {
          $("#publicationInfo>dl").append(`<dt>${el[0]}:</dt><dd>${el[1]}</dd>`)
        }

      })
    }

    $('#refDownload>a').click(function () {

      let type = $(this).attr('value')
      let export_format = citation.format(type)
      let id = citation.data[0].id;

      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(export_format));
      element.setAttribute('download', `${id}${$(this).text()}`);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

    })

  });

