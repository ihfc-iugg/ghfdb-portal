function historical_heat_flow(id,data) {

    var trace1 = {
      x: data[0].x,
      y: data[0].y,
      name: 'Publications',
      type: 'scatter'
    };
    
    var trace2 = {
      x: data[1].x,
      y: data[1].y,
      name: 'Heat flow estimates',
      yaxis: 'y2',
      type: 'scatter'
    };
    
    var data = [trace1, trace2];
    
    var layout = {
      // title: 'Historical heat flow contributions',
      yaxis: {
        showgrid: false,
        title: 'Number of publications'},
      yaxis2: {
        showgrid: false,
        title: 'Number of heat flow estimates',
        overlaying: 'y',
        side: 'right'
      },
      xaxis: {
        showgrid: false,
        title: {
          text: "Year",
        },
      },
      legend: {
        x: 0,
        xanchor: 'left',
        y: 1,
        yanchor:'top',
      },
      // paper_bgcolor:'rgba(0,0,0,0)',
      // plot_bgcolor:'rgba(0,0,0,0)'
    };
    
    var config = {responsive: true}

    Plotly.newPlot(id, data, layout, config);

}

function heat_flow_hist(fig_id,data) {
  var opacity = 0.6
  var nbins = 20

  var trace1 = {
    x: data[0],
    name: 'Continental',
    type: 'histogram',
    'opacity': opacity,
    'nbinsx':nbins,

  };
  
  var trace2 = {
    x: data[1],
    name: 'Oceanic',
    type: 'histogram',
    'opacity': opacity,
    'nbinsx':nbins,

  };

  var data = [trace1,trace2]

  var layout = {
    // title:{
    //   text: "Heat Flow",
    //   y:0.9,
    //   x:0.5,
    //   xanchor: 'center',
    //   yanchor: 'top'
    // },
    legend: {
      x: 1,
      xanchor: 'right',
      y: 1
    },
    xaxis: {
      title: {
        text: "Heat Flow [mW/m2]",
      },
    },
    barmode:'overlay',
    margin:{
      l:50,
      r:50,
      pad:10
    },
    paper_bgcolor:'transparent',
    plot_bgcolor: 'transparent',

  }

  var config = {responsive: true}

  Plotly.newPlot(fig_id, data, layout, config);

}

function entries_pie_chart(input,id) {

  var data = [{
    values: input[1].y,
    labels: input[1].x,
    type: 'pie'
  }];
  
  var layout = {
    title:{
      text: input[0],
      xanchor: 'center',
      yanchor: 'top'
    },
 
  };
  
  Plotly.newPlot(id, data, layout);
}

function data_counts(fig_id,data,type) {
  
  data = remove_zero_counts(data)

  var yVals = Object.keys(data)
  var xVals = Object.values(data)
  var layout = {
    title:{
      text: "Data Totals",
      y:0.9,
      x:0.5,
      xanchor: 'center',
      yanchor: 'top'
    },
    yaxis: {
      ticks: '',
      showticklabels: false,
      // tickmode: "array",
      // tickvals: [5, 4, 3, 2, 1, 0],
      // ticktext: yVals,
    },
    margin:{
      l:10,
      r:10,
      // b:35,
      // t:25,
      // pad:4,
    },
    xaxis: {
      title: {
        text: "Data Counts",
      },
    },
  }

  if (type == 'bar') {

    var data = [{
      type: 'bar',
      x: xVals,
      y: yVals,
      
      orientation: 'h',
      text: yVals.map(String),
      textposition: 'inside',
      insidetextanchor:'middle',
      hoverinfo: 'none',
    }];

  } else {

    var data = [{
      type: 'pie',
      values: xVals,
      labels: yVals,
      textinfo:'label+value',
      showlegend: false,
      // text: yVals.map(String),
      textposition: 'inside',
      insidetextanchor:'middle',
      hoverinfo: 'none',
    }];
  }

  var config = {responsive: true}

  Plotly.newPlot(fig_id, data, layout, config);


}

function remove_zero_counts(data) {

  let entries = Object.entries(data);

  var new_data = {};

  for (const [key, count] of entries) {
    if (count > 0) {
      new_key = key.replace('_',' ')
      new_data[new_key] = count
    }
  }
  return new_data


}
