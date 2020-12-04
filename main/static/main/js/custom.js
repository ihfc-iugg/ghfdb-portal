$(function() {
  // make sure the nav pills are working on the multi tables
  $('.nav-pills a').click(function(){
    $('.nav-pills a').each(function(){
      $( this ).removeClass('primary')
    })
    $( this ).addClass('primary')
  })
  // makes tooltips interactive
  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

  $('.toggle').mouseup(function () {
    map.invalidateSize(true)
  })

  if ($('#map').length) {
    $('.toggle').addClass('alt')
  }


  var $plots = $('.plot').appear();

  var loaded = [];

  // ensures plots in the viewport on load get loaded without scrolling
  $(document.body).on('appear', '.plot', function(e, $affected) {
    $affected.each(function () {
        var id =  $( this ).attr('type') + '-' + $( this ).attr('field');
        
        //check if it's already been loaded
        if (!loaded.includes(id)) {
          //if not, load the plot and add it to the loaded list
          loaded.push(id)
          $( this ).attr('id',id);
          plot($( this ))
      }
    })
  });

  $.force_appear()

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
      url: $(location).attr('href'),
      data: {
        'type':el.attr('type'),
        'field':el.attr('field'),
      },
      success: function (data) {
        el.replaceWith(data.result)
      },
    }) 
}

$('.custom-file-input').on('change',function(){
  var fileName = $(this).val();
  fileName = fileName.split('\\')[2]
  $(this).next('.custom-file-label').html(fileName);
})