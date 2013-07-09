function drawDiagramForActivity(uri, id, graph_uri) {
    $("#graph").empty();
    $("#loading").show();
    
    
    $.get('/diagram', {'type': 'activities', 'uri': uri, 'id': id, 'graph_uri': graph_uri}, function(data) {
                $("#loading").hide();
                if (data.graph.links.length > 0) {
                        drawSankeyDiagram(data.graph, data.start_nodes, data.types);
                } else {
                        $("#noresponse").show();        
                }
    });
}




function drawSankeyDiagram(graph, start_nodes, types) {
var margin = {top: 1, right: 1, bottom: 6, left: 1},
    width = 2000 - margin.left - margin.right;
    
    if ((500/start_nodes) > 40) {
        var height = 40*start_nodes - margin.top - margin.bottom;
    } else {
        var height = 500 - margin.top - margin.bottom;
    }
    

var formatNumber = d3.format(",.0f"),
    format = function(d) { return formatNumber(d) + " TWh"; },
    
    color = d3.scale.ordinal()
    //        .domain(["foo", "bar", "baz"])
            .range(colorbrewer.Paired[types]);
    
    //color = d3.scale.category20();

var svg = d3.select("#graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var sankey = d3.sankey()
    .nodeWidth(15)
    .nodePadding(20)
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
      .style("stroke-width", function(d) { return Math.max(1, d.dy); })
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
      .style("stroke", function(d) { return d3.rgb(d.color).darker(2); })
    .append("title")
      .text(function(d) { return d.label + "\n" + format(d.type); });

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