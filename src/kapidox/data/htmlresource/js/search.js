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

function do_search(json_path, query)
{
    var results = []
    $.ajax({
        url: json_path,
        dataType: 'json',
        error: function(data, status, err) {
            console.log(err)
        },
        success: function(json) {

            $.each(json.docfields, function(key, val) {
                if (!('name' in val) || !('text' in val)) {
                    return // like continue in $.each, don't ask, jQuery...
                }

                if (val.name.search(new RegExp(query, "i")) != -1 || val.text.search(new RegExp(query, "i")) != -1) {
                    results.push(val)
                }
            });
            fill_results(results)
        }
    });
}

function fill_results(results)
{
    $( '#results' ).append("<ul>")
    $.each(results, function(key, result) {
        $( '#results' ).append("\t<li><a href=\"" + result.url + "\">"+ result.name + "</a>: " + result.text + "</li>" + '\n')
    });
    $( '#results' ).append("</ul>\n")

}

function render_search()
{
    var query = GetURLParameter("query")
    $( "#search-input" ).val(query)
    $( "#search-title" ).append(" \"<i>" + query + "</i>\"")
    var json_path =  "searchdata.json"
    do_search(json_path, query)
}
