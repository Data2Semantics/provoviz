function drawDiagramForActivity(diagram_service_url, uri, id, graph_uri, endpoint_uri) {
    $("#graph").empty();
    $("#loading").show();
    
    
    $.get(diagram_service_url, {'type': 'activities', 'uri': uri, 'id': id, 'graph_uri': graph_uri, 'endpoint_uri': endpoint_uri}, function(data) {
                $("#loading").hide();
                if (data.graph.links.length > 0) {
                        drawSankeyDiagram(data.graph, data.width, data.types, data.diameter);
                } else {
                        $("#noresponse").show();        
                }
    });
}




function drawSankeyDiagram(graph, tree_width, types, diameter) {
var margin = {top: 1, right: 1, bottom: 6, left: 1},
    width = (200 * diameter) - margin.left - margin.right;
    
    if ((500/tree_width) > 40) {
        console.log("Over 40");
        var height = 40*tree_width - margin.top - margin.bottom;
        
        if (height < 500 ) {
            height = 300;
        }
    } else {
        console.log("Under 40");
        var height = 500 - margin.top - margin.bottom;
    }
    

var color = d3.scale.ordinal()
            .domain(["activity","origin","entity"])
            .range(["#EB6841","#CC333F","#00A0B0"]) // colourlovers.com "Ocean 5"
    //        .domain(["foo", "bar", "baz"])
    //        .range(colorbrewer.Paired[types]);
    
    //color = d3.scale.category20();

var svg = d3.select("#graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var sankey = d3.sankey()
    .nodeWidth(15)
    .nodePadding(25)
    .size([width, height]);

var path = sankey.link();


  sankey
      .nodes(graph.nodes)
      .links(graph.links)
      .layout(32);

  var link = svg.append("g").selectAll(".link")
      .data(graph.links)
    .enter().append("path")
      .attr("class", "link")
      .attr("d", path)
      .style("stroke-width", function(d) { return Math.max(.3, d.dy); })
      .sort(function(a, b) { return b.dy - a.dy; });

  link.append("title")
      .text(function(d) { return d.source.label + " → " + d.target.label; });

  var node = svg.append("g").selectAll(".node")
      .data(graph.nodes)
    .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
    .call(d3.behavior.drag()
      .origin(function(d) { return d; })
      .on("dragstart", function() { this.parentNode.appendChild(this); })
      .on("drag", dragmove));

  node.append("rect")
      .attr("height", function(d) { return d.dy; })
      .attr("width", sankey.nodeWidth())
      .style("fill", function(d) { return d.color = color(d.type.replace(/ .*/, "")); })
      .style("stroke", function(d) { return d3.rgb(d.color).darker(1); })
    .append("title")
      .text(function(d) { return d.label + "\n(" + d.type + ")"; });

  node.append("text")
      .attr("x", -6)
      .attr("y", function(d) { return d.dy / 2; })
      .attr("dy", ".35em")
      .attr("text-anchor", "end")
      .attr("transform", null)
      .text(function(d) { return d.label; })
    .filter(function(d) { return d.x < width / 2; })
      .attr("x", 6 + sankey.nodeWidth())
      .attr("text-anchor", "start");

  function dragmove(d) {
    d3.select(this).attr("transform", "translate(" + d.x + "," + (d.y = Math.max(0, Math.min(height - d.dy, d3.event.y))) + ")");
    sankey.relayout();
    link.attr("d", path);
  }

}