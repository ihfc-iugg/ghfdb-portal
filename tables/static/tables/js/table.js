try {
  var Cite = require('citation-js')
}
catch(err) {}

var country_list = {
    1: 'Antigua and Barbuda',
    2: 'Algeria',
    3: 'Azerbaijan',
    4: 'Albania',
    5: 'Armenia',
    6: 'Angola',
    7: 'American Samoa',
    8: 'Argentina',
    9: 'Australia',
    10: 'Bahrain',
    11: 'Barbados',
    12: 'Bermuda',
    13: 'Bahamas',
    14: 'Bangladesh',
    15: 'Belize',
    16: 'Bosnia and Herzegovina',
    17: 'Bolivia',
    18: 'Burma',
    19: 'Benin',
    20: 'Solomon Islands',
    21: 'Brazil',
    22: 'Bulgaria',
    23: 'Brunei Darussalam',
    24: 'Canada',
    25: 'Cambodia',
    26: 'Sri Lanka',
    27: 'Congo',
    28: 'Democratic Republic of the Congo',
    29: 'Burundi',
    30: 'China',
    31: 'Afghanistan',
    32: 'Bhutan',
    33: 'Chile',
    34: 'Cayman Islands',
    35: 'Cameroon',
    36: 'Chad',
    37: 'Comoros',
    38: 'Colombia',
    39: 'Costa Rica',
    40: 'Central African Republic',
    41: 'Cuba',
    42: 'Cape Verde',
    43: 'Cook Islands',
    44: 'Cyprus',
    45: 'Denmark',
    46: 'Djibouti',
    47: 'Dominica',
    48: 'Dominican Republic',
    49: 'Ecuador',
    50: 'Egypt',
    51: 'Ireland',
    52: 'Equatorial Guinea',
    53: 'Estonia',
    54: 'Eritrea',
    55: 'El Salvador',
    56: 'Ethiopia',
    57: 'Austria',
    58: 'Czech Republic',
    59: 'French Guiana',
    60: 'Finland',
    61: 'Fiji',
    62: 'Falkland Islands (Malvinas)',
    63: 'Micronesia, Federated States of',
    64: 'French Polynesia',
    65: 'France',
    66: 'Gambia',
    67: 'Gabon',
    68: 'Georgia',
    69: 'Ghana',
    70: 'Grenada',
    71: 'Greenland',
    72: 'Germany',
    73: 'Guam',
    74: 'Greece',
    75: 'Guatemala',
    76: 'Guinea',
    77: 'Guyana',
    78: 'Haiti',
    79: 'Honduras',
    80: 'Croatia',
    81: 'Hungary',
    82: 'Iceland',
    83: 'India',
    84: 'Iran (Islamic Republic of)',
    85: 'Israel',
    86: 'Italy',
    87: "Cote d'Ivoire",
    88: 'Iraq',
    89: 'Japan',
    90: 'Jamaica',
    91: 'Jordan',
    92: 'Kenya',
    93: 'Kyrgyzstan',
    94: "Korea, Democratic People's Republic of",
    95: 'Kiribati',
    96: 'Korea, Republic of',
    97: 'Kuwait',
    98: 'Kazakhstan',
    99: "Lao People's Democratic Republic",
    100: 'Lebanon',
    101: 'Latvia',
    102: 'Belarus',
    103: 'Lithuania',
    104: 'Liberia',
    105: 'Slovakia',
    106: 'Liechtenstein',
    107: 'Libyan Arab Jamahiriya',
    108: 'Madagascar',
    109: 'Martinique',
    110: 'Mongolia',
    111: 'Montserrat',
    112: 'The former Yugoslav Republic of Macedonia',
    113: 'Mali',
    114: 'Morocco',
    115: 'Mauritius',
    116: 'Mauritania',
    117: 'Malta',
    118: 'Oman',
    119: 'Maldives',
    120: 'Mexico',
    121: 'Malaysia',
    122: 'Mozambique',
    123: 'Malawi',
    124: 'New Caledonia',
    125: 'Niue',
    126: 'Niger',
    127: 'Aruba',
    128: 'Anguilla',
    129: 'Belgium',
    130: 'Hong Kong',
    131: 'Northern Mariana Islands',
    132: 'Faroe Islands',
    133: 'Andorra',
    134: 'Gibraltar',
    135: 'Isle of Man',
    136: 'Luxembourg',
    137: 'Macau',
    138: 'Monaco',
    139: 'Palestine',
    140: 'Montenegro',
    141: 'Mayotte',
    142: 'Åland Islands',
    143: 'Norfolk Island',
    144: 'Cocos (Keeling) Islands',
    145: 'Antarctica',
    146: 'Bouvet Island',
    147: 'French Southern and Antarctic Lands',
    148: 'Heard Island and McDonald Islands',
    149: 'British Indian Ocean Territory',
    150: 'Christmas Island',
    151: 'United States Minor Outlying Islands',
    152: 'Vanuatu',
    153: 'Nigeria',
    154: 'Netherlands',
    155: 'Norway',
    156: 'Nepal',
    157: 'Nauru',
    158: 'Suriname',
    159: 'Nicaragua',
    160: 'New Zealand',
    161: 'Paraguay',
    162: 'Peru',
    163: 'Pakistan',
    164: 'Poland',
    165: 'Panama',
    166: 'Portugal',
    167: 'Papua New Guinea',
    168: 'Guinea-Bissau',
    169: 'Qatar',
    170: 'Reunion',
    171: 'Romania',
    172: 'Republic of Moldova',
    173: 'Philippines',
    174: 'Puerto Rico',
    175: 'Russia',
    176: 'Rwanda',
    177: 'Saudi Arabia',
    178: 'Saint Kitts and Nevis',
    179: 'Seychelles',
    180: 'South Africa',
    181: 'Lesotho',
    182: 'Botswana',
    183: 'Senegal',
    184: 'Slovenia',
    185: 'Sierra Leone',
    186: 'Singapore',
    187: 'Somalia',
    188: 'Spain',
    189: 'Saint Lucia',
    190: 'Sudan',
    191: 'Sweden',
    192: 'Syrian Arab Republic',
    193: 'Switzerland',
    194: 'Trinidad and Tobago',
    195: 'Thailand',
    196: 'Tajikistan',
    197: 'Tokelau',
    198: 'Tonga',
    199: 'Togo',
    200: 'Sao Tome and Principe',
    201: 'Tunisia',
    202: 'Turkey',
    203: 'Tuvalu',
    204: 'Turkmenistan',
    205: 'United Republic of Tanzania',
    206: 'Uganda',
    207: 'United Kingdom',
    208: 'Ukraine',
    209: 'United States',
    210: 'Burkina Faso',
    211: 'Uruguay',
    212: 'Uzbekistan',
    213: 'Saint Vincent and the Grenadines',
    214: 'Venezuela',
    215: 'British Virgin Islands',
    216: 'Viet Nam',
    217: 'United States Virgin Islands',
    218: 'Namibia',
    219: 'Wallis and Futuna Islands',
    220: 'Samoa',
    221: 'Swaziland',
    222: 'Yemen',
    223: 'Zambia',
    224: 'Zimbabwe',
    225: 'Indonesia',
    226: 'Guadeloupe',
    227: 'Netherlands Antilles',
    228: 'United Arab Emirates',
    229: 'Timor-Leste',
    230: 'Pitcairn Islands',
    231: 'Palau',
    232: 'Marshall Islands',
    233: 'Saint Pierre and Miquelon',
    234: 'Saint Helena',
    235: 'San Marino',
    236: 'Turks and Caicos Islands',
    237: 'Western Sahara',
    238: 'Serbia',
    239: 'Holy See (Vatican City)',
    240: 'Svalbard',
    241: 'Saint Martin',
    242: 'Saint Barthelemy',
    243: 'Guernsey',
    244: 'Jersey',
    245: 'South Georgia South Sandwich Islands',
    246: 'Taiwan'}

