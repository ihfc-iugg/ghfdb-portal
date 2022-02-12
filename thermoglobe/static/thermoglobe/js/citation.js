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

    $('#refDownload>a').click(function () {

      let export_format = citation.format($(this).val())

      var a = document.createElement('a');

      var a = $("<a></a>")
      a.attributes({
        href: 'data:text/plain;charset=utf-8,' + encodeURIComponent(export_format),
        download: `${$(this).text()}`,
      })

      a.hide()
      a.click();



      // a.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(export_format));
      // let id = citation.data[0].id;
      // a.setAttribute('download', `${id}${$(this).text()}`);
      // a.setAttribute('download', `${$(this).text()}`);

      // a.style.display = 'none';
      // document.body.appendChild(a);
      // a.click();
      // document.body.removeChild(a);

    })

  });

