function drawDiagramForActivity(diagram_service_url, uri, id, graph_uri, endpoint_uri) {
    $("#graph").empty();
    $("#loading").show();


    $.get(diagram_service_url, {'type': 'activities', 'uri': uri, 'id': id, 'graph_uri': graph_uri, 'endpoint_uri': endpoint_uri}, function(data) {
                $("#loading").hide();
                if (data.graph.links.length > 0) {
                        drawSankeyDiagram('#graph', data.graph, data.width, data.types, data.diameter);
                } else {
                        $("#noresponse").show();
                }
    });
}




function drawSankeyDiagram(graph_div, graph, tree_width, types, diameter) {
    var margin = {top: 16, right: 15, bottom: 16, left: 5},
        width = (200 * diameter) - margin.left - margin.right;

		console.log("Tree width = "+tree_width);

		// We will use a minimum height of 150 pixels
        if (tree_width * 30 < 150) {
			console.log("Set height to 150");
            var height = 150;
        } else {
            var height = tree_width * 30;
			console.log("Set height to "+height);
        }

    var color = d3.scale.ordinal()
                .domain(["activity","origin","entity","entity1","entity2","activity1","activity2"])
                .range(["#CED1FB","#FDEAC8","#FFFCE2","#FFFCE2","#FFFCE2","#CED1FB","#CED1FB"]);

    var svg = d3.select(graph_div).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("id","svg")
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
		.attr("class", function(d) { if(d.type == 'origin') {return 'node activity';} else { return 'node '+ d.type; } })
		.attr("id", function(d) {return d.id; })
		.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
        .call(d3.behavior.drag()
        .origin(function(d) { return d; })
        .on("dragstart", function() { this.parentNode.appendChild(this); })
        .on("drag", dragmove))
        .on("click",function(d) { console.log("Clicked"); console.log(d); build_sankey(d.id); })
        .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div .html("<b>" + d.name + "</b>:<br/>" + format(d.value) + "<br/><b>Generated at:</b>" + d.time)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });

    node.append("rect")
        .attr("height", function(d) { return d.dy; })
        .attr("width", sankey.nodeWidth())
        .style("fill", function(d) { return d.color = color(d.type); })
        .style("stroke", function(d) { return d3.rgb(d.color).darker(1); })
        .style("stroke-width", function(d) { if (d.type == 'origin') { return 2;} else { return 1;}})
        .append("title")
        .text(function(d) { return d.label + "\n(" + d.type + ")\n" + d.time ; });

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

    node.append("text")
        .attr("x", -6)
        .attr("y", function(d) { return d.dy / 2 + 12; })
        .attr("dy", ".35em")
        .attr("text-anchor", "end")
        .attr("transform", null)
        .text(function(d) { return "(" + d.type + ")"; })
        .filter(function(d) { return d.x < width / 2; })
        .attr("x", 6 + sankey.nodeWidth())
        .attr("text-anchor", "start")


    function dragmove(d) {
        d3.select(this).attr("transform", "translate(" + d.x + "," + (d.y = Math.max(0, Math.min(height - d.dy, d3.event.y))) + ")");
        sankey.relayout();
        link.attr("d", path);
    }

}
