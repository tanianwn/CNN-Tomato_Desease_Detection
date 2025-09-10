let classDistributionChart = null;
let healthSickChart = null;

function formatToMexicoCityTime(timestamp) {
    const date = new Date(timestamp);
    const options = {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        hour12: true,
    };
    return new Intl.DateTimeFormat('en-US', options).format(date);
}

async function loadRecentPredictions() {
    const response = await fetch("http://localhost:5000/history");
    const data = await response.json();

    const historyContainer = document.getElementById('recentPredictions');
    historyContainer.innerHTML = '';

    if (data.length === 0) {
        historyContainer.innerHTML = '<p>No predictions available yet.</p>';
        return;
    }

    data.forEach(prediction => {
        const div = document.createElement('div');
        div.classList.add('prediction-item');

        const mexicoCityTime = formatToMexicoCityTime(prediction.timestamp);

        div.innerHTML = `<strong>${prediction.label}</strong> (Confidence: ${(prediction.confidence * 100).toFixed(2)}%)<br><small>Predicted at: ${mexicoCityTime}</small>`;
        historyContainer.appendChild(div);
    });
}

async function loadClassDistribution() {
    const response = await fetch("http://localhost:5000/class_distribution_counts");
    const data = await response.json();

    const ctx = document.getElementById('predictionChart').getContext('2d');

    if (classDistributionChart) {
        classDistributionChart.destroy();
    }

    classDistributionChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#FF9F40'],
            }]
        }
    });
}

async function loadHealthSickData() {
    const response = await fetch("http://localhost:5000/class_distribution");
    const data = await response.json();

    const labels = data.map(item => item.date);
    const healthyData = data.map(item => item.healthy_percent);
    const sickData = data.map(item => item.sick_percent);

    const ctx = document.getElementById('healthSickChart').getContext('2d');

    if (healthSickChart) {
        healthSickChart.destroy();
    }

    healthSickChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Healthy Tomatoes (%)',
                    data: healthyData,
                    fill: false,
                    borderColor: '#8BC34A',
                    tension: 0.1
                },
                {
                    label: 'Sick Tomatoes (%)',
                    data: sickData,
                    fill: false,
                    borderColor: '#D32F2F',
                    tension: 0.1
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'category',
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                }
            }
        }
    });
}

document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("image", document.getElementById('imageFile').files[0]);

    const response = await fetch("http://localhost:5000/predict", {
        method: 'POST',
        body: formData,
    });

    const result = await response.json();
    console.log(result);

    if (response.ok) {
        loadRecentPredictions();
        loadClassDistribution();
        loadHealthSickData();
    } else {
        alert("Error: " + result.error);
    }
});

window.onload = () => {
    loadRecentPredictions();
    loadClassDistribution();
    loadHealthSickData();
};
