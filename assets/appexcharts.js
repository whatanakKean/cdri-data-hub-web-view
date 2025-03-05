window.dash_clientside = Object.assign({}, window.dash_clientside, {
    apexCharts: {
        lineChart: function (inputData) {
            console.log(inputData);
            
            // Clear the chart before redrawing
            document.getElementById("apexLineChart").innerHTML = "";
            
            // Group data by year
            let groupedData = {};
            inputData.forEach(item => {
                let year = item.Year;
                if (!groupedData[year]) {
                    groupedData[year] = {};
                }
                groupedData[year][item.Indicator] = item["Indicator Value"];
            });
            
            // Extract unique indicators
            let indicators = [...new Set(inputData.map(item => item.Indicator))];
            
            // Format data for ApexCharts
            let seriesData = indicators.map(indicator => {
                return {
                    name: indicator,
                    type: 'line',
                    data: Object.keys(groupedData).map(year => groupedData[year][indicator] || 0) // Ensure no undefined values
                };
            });
            
            let years = Object.keys(groupedData).map(year => parseInt(year));
            
            var options = {
                series: seriesData,
                labels: years,
                xaxis: { type: 'category', categories: years },
                yaxis: {
                    labels: { formatter: (val) => val.toLocaleString() },
                    title: { text: "Rice Production Indicators" },
                },
                chart: { height: '85%' },
                stroke: { width: 2, curve: 'smooth' },
                title: {
                    text: "Rice Production Trends",
                    align: 'left',
                    style: {
                        fontSize: '22px',
                        fontWeight: 'bold',
                    },
                },
                subtitle: {
                    text: "A comprehensive view of rice production indicators over the years",
                    align: 'left',
                    style: {
                        fontSize: '16px',
                        fontWeight: 'normal',
                    },
                },
                dataLabels: { enabled: true },
                tooltip: {
                    shared: true,
                    intersect: false,
                    y: {
                        formatter: function (val) {
                            return val === undefined || val === null ? 'N/A' : val.toLocaleString();
                        }
                    }
                },
            };
            
            // Initialize and render the chart
            var chart = new ApexCharts(document.getElementById('apexLineChart'), options);
            chart.render();
            
            return window.dash_clientside.no_update;
        },
    },
});
