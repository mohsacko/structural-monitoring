if (window.TiltDashboard) {
    console.warn('TiltDashboard has already been initialized. Skipping re-initialization.');
} else {
    const TiltDashboard = (function() {
        let sensorsData;  // Encapsulated within the TiltDashboard object
        let color;
        let path;

        function updateDialWithClickedValue(sensorId, value) {
            console.log(`Entered updateDialWithClickedValue method!`)
            const dialWidth = 300;
            const dialHeight = 300;
            const dialRadius = 100;
            const dialCenter = [dialWidth / 2, dialHeight / 2];
        
            // Select the SVG within the div with the unique ID
            const svg = d3.select(`#dial-${sensorId}`).select("svg");

            // Remove any existing red needles
            svg.selectAll("line[stroke='red']").remove();
        
            // Draw the additional needle
            const needleLength = dialRadius - 10;
            const needle = svg.append("line")
                .attr("x1", dialCenter[0])
                .attr("y1", dialCenter[1])
                .attr("x2", dialCenter[0])
                .attr("y2", dialCenter[1] - needleLength)
                .attr("stroke", "red")  // Different color to distinguish from the main needle
                .attr("stroke-width", 2);
        
            // Calculate the rotation angle for a full circle
            const fullCircleRotationAngle = value * 36 * (5/6); 
            needle.attr("transform", `rotate(${fullCircleRotationAngle}, ${dialCenter[0]}, ${dialCenter[1]})`);
        }        

        function renderTiltChart(tiltData) {
            console.log(`Render Tilt Chart!`)
            // Constants for dimensions
            const width = 928;
            const height = 500;
            const marginTop = 50;
            const marginRight = 50;
            const marginBottom = 50;
            const marginLeft = 60;

            // Scales
            const x = d3.scaleTime()
                .domain(d3.extent(tiltData, d => d.date))
                .range([marginLeft, width - marginRight]);

            const y = d3.scaleLinear()
                .domain([d3.min(tiltData, d => d.value), d3.max(tiltData, d => d.value)])
                .range([height - marginBottom, marginTop]);

            // SVG canvas
            const svg = d3.select("#tilt-graph") 
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            // 1. X-Axis Label (Local Timezone)
            const timezoneOffset = new Date().getTimezoneOffset();
            const timezoneLabel = `Time (UTC${timezoneOffset > 0 ? '-' : '+'}${Math.abs(timezoneOffset / 60).toString().padStart(2, '0')}:00)`;
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height)
                .attr("text-anchor", "middle")
                .text(timezoneLabel);

            // 2. Y-Axis Label (Degrees of Tilt)
            svg.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0)
                .attr("x", -(height / 2))
                .attr("dy", "1em")
                .attr("text-anchor", "middle")
                .text("Degrees of Tilt");

            // 3. Chart Title (Live Tilt Data)
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", marginTop - 20)
                .attr("text-anchor", "middle")
                .attr("font-weight", "bold")
                .attr("font-size", "24px")  // Increase font size
                .text("Live Tilt Data");
                

            // Add invisible layer for the interactive tip
            const dot = svg.append("g")
                .attr("display", "none")
                .raise();  // Bring the dot group to the front

            dot.append("circle")
                .attr("r", 10)
                .attr("opacity", 0);

            dot.append("circle")
                .attr("class", "visible-dot")
                .attr("r", 2.5);  // Smaller radius
            

            dot.append("text")
                .attr("text-anchor", "middle")
                .attr("y", -8);

            // Add click event listener to the dot group
            /*
            dot.select("circle:not(.visible-dot)")  // This selects the larger invisible circle
                .on("click", function() {
                    console.log('Creating an event listener for the dot group!');
                    // Extract sensor name and value from the displayed tip
                    
                    const textContent = dot.select("text").text();
                    const sensorNameMatch = textContent.match(/^([A-Z]\d+):/);
                    const valueMatch = textContent.match(/: ([\d.]+) \(/);

                    if (sensorNameMatch && valueMatch) {
                        const sensorName = sensorNameMatch[1];
                        // Extract the idx from the sensorName
                        const idx = parseInt(sensorName.match(/\d+/)[0]);
                        const value = parseFloat(valueMatch[1]);
                        updateDialWithClickedValue(idx, value);
                    }
                });
            */    
            svg
                .on("pointerenter", pointerentered)
                .on("pointermove", pointermoved)
                .on("pointerleave", pointerleft)
                .on("touchstart", event => event.preventDefault());

            // Axes
            svg.append("g")
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(d3.axisBottom(x));

            svg.append("g")
                .attr("transform", `translate(${marginLeft},0)`)
                .call(d3.axisLeft(y));

            // Group the data by sensor
            sensorsData = d3.groups(tiltData, d => d.sensor);

            // Color scale for different sensors
            color = d3.scaleOrdinal()
                .domain(sensorsData.map(d => d[0]))
                .range(d3.schemeCategory10);  // This is a predefined set of 10 categorical colors in D3

            // Line generator
            const line = d3.line()
                .x(d => x(d.date))
                .y(d => y(d.value));

            // Draw the lines
            path = svg.append("g")
                .attr("fill", "none")
                .attr("stroke-width", 1.5)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
            .selectAll("path")
            .data(sensorsData)
            .join("path")
                .style("mix-blend-mode", "multiply")
                .attr("stroke", d => color(d[0]))
                .attr("d", d => line(d[1]));

            // Define the time format function
            const formatDate = d3.timeFormat("%b %d, %Y %I:%M %p");

            function pointermoved(event) {
                const [xm, ym] = d3.pointer(event);
                const i = d3.leastIndex(tiltData, d => Math.hypot(x(d.date) - xm, y(d.value) - ym));
                const point = tiltData[i];

                // Check if the line corresponding to the point is inactive
                const isLineInactive = path.filter(d => d[0] === point.sensor).classed("inactive");
                if (isLineInactive) {
                    return;  // Exit the function if the line is inactive
                }
                
                // Get the first letter of the sensor name
                const firstLetter = point.sensor.charAt(0);
                // Extract the numeric part of the sensor name
                const numericPart = point.sensor.match(/\d+/);
                // Combine the first letter and the numeric part
                const abbreviatedSensor = firstLetter + numericPart;
                
                path.style("stroke", d => d[0] === point.sensor ? null : "#ddd").filter(d => d[0] === point.sensor).raise();
                dot.attr("transform", `translate(${x(point.date)},${y(point.value)})`);
                
                // Determine the position of the text based on the x-coordinate of the point
                if (x(point.date) < width / 2) {
                    dot.select("text")
                        .attr("text-anchor", "start")  // Align to the start (right side of the point)
                        .attr("dx", "10px");  // Small offset to separate the text from the point
                } else {
                    dot.select("text")
                        .attr("text-anchor", "end")  // Align to the end (left side of the point)
                        .attr("dx", "-10px");  // Small offset to separate the text from the point
                }
                
                dot.select("text").text(`${abbreviatedSensor}: ${point.value.toFixed(2)} (${formatDate(point.date)})`);
            }    
                
            function pointerentered() {
                path.each(function(d) {
                    if (!d3.select(this).classed("inactive")) {
                        d3.select(this).style("mix-blend-mode", null).style("stroke", "#ddd");
                    }
                });
                dot.attr("display", null);
            }
            
            function pointerleft() {
                path.each(function(d) {
                    if (!d3.select(this).classed("inactive")) {
                        d3.select(this).style("mix-blend-mode", "multiply").style("stroke", null);
                    }
                });
                dot.attr("display", "none");
            }            
        }

        function renderTiltLegend() {
            const legendDiv = document.getElementById("tilt-legend");
            sensorsData.forEach(sensor => {
                const sensorName = sensor[0];
                const legendItem = document.createElement("span");
                legendItem.className = "me-3";
                legendItem.style.color = color(sensorName);
                legendItem.style.cursor = "pointer";
                legendItem.textContent = sensorName;
                legendItem.dataset.sensorName = sensorName;
                legendDiv.appendChild(legendItem);

                // Move the event listener inside the loop
                legendItem.addEventListener("click", function() {
                    const sensorName = this.dataset.sensorName;
                    const line = path.filter(d => d[0] === sensorName);
                    if (line.classed("inactive")) {  // Check if the line has the "inactive" class
                        line.classed("inactive", false);  // Remove the "inactive" class
                        this.style.opacity = 1;
                    } else {
                        line.classed("inactive", true);  // Add the "inactive" class
                        this.style.opacity = 0.5;
                    }
                });                
            });
        }

        function renderDials(tiltData) {
            const dialsDiv = document.getElementById("dials");
            
            // Group the data by sensor
            sensorsData = d3.groups(tiltData, d => d.sensor);

            // Define dimensions for each dial
            const dialWidth = 300;
            const dialHeight = 300;
            const dialRadius = 100;
            const dialCenter = [dialWidth / 2, dialHeight / 2];

            sensorsData.forEach((sensorData, idx) => {
                const sensorName = sensorData[0];
                const data = sensorData[1];
                const mostRecentData = data.sort((a, b) => b.date - a.date)[0];
                const currentValue = mostRecentData ? mostRecentData.value : null;

                const dialContainer = document.createElement("div");
                dialContainer.id = `dial-${idx}`;
                dialContainer.style.width = `${dialWidth}px`;
                dialContainer.style.height = `${dialHeight}px`;
                dialContainer.style.display = "inline-block";
                dialsDiv.appendChild(dialContainer);

                const svg = d3.select(`#dial-${idx}`)
                    .append("svg")
                    .attr("width", dialWidth)
                    .attr("height", dialHeight);

                // Draw the horseshoe shape
                const arc = d3.arc()
                    .innerRadius(dialRadius - 10)
                    .outerRadius(dialRadius)
                    .startAngle(-Math.PI / 6 * 5)  // Start from -5
                    .endAngle(Math.PI / 6 * 5);    // End at 5

                svg.append("path")
                    .attr("d", arc())
                    .attr("fill", "none")
                    .attr("stroke", "black")
                    .attr("transform", `translate(${dialCenter[0]}, ${dialCenter[1]})`);                

                // Highlight the critical sections
                const criticalSections = [[-5, -3], [3, 5]];
                criticalSections.forEach(section => {
                    const startAngle = section[0] * (Math.PI / 6);
                    const endAngle = section[1] * (Math.PI / 6);

                    const criticalArc = d3.arc()
                        .innerRadius(dialRadius - 10)
                        .outerRadius(dialRadius)
                        .startAngle(startAngle)
                        .endAngle(endAngle);

                    svg.append("path")
                        .attr("d", criticalArc())
                        .attr("fill", "red")
                        .attr("transform", `translate(${dialCenter[0]}, ${dialCenter[1]})`);
                });

                // 1. Determine the Historical Range
                const minValue = d3.min(data, d => d.value) - 0.025;
                const maxValue = d3.max(data, d => d.value) + 0.025;

                // 2. Draw the Shaded Region
                const historicalArc = d3.arc()
                    .innerRadius(dialRadius - 10)
                    .outerRadius(dialRadius)
                    .startAngle(minValue * (Math.PI / 6))
                    .endAngle(maxValue * (Math.PI / 6));

                svg.append("path")
                    .attr("d", historicalArc())
                    .attr("fill", "lightgreen")
                    .attr("transform", `translate(${dialCenter[0]}, ${dialCenter[1]})`);


                // Add small lines and labels at 0.25 intervals
                for (let i = -5; i <= 5; i += 0.25) {
                    const angle = i * (Math.PI / 6);
                    const x1 = dialCenter[0] + (dialRadius - 10) * Math.sin(angle);
                    const y1 = dialCenter[1] - (dialRadius - 10) * Math.cos(angle);
                    const x2 = dialCenter[0] + dialRadius * Math.sin(angle);
                    const y2 = dialCenter[1] - dialRadius * Math.cos(angle);

                    svg.append("line")
                        .attr("x1", x1)
                        .attr("y1", y1)
                        .attr("x2", x2)
                        .attr("y2", y2)
                        .attr("stroke", "black")
                        .attr("stroke-width", 1);

                    if (i % 0.5 === 0) {
                        const labelX = dialCenter[0] + (dialRadius + 15) * Math.sin(angle);
                        const labelY = dialCenter[1] - (dialRadius + 15) * Math.cos(angle);
                        
                        // Determine the label text based on whether it's a whole number or not
                        const labelText = i % 1 === 0 ? i.toString() : i.toFixed(1);
                        
                        svg.append("text")
                            .attr("x", labelX)
                            .attr("y", labelY)
                            .attr("text-anchor", "middle")
                            .attr("alignment-baseline", "middle")
                            .text(labelText);
                    }
                }

                // Draw the needle
                const needleLength = dialRadius - 10;
                const needle = svg.append("line")
                    .attr("x1", dialCenter[0])
                    .attr("y1", dialCenter[1])
                    .attr("x2", dialCenter[0])
                    .attr("y2", dialCenter[1] - needleLength)
                    .attr("stroke", "black")
                    .attr("stroke-width", 2);

                // Calculate the rotation angle for a full circle
                const fullCircleRotationAngle = currentValue * 36 * (5/6); 
                needle.attr("transform", `rotate(${fullCircleRotationAngle}, ${dialCenter[0]}, ${dialCenter[1]})`);

                // Label the sensor
                svg.append("text")
                    .attr("x", dialCenter[0])
                    .attr("y", dialHeight - 10)
                    .attr("text-anchor", "middle")
                    .attr("alignment-baseline", "middle")
                    .text(sensorName);
            });
        }

        function updateDashboard() {
            if (typeof sensorsData === 'undefined') {
                window.sensorsData = null;  // Declare it on the window object to make it global
            }
            const tiltGraph = document.getElementById("tilt-graph");
            const tiltDataRaw = JSON.parse(tiltGraph.dataset.tiltData);
            console.log(tiltDataRaw);

            // Convert date strings to Date objects and flatten the data
            const tiltData = [].concat(...tiltDataRaw.map((sensorData, idx) => 
                sensorData.map(d => ({
                    date: new Date(d.date),
                    value: d.value,
                    sensor: `Sensor ${idx + 1}`,
                    sensor_id: d.sensor_id
                }))
            ));
            renderTiltChart(tiltData);
            renderTiltLegend();
            renderDials(tiltData);

        }

        return {
            updateDashboard: updateDashboard
        };

    })();

    // Call the updateDashboard function
    TiltDashboard.updateDashboard();

    // Expose the updateDashboard function to the global scope
    window.updateDashboard = TiltDashboard.updateDashboard;
}