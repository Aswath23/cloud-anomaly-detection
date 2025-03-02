document.addEventListener("DOMContentLoaded", function () {
    fetchStatsAndRenderCharts();
});

// ✅ Establish WebSocket Connection
var socket = io.connect('http://' + document.domain + ':' + location.port);

// ✅ Fetch Initial Stats and Render Charts
function fetchStatsAndRenderCharts() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            console.log("📊 Fetched Stats:", data);

            if (!data || Object.keys(data).length === 0) {
                console.error("❌ No data received from /stats");
                return;
            }

            // ✅ Ensure data exists before rendering
            if (data.SVM) renderChart("svmChart", data.SVM, "SVM Model");
            if (data.RandomForest) renderChart("rfChart", data.RandomForest, "Random Forest Model");
            if (data.Autoencoder) renderChart("autoencoderChart", data.Autoencoder, "Autoencoder Model");
            if (data.Accuracy) renderChart("accuracyChart", data.Accuracy, "Model Accuracy");
            if (data.Predictions) renderChart("predictionChart", data.Predictions, "Prediction Distribution");
        })
        .catch(error => console.error("❌ Error fetching stats:", error));
}

// ✅ Render Pie Charts
function renderChart(canvasId, chartData, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`❌ Canvas '${canvasId}' not found!`);
        return;
    }

    const ctx = canvas.getContext("2d");

    // ✅ Fix: Ensure we are destroying only Chart instances
    if (window[canvasId] instanceof Chart) {
        window[canvasId].destroy();
    }

    // ✅ Create Pie Chart
    window[canvasId] = new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(chartData),
            datasets: [{
                data: Object.values(chartData),
                backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#8ecae6", "#ff6b6b"],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: title },
                legend: { position: "bottom" }
            }
        }
    });
}

// ✅ Listen for real-time prediction updates
socket.on("real_time_update", function (data) {
    console.log("📡 Real-time Prediction Update:", data);
    document.getElementById("predictionOutput").innerHTML =
        `Timestamp: <b>${data.timestamp}</b> <br> 
         IP: <b>${data.ip_address}</b> <br> 
         SVM Prediction: <b>${data["SVM Prediction"]}</b> <br> 
         RF Prediction: <b>${data["Random Forest Prediction"]}</b> <br> 
         Autoencoder Anomaly: <b>${data["Anomaly Detected"]}</b> <br> 
         Reconstruction Error: <b>${data["Reconstruction Error"]}</b>`;

    // ✅ Update prediction distribution chart dynamically
    if (window["predictionChart"]) {
        const chart = window["predictionChart"];
        const labelIndex = chart.data.labels.indexOf(data["Anomaly Detected"]);
        if (labelIndex !== -1) {
            chart.data.datasets[0].data[labelIndex] += 1;
        } else {
            chart.data.labels.push(data["Anomaly Detected"]);
            chart.data.datasets[0].data.push(1);
        }
        chart.update();
    }
});

// ✅ Listen for real-time accuracy updates
socket.on("accuracy_update", function (data) {
    console.log("📡 Real-time Accuracy Update:", data);
    updateChart("accuracyChart", data);
});

// ✅ Update Chart Data in Real-time
function updateChart(canvasId, newData) {
    if (window[canvasId] instanceof Chart) {
        window[canvasId].data.labels = Object.keys(newData);
        window[canvasId].data.datasets[0].data = Object.values(newData);
        window[canvasId].update();
    }
}
