
$( document ).ready(function() {
  $('.plot-banner').appear();
  var loaded = [];

  $(document.body).on('appear', '.plot-banner', function(e, $affected) {
    //get all plots within the plot-banner class that appears in the viewport
    var $plots = $(this).find('.plot')
   
    //for each plot in the current plot-banner...
    $plots.each(function () {

        var id =  $( this ).attr('data') + '-' + $( this ).attr('type');
        //check if it's already been loaded
        if (!loaded.includes(id)) {
          //if not, load the plot and add it to the loaded list
          loaded.push(id)
          $( this ).attr('loaded');
          $( this ).attr('id',id);
          plot($( this ))
      }
    })
  });



  $('.toggle').mouseup(function () {
    map.invalidateSize(true)
  })
  

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

  if ($('#map').length) {
    $('.toggle').addClass('alt')
  }

});

// convert bibtex list to a cite instance
function flattenObj(obj, res = {}){
  for(let key in obj){
      if(typeof obj[key] == 'object'){
          flattenObj(obj[key], res);
      } else {
          res[key] = obj[key];
      }
  }
  return res;
}

function plot(el) {
  $.getJSON({
      url: '/thermoglobe/plots',
      data: {'data':el.attr('data'), 'type':el.attr('type')},
      success: function (data) {
        el.replaceWith(data.result)
      },
    }) 
}
