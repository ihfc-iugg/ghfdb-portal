$(document).ready(function(){
    if($('#refDetailsCard').length){
        create_reference_card(bibtex)
    }
  });

function create_citations(entries){
    // var bib_list = [];
    for (i = 0; i < entries.length; i++) {
        // bib_list.push(entries[i].fields.bibtex)
        create_citation_row(entries[i])
    }

}

function create_citation_row(entry) {

    var cite = create_citation(entry)
    var opt = {
        format: 'string',
        style:'citation-apa',
        type: 'html',
        lang: 'en-US',
    }
    // console.log(cite)

    var row = `<tr><td>${cite.data[0].year}</td><td>${cite.get(opt)}</td></tr>`

    $('#pubTab').append(row)
    // $('#pubTab').append('<div class="hr"></div>')


}

function create_citation(entry){
    var Cite = require('citation-js') 

    var opt = {
        format: 'string',
        style:'citation-apa',
        type: 'html',
        lang: 'en-US',
    }

    var bib = entry.fields.bibtex
    // console.log(bib)
    var cite = new Cite(bib)
    // console.log(id)

    // $('#pubList').append(`<li id="${entry.fields.bib_id}" class="list-group-item"></li>`)

    

    // var id = '#'.concat(entry.fields.bib_id)
    // $(id).html(cite.get(opt))

    return cite

}

function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function create_reference_card(bibtex) {
    var Cite = require('citation-js') 
    var cite = new Cite(bibtex)
    
    console.log(cite)
    data = cite.get()[0]

    if (data == undefined) {

        $('.d-none').toggleClass('.d-none d-block');
        $(".referenceCardTitle").html('Unknown')

        return

    }

    $('.export_bibtex').click(function(){
        download(data.id.concat('.bib'),bibtex);
     });

    $("#tableTitle").append(citep(cite))
    $(".referenceCardTitle").html(data.id)
    add_row('title',data.title)

    array = Object.entries(data)
    for (let index = 0; index < array.length; index++) {
        const element = array[index];

        var key = element[0]
        var value = element[1]
        var skip = ['author','citation-label','id','title','year-suffix']

        if (skip.includes(key)) {
            continue
        }
        if (value instanceof Object) {
            continue
        }

        if (key == 'container-title') {
            var key = 'Journal'
        }

        if (key == 'id') {
            var key = 'ID'
        }

        if (key == 'DOI') {
            $(".referenceDetails").append(`<tr><td>${capitalize(key)}:</td><td><a href='http://www.doi.org/${value}'>${value}</a></td></tr>`)
            continue
        }

        add_row(key,value)

    }
}


function add_row(key,value) {

    $(".referenceDetails").append(`<tr><td>${capitalize(key)}:</td><td>${value}</td></tr>`)

}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function citep(cite) {

    a = cite.format('citation').replace('(','')
    position = -5
    return [a.slice(0, position-2), ' (', a.slice(position)].join('');

}

function get_author_name(bibtex) {
    var Cite = require('citation-js') 
    var cite = new Cite(bibtex.entry)
    console.log(cite)
    $('.card-title').html(cite.data[0].title)


    var intext = cite.format('citation',{
        format:'html',
        template:'apa',
    })

    intext = intext.replace('(','').replace(')','')
}
