function GetURLParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);

    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }
}

function do_search(json_path, query, type)
{
    var results = []
    $.ajax({
        url: json_path,
        dataType: 'json',
        error: function(data, status, err) {
            console.log(err)
        },
        success: function (json) {
            search_json(type, json, query)
        }
    });
}

function search_json(type, json, query)
{
    result_html = ""
    if (type == 'library') {
        results_html = search_json_library(json, query)
    } else if (type == 'group') {
        results_html = search_json_group(json, query)
    } else if (type == 'global') {
        results_html = search_json_global(json, query)
    }
    $( '#results' ).append(results_html)
}

function search_json_library(json, query)
{
    var results = []
    $.each(json.docfields, function(key, val) {
        if (!('name' in val) || !('text' in val)) {
            return // acts like continue in $.each, don't ask, it's jQuery...
        }

        if (val.name.search(new RegExp(query, "i")) != -1 || val.text.search(new RegExp(query, "i")) != -1) {
            results.push(val)
        }
    });

    var html_results = "<ul>\n"
    $.each(results, function(key, result) {
        html_results += "\t<li><a href=\"" + result.url + "\">"+ result.name + "</a>: " + result.text + "</li>" + '\n'
    });
    html_results += "</ul>\n"

    return html_results
}


function render_search(type)
{
    var query = GetURLParameter("query");
    $( "#search-input" ).val(query);
    $( "#search-title" ).append(" <i>" + query + "</i>");
    var json_path =  "searchdata.json";
    do_search(json_path, query, type);
}
