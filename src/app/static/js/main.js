var graphs_url;
var endpoint_url;
var data_url;

var socket = io.connect('http://' + document.domain + ':' + location.port + '/log');



function initialize(g_url, e_url, d_url) {
	
    graphs_url = g_url;
    endpoint_url = e_url;
    data_url = d_url;
    
    
	
	socket.on('message', function(msg) {
        $('#log').html(msg.data);
		console.log(msg);
    });
	
	socket.on('disconnect', function(msg){
		$('#log').html("Disconnected, server busy?");
		console.log("Disconnected");
	});
	
	
	/*
	// We need to make sure that the dropdowns don't close on data entry!
	*/
    $("#provenance-data").click(function(e) {
       e.stopPropagation();
    });
    $("#provenance-endpoint").click(function(e) {
       e.stopPropagation();
    });
    $("#ignore-named-graphs").click(function(e) {
       e.stopPropagation();
    });
    
    $("#format-radio-turtle").click(function(e) {
       e.stopPropagation(); 
    });
	
    $("#format-radio-rdfxml").click(function(e) {
       e.stopPropagation(); 
    });
    
	$("#title").fitText();
    $("#title").show();
    
	// Hide the named graphs dropdown menu as long as it's empty.
	$("#named-graphs-dropdown").hide();
	
	
	$("#source").hide();
    $("#loading").hide();
	$("#noselection").hide();
    $("#noresponse").hide();
	$("#selectgraph").hide();
    $("#explore-row").hide();
    $("#activities-row").hide();
	$("#serviceactivities").hide();	
	$("#serviceactivities").empty();
    
    $('#api-button').on('click',function(){
       $('#about').toggleClass('hidden'); 
    });
    
    $('#submit-provenance-endpoint').on('click',function(){
        $('#log').html("Connecting to endpoint...");
		var value = $('#provenance-endpoint').val();		
        if (value == ''){
			value = $('#provenance-endpoint').attr('placeholder');
		}
		
    	graphs_client(value);
    });

	$('#submit-provenance-data').on('click', function(){
        $('#log').html("Sending provenance data");
        
        var data = $('#provenance-data').val();
        var format = $('input[name=format-radios]:checked' ).val();
        
		data_client(data, format);
	});
	
	$('#source').on('click', function(){
		showSource();
	})
}

function showSource() {
	var path = $('#serviceactivities').html();
	path = path.replace(/ &amp;gt; /g,".");
	//console.log(path);
	$('#sourcetext').text(path);
}

function graphs_client(endpoint_uri) {
	//$('.dropdown.keep-open').trigger('hide.bs.dropdown');
	
	loading();
    $("#named-graphs-menu").empty();
    $("#named-graphs-dropdown").hide();
    	
    $.localStorage('endpoint_uri',endpoint_uri);
	
	if ($("#ignore-named-graphs").is(':checked')) {
		console.log("Ignoring named graphs");
		
		endpoint_client('http://example.com/none',endpoint_uri);
	} else {
        $.getJSON(graphs_url, {endpoint_uri: endpoint_uri }).done(function(data){
            $('#named-graphs-menu').empty();
            $.each(data.graphs, function(k,v){
                var li = $('<li></li>');
                var a = $('<a></a>');
            
                a.attr('id',v.id);
            
                a.on('click',function(e){
                    $('#log').html("Connecting to endpoint...");
        		    var graph_uri = e.target.id;
        		    $.localStorage('graph_uri',graph_uri);
        		    var endpoint_uri = $.localStorage('endpoint_uri');
                    
                    loading();
                    
        		    endpoint_client(graph_uri, endpoint_uri);
                });
            
                a.append(v.text);
                li.append(a);
            
            
                $('#named-graphs-menu').append(li);
				$("#named-graphs-dropdown").show();
            })
            $("#loading").hide();
        });
	}
    
    
}

function loading(){
	$("#splash-container").hide();
	$("#loading").show();
    $("#source").hide();
    $("#noresponse").hide();
    $("#noselection").hide();
	$("#selectgraph").hide();
    $("#explore-row").hide();
    $("#activities-row").hide();
	$("#serviceactivities").hide();	
	$("#serviceactivities").empty();
}

function endpoint_client(graph_uri, endpoint_uri){
	loading();
	
    $.get(endpoint_url, {graph_uri: graph_uri, endpoint_uri: endpoint_uri }).done(function(data){
		$("#serviceactivities").empty();
		$("#serviceactivities").html(data);
		$("#loading").hide();
		$("#selectgraph").hide();
		$("#source").show();
		$("#activities-row").show();
		$("#serviceactivities").show();	    
    });
}

function data_client(data, format) {
    
    
	loading();
    $("#named-graphs-menu").empty();
    $("#named-graphs-dropdown").hide();


    // var hash=CryptoJS.SHA1(data);
    // 
    // var graph_uri = "http://prov.data2semantics.org/resource/"+hash;
    // 
    // console.log(graph_uri);
	
	var post_data = { data: data, format: format };
	
	$.post(data_url, post_data, function(data){
		$("#serviceactivities").empty();
		$("#serviceactivities").html(data);
		$("#loading").hide();
		$("#source").show();
		$("#activities-row").show();
		$("#serviceactivities").show();	
	})
}

$('#graphs').change(function(e) {

    if (e.val == []) {
        $('#noselection').show()
        return;
    }

    $("#noselection").hide();
    $("#noresponse").hide();
	$("#selectgraph").hide();
	$("#source").hide();
    $("#loading").show();
    $("#activities-row").hide();
	$("#serviceactivities").empty();
	$("#serviceactivities").hide();	


    var graph_uri = e.val;
    $.localStorage('graph_uri',graph_uri);
    var endpoint_uri = $.localStorage('endpoint_uri');

	endpoint_client(graph_uri, endpoint_uri);
});