var seas_list = {'1': 'Baltic Sea',
    '10': 'Laptev Sea',
    '11': 'East Siberian Sea',
    '12': 'Chukchi Sea',
    '13': 'Beaufort Sea',
    '14': 'The Northwestern Passages',
    '14A': 'Baffin Bay',
    '15': 'Davis Strait',
    '15A': 'Labrador Sea',
    '16': 'Hudson Bay',
    '16A': 'Hudson Strait',
    '17': 'Arctic Ocean',
    '17A': 'Lincoln Sea',
    '18': 'Inner Seas off the West Coast of Scotland',
    '19': "Irish Sea and St. George's Channel",
    '1a': 'Gulf of Bothnia',
    '1b': 'Gulf of Finland',
    '1c': 'Gulf of Riga',
    '2': 'Kattegat',
    '20': 'Bristol Channel',
    '21': 'English Channel',
    '21A': 'Celtic Sea',
    '22': 'Bay of Biscay',
    '23': 'North Atlantic',
    '24': 'Gulf of St. Lawrence',
    '25': 'Bay of Fundy',
    '26': 'Gulf of Mexico',
    '27': 'Caribbean Sea',
    '28a': 'Strait of Gibraltar',
    '28A': 'Mediterranean Sea - Western Basin',
    '28b': 'Alboran Sea',
    '28B': 'Mediterranean Sea - Eastern Basin',
    '28c': 'Balearic (Iberian Sea)',
    '28d': 'Ligurian Sea',
    '28e': 'Tyrrhenian Sea',
    '28f': 'Ionian Sea',
    '28g': 'Adriatic Sea',
    '28h': 'Aegean Sea',
    '29': 'Sea of Marmara',
    '3': 'Skagerrak',
    '30': 'Black Sea',
    '31': 'Sea of Azov',
    '32': 'South Atlantic',
    '33': 'Rio de La Plata',
    '34': 'Gulf of Guinea',
    '35': 'Gulf of Suez',
    '36': 'Gulf of Aqaba',
    '37': 'Red Sea',
    '38': 'Gulf of Aden',
    '39': 'Arabian Sea',
    '4': 'North Sea',
    '40': 'Gulf of Oman',
    '41': 'Persian Gulf',
    '42': 'Laccadive Sea',
    '43': 'Bay of Bengal',
    '44': 'Andaman or Burma Sea',
    '45': 'Indian Ocean',
    '45A': 'Mozambique Channel',
    '46A': 'Malacca Strait',
    '46B': 'Singapore Strait',
    '47': 'Gulf of Thailand',
    '48a': 'Sulu Sea',
    '48b': 'Celebes Sea',
    '48c': 'Molukka Sea',
    '48d': 'Gulf of Tomini',
    '48e': 'Halmahera Sea',
    '48f': 'Ceram Sea',
    '48g': 'Banda Sea',
    '48h': 'Arafura Sea',
    '48i': 'Timor Sea',
    '48j': 'Flores Sea',
    '48k': 'Gulf of Boni',
    '48l': 'Bali Sea',
    '48m': 'Makassar Strait',
    '48n': 'Java Sea',
    '48o': 'Savu Sea',
    '49': 'South China Sea',
    '5': 'Greenland Sea',
    '50': 'Eastern China Sea',
    '51': 'Yellow Sea',
    '52': 'Japan Sea',
    '53': 'Seto Naikai or Inland Sea',
    '54': 'Sea of Okhotsk',
    '55': 'Bering Sea',
    '56': 'Philippine Sea',
    '57': 'North Pacific',
    '58': 'Gulf of Alaska',
    '59': 'The Coastal Waters of Southeast Alaska and British Columbia',
    '6': 'Norwegian Sea',
    '60': 'Gulf of California',
    '61': 'South Pacific',
    '62': 'Great Australian Bight',
    '62A': 'Bass Strait',
    '63': 'Tasman Sea',
    '64': 'Coral Sea',
    '65': 'Solomon Sea',
    '66': 'Bismarck Sea',
    '67': 'Southern Ocean',
    '7': 'Barentsz Sea',
    '8': 'White Sea',
    '9': 'Kara Sea'}

