function drawGraphForActivity(uri, id) {
    $("#graph").empty();
    $("#loading").show();
    
    $.get('/graph', {'type': 'activities', 'uri': uri, 'id': id }, function(data) {
                $("#loading").hide();
                if (data.graph.links.length > 0) {
                        // drawActivityGraph(data.graph);
                        drawSankeyDiagram(data.graph);
                } else {
                        $("#noresponse").show();        
                }
    });
}


function drawActivityGraph(graph) {
  var width = 900,
      height = 900;
  
  var color = d3.scale.category20();
  
  var force = d3.layout.force()
      .charge(-220)
      .linkDistance(60)
      .size([width, height]);
  
  var svg = d3.select("#graph").append("svg")
      .attr("width", width)
      .attr("height", height);


  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

  var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return 3;}); //Math.sqrt(d.value); });

  var node = svg.selectAll("circle.node")
      .data(graph.nodes)
    .enter().append("circle")
      .attr("class", "node")
      .attr("r", function(d) { return d.degree + 20;})
      .style("fill", function(d) { return color(d.type); })
      .on("click", function(d) { click(d); })
      .call(force.drag);

      
  node.append("title")
      .text(function(d) { return d.label; });

  var texts = svg.selectAll("text.label")
                .data(graph.nodes)
                .enter().append("text")
                .attr("class", "label")
                .attr("fill", "black")
                .style("text-anchor", "middle")
                .attr("dy", ".3em")
                .attr("class", function(d) { return d.type;})
                .text(function(d) {  if (d.type != 'criterion') { return d.label; } else { return ''; }  });
  
      

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
        
    texts.attr("transform", function(d) {
        return "translate(" + d.x + "," + d.y + ")";
    });
  });
  
  function click(n) {
        if (n.type == 'trial') {
            drawGraphForTrial(n.uri, n.label);
        }
        if (n.type == 'concept') {
            drawChordForConcept(n.uri);
        }
        
  }
}


function drawSankeyDiagram(graph) {
var margin = {top: 1, right: 1, bottom: 6, left: 1},
    width = 900 - margin.left - margin.right,
    height = 1500 - margin.top - margin.bottom;

var formatNumber = d3.format(",.0f"),
    format = function(d) { return formatNumber(d) + " TWh"; },
    color = d3.scale.category20();

var svg = d3.select("#graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var sankey = d3.sankey()
    .nodeWidth(15)
    .nodePadding(10)
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

  //node.append("text")
  //    .attr("x", -6)
  //    .attr("y", function(d) { return d.dy / 2; })
  //    .attr("dy", ".35em")
  //    .attr("text-anchor", "end")
  //    .attr("transform", null)
  //    .text(function(d) { return d.label; })
  //  .filter(function(d) { return d.x < width / 2; })
  //    .attr("x", 6 + sankey.nodeWidth())
  //    .attr("text-anchor", "start");

  function dragmove(d) {
    d3.select(this).attr("transform", "translate(" + d.x + "," + (d.y = Math.max(0, Math.min(height - d.dy, d3.event.y))) + ")");
    sankey.relayout();
    link.attr("d", path);
  }

}