var province_list = {
      1: 'Andean Plateau',
      2: 'Namaqua-Natal Mobile Belt',
      3: 'Mahanadi Rift',
      4: 'Yenisei Fold Belt',
      5: 'Rio Grande Rift',
      6: 'Dabie Orogen',
      7: 'Dinarides',
      8: 'Ross Peninsula',
      9: 'Llanos Basin',
      10: 'Southern Central Alaskan Terrane',
      11: 'Columbia Plateau',
      12: 'Pinjarra Orogen',
      13: 'Marie Byrd Land',
      14: 'Lambert Rift',
      15: 'Cantabrian-Pyrenean Belt',
      16: 'Amudsen Fold System',
      17: 'West Austerian Leonese Zone',
      18: 'Dneipr-Donets Basin',
      19: 'Hudson Bay Terrane',
      20: 'Godavari Rift',
      21: 'Pine Creek Inlier',
      22: 'North Caribou Terrane',
      23: 'Bengal Fan',
      24: 'Sinai Shield',
      25: 'West Antarctic Rift',
      26: 'Western Wabigoon Terrane',
      27: 'Red Sea Rift',
      28: 'Georgina Basin',
      29: 'Yilgarn Craton',
      30: 'Bothnia microcontinent',
      31: 'Chaco Basin',
      32: 'New Caledonian Trough',
      33: 'Alaskan Accretionary Complex',
      34: 'Alaskan North Slope',
      35: 'Makran Accretionary Complex',
      36: 'Anti-Atlas Mountains',
      37: 'Aegean Volcanic Arc',
      38: 'Kopeh Dag',
      39: 'Lord Howe Basin',
      40: 'Torlesse Terrane',
      41: 'Wanni Complex',
      42: 'Banda Volcanic Arc',
      43: 'Alborz Mountains',
      44: 'Uganda Craton',
      45: 'Java Volcanic Arc',
      46: 'Zagros Orogen',
      47: 'Bureja-Jziamusy Terrane',
      48: 'Deccan Traps',
      49: 'Charleston-Carolina Terranes',
      50: 'Sea of Japan',
      51: 'Svalbard Caldeonides',
      52: 'Rockelides',
      53: 'Okinawa Trough',
      54: 'North-central Mobile Belt',
      55: 'East Congo Mobile Belt',
      56: 'Anabar Shield',
      57: 'Palmyra Fold Belt',
      58: 'East Hearne',
      59: 'East Rae',
      60: 'Karakoram Province',
      61: 'Gulf of California Coast',
      62: 'Qiangtang Terrane',
      63: 'Idaho Batholith',
      64: 'Innuitian Orogen',
      65: 'Antenanarivo Block',
      66: 'Intermontane Belt',
      67: 'Al Kufrah Craton',
      68: 'La Range Arc',
      69: 'Murzuq Craton',
      70: 'Himalayan Orogen',
      71: 'Mayan Highlands',
      72: 'Medicine Hat Terrane',
      73: 'Sibumasu Terrane',
      74: 'Seychelle Remnant',
      75: 'Yidun Arc',
      76: 'Middle Rocky Mountains',
      77: 'Mosquito Coast Lowlands',
      78: 'Nagssugtoqidian Mobile Belt',
      79: 'Nain Province',
      80: 'North Atlantic Craton',
      81: 'Northern Japan Accretionary Prism',
      82: 'Omineca Belt/Shushwap Complex',
      83: 'Pacific Coast Ranges',
      84: 'Qilian Shan',
      85: 'Penokean Orogen',
      86: 'Rae Province',
      87: 'Rimbey-Talston-Thelon Arc',
      88: 'Tarim Basin',
      89: 'Fly Platform',
      90: 'Papuan Fold and Trust Belt',
      91: 'Longgang Block',
      92: 'Slave Craton',
      93: 'Southern Rocky Mountains',
      94: 'Luzon Volcanic Arc',
      95: 'Trans-Hudson Orogen',
      96: 'Sulu Volcanic Arc',
      97: 'Unknown Precambrian Province',
      98: 'Wopmay Orogen',
      99: 'Wyoming Craton',
      100: 'Yucatan Peninsula',
      101: 'Greater Antilles',
      102: 'Jiangnan Orogen',
      104: 'East Cathaysia',
      105: 'Southern Caspian Basin',
      106: 'West Cathaysia',
      107: 'Sichuan Basin',
      110: 'Balkhash-Yili Fold Belt',
      111: 'Stepnyak-Northern Tien Shan',
      112: 'Chu-Yili Microcontinent',
      113: 'Chatkal-Valerianov Arc',
      114: 'Tourgai-Karatau Basin',
      115: 'Tian Shan Fold Belt',
      117: 'Afghan Tajik Block',
      118: 'Aktau Microcontinent',
      119: 'Sulawesi Volcanic Arc',
      120: 'Karakum Craton',
      121: 'Zharma-Saur Fold Belt',
      122: 'Caucas Mountains',
      123: 'Novosibirsk-Chukhi Fold Belt',
      126: 'Sulawesi Ophiolite complex',
      128: 'Palau Arc',
      129: 'Kyushu Ridge',
      130: 'West Mariana Ridge',
      131: 'Yap Arc',
      132: 'Kermadec Arc',
      133: 'Tonga Arc',
      134: 'Colville Ridge',
      135: 'Colville Ridge',
      136: 'Kermadec Arc',
      137: 'San Christobal Arc',
      138: 'New Hebrides Arc',
      139: 'Bayangol Island Arc',
      140: 'Gurvansayhan volcanic arc',
      141: 'Dzhida Arc',
      142: 'Salair Arc',
      143: 'Papuan Arc',
      144: 'Tarvagatay Igneous Belt',
      145: 'Mamberamo Thrust Belt',
      146: 'North Tian Shan',
      147: 'Zavhan Basin',
      148: 'Haraa Basin',
      149: 'Yeongnam Massif',
      150: 'Angara-Vitim Batholith',
      151: 'Arkalyk fold and thrust belt',
      152: 'Hamardavaa Metamorphic Belt',
      153: 'Sangelin Metamorphic Belt',
      154: 'Tasgaanolom Basin',
      155: 'Hovsgul Basin',
      156: 'Zag Passive Margin',
      157: 'Rudny Altai Terrane',
      158: 'Baydrag Craton',
      159: 'Bantam Arc',
      160: 'Bismarck Volcanic Arc',
      161: 'Western Sumatra',
      162: 'Song Da Terrane',
      163: 'Truongson Terrane',
      164: 'Loei-Petchabun Foldbelt',
      166: 'Sukhothai Block',
      167: 'Indochina Terrane',
      168: 'Sabah Zone',
      169: 'Lancangjiang Belt',
      170: 'Sibu Zone',
      171: 'Kuching Zone',
      172: 'Miri Zone',
      173: 'Gorny Altai',
      174: 'Henegshan-Baolidao Accretionary Complex',
      175: 'Junggar Basin',
      176: 'Erdaojing subduction complex',
      177: 'South Tian Shan',
      178: 'Lake Zone',
      179: 'Altai-Mongolia Terrane',
      180: 'Unknown',
      181: 'West Sayan Terrane',
      182: 'Zavhan Craton',
      183: 'Hangay-Hentey Basin',
      184: 'Lao Basin',
      185: 'Havre Trough',
      186: 'Mariana Trough',
      187: 'Woodlark Basin',
      188: 'Triobrand Arc',
      189: 'Kuznetsk Basin',
      190: 'Gobi-Altai Zone'}

$.fn.dataTable.render.author = function ( num ) {
  return function ( data, type, row ) {
      if (type === 'display' && data) {
        return data.split(',').length > 2 ?
        data.split(',')[0] + ' et al.' :
        data;
      }
      return ""
  }
};

$.fn.dataTable.render.iconize_href = function ( icon, href) {
  return function ( data, type, row ) {
      return type === "display" && data && href ?
        '<a href='+href+data+'><i class="'+icon+'"></i></a>' :
        ""
  }
};

$.fn.dataTable.render.from_list = function (list) {
  return function ( data, type, row ) {
      return data ?
        list[data] : null
  }
};


$.fn.dataTable.render.apa = function ( href ) {
  return function ( data, type, row ) {
      return Cite(data).format('bibliography', {format: 'html', template: 'apa' })
    };
  };

$.fn.dataTable.render.href = function ( href ) {
  return function ( slug, type, row ) {
      return '<a href='+href+slug+'>'+data+'<i class="fas fa-lg fa-globe"></i></a>'
  }
};

var customColumns = {
  slug: { data: 'slug', 
    render: $.fn.dataTable.render.iconize_href("fas fa-lg fa-binoculars","/thermoglobe/publications/"),
    defaultContent:''},
  site_slug: { 
    render: $.fn.dataTable.render.iconize_href("fas fa-lg fa-binoculars","/thermoglobe/sites/"),
    defaultContent:''},
  doi: { data: 'doi', 
    render: $.fn.dataTable.render.iconize_href("fas fa-lg fa-globe","http://www.doi.org/"), 
    defaultContent:''},
  author: {data:'author',
    render: $.fn.dataTable.render.author(1),
    defaultContent:''},
  reference: { data: 'bibtex', 
    render: $.fn.dataTable.render.apa(), 
    defaultContent:''},
  country: {
    title:'Country',
    render: $.fn.dataTable.render.from_list(country_list), 
    defaultContent:''},
  sea: {
    title:'Sea/Ocean',
    render: $.fn.dataTable.render.from_list(seas_list), 
    defaultContent:''},
  province: {
    title:'Geological Province',
    render: $.fn.dataTable.render.from_list(province_list), 
    defaultContent:''},
}


function table_from_objects(id, headers, table, options, preDefined) {
  preDefined = {...customColumns,...preDefined};
  let columns = []
  headers.forEach(function(el){
    //either gets the options from preDefined or append the standard options
    columns.push(preDefined[el.toLowerCase()] || {title: el, defaultContent: ""})
    })

  let dataTable = $('#'+id).DataTable( {
      columns:columns,
      data:table,
      ...options,
      });

  return dataTable
}

function table_from_values(table) {
  let options = table.options;
  
  let columns = []
  table.columns.forEach(function(el){
    //either gets the options from preDefined or append the standard options
    columns.push(customColumns[el.toLowerCase()] || {title: el, defaultContent: ""})
    })

  let dataTable = $(table.id).DataTable( {
      columns:columns,
      ...table.options,
      });

  return dataTable
}

function create_table(id, table, options, preDefined) {
    preDefined = {...customColumns,...preDefined};
    var columns = []
    table.columns.forEach(function(el){
        //either gets the options from preDefined or append the standard options
        columns.push(preDefined[el] || {title: el, defaultContent: ""})
        })
    
    
    var dataTable = $("#"+id).DataTable({
      columns:columns,
      ...options,
    })

    dataTable.rows.add(table.data)
    dataTable.draw()


    return dataTable
}



function empty_table(id, options, columns) {
  
  var dataTable = $("#"+id).DataTable({
    columns:columns,
    ...options,
  })

  return dataTable
}

function table_from_bibtex(table, options, preDefined){
    preDefined = {...customColumns,...preDefined};

    var columns = []
    table.columns.forEach(function(el){
      //either gets the options from preDefined or append the standard options
      columns.push(preDefined[el] || {data: el, defaultContent: "", searchable:false})
      })
    columns.push({data: 'bibtex', defaultContent: "", visible: false})

    var dataTable = $("#"+table.id).DataTable({
        columns: columns,
        ajax: {
          url: $(location).attr('href'),
          dataSrc: get_bibtex_from_ajax,
        },
        ...options,
        })

    return table
  }

function get_bibtex_from_ajax(data) {
  var rows = []
  $(data.data).each(function (ind, row) {
    try {rows.push({
        slug: row.slug,
        bibtex: row.bibtex,
        ...flattenObj(Cite(row.bibtex).format('bibtex',{format: 'object'})),
      })}
    catch(err) { console.log(err) }
  })
  return rows
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








