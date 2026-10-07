document.addEventListener("DOMContentLoaded", function () {

    // ----------------------------------
    // 1. Retrieve initial data from Django
    // ----------------------------------

    const chartData = JSON.parse(
        document.querySelector("#chart-data").textContent
    );

    const canvas = document.querySelector("#studyChart");

    const periodButtons = document.querySelectorAll(".period-btn");

    const totalMinutes = document.querySelector("#total-minutes");
    const sessionCount = document.querySelector("#session-count");
    const mostStudied = document.querySelector("#most-studied");
    const studyTimeList = document.querySelector("#study-time-list");
    const errorMessage = document.querySelector("#dashboard-error");


    // ----------------------------------
    // 2. Generate colours for each subject
    // ----------------------------------

    function generateColors(count) {
        const palette = [
            "#E9A6C2", // Pink
            "#B8E0D2", // Mint green
            "#CDB4DB", // Lavender
            "#A2D2FF", // Light blue
            "#FFB4A2", // Peach
            "#B5EAD7", // Pastel green
            "#FFDAC1", // Apricot
            "#D4A5F9", // Purple
            "#F4C2C2"  // Rose
        ];

        const colors = [];

        for (let i = 0; i < count; i++) {
            if (i < palette.length) {
                colors.push(palette[i]);
            } else {
                // Generate additional distinct colours
                const hue = ((i - palette.length) * 137.508 + 45) % 360;

                colors.push(
                    `hsl(${hue} 70% 75%)`
                );
            }
        }
        return colors;
    }

    // ----------------------------------
    // 3. Create Chart.js pie chart
    // ----------------------------------

    const studyChart = new Chart(canvas, {
        type: "pie",

        data: {
            labels: chartData.labels,

            datasets: [{
                label: "Study Time (minutes)",
                data: chartData.minutes,
                backgroundColor: generateColors(
                    chartData.labels.length
                ),
                borderColor: "#FFFFFF",
                borderWidth: 5
            }]

        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    position: "bottom"
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const subject = context.label;
                            const minutes = context.parsed;

                            return `${subject}: ${minutes} minutes`;
                        }
                    }
                }
            }
        }
    });

    // ----------------------------------
    // 4. Update the most studied subject
    // ----------------------------------

    function updateMostStudied(data) {
        mostStudied.replaceChildren();

        if (data.most_studied) {
            const heading = document.createElement("h2");

            heading.textContent = data.most_studied;

            const duration = document.createElement("p");

            duration.textContent =
                `${data.most_studied_minutes} minutes`;

            mostStudied.append(heading, duration);

        } else {
            const message = document.createElement("p");
            message.textContent = "No study sessions yet.";
            mostStudied.appendChild(message);
        }
    }

    // ----------------------------------
    // 5. Update study time by subject
    // ----------------------------------

    function updateStudyTime(chartData) {
        studyTimeList.replaceChildren();

        // Handle periods without study sessions
        if (chartData.labels.length === 0) {
            const message = document.createElement("p");

            message.textContent =
                "No study activity for this period.";

            studyTimeList.appendChild(message);

            return;
        }

        // Create a row for each subject
        chartData.labels.forEach(function (subject, index) {
            const row = document.createElement("div");

            row.className =
                "d-flex justify-content-between mb-2";

            // Subject name
            const name = document.createElement("span");

            name.textContent = subject;

            // Subject duration
            const duration = document.createElement("span");

            duration.textContent =
                `${chartData.minutes[index]} minutes`;

            // Add elements to the row
            row.append(name, duration);

            // Add row to the dashboard
            studyTimeList.appendChild(row);
        });
    }

    // ----------------------------------
    // 6. Update the pie chart
    // ----------------------------------

    function updateChart(chartData) {
        // Update subject names
        studyChart.data.labels = chartData.labels;

        // Update study durations
        studyChart.data.datasets[0].data =
            chartData.minutes;

        // Generate colours for the current subjects
        studyChart.data.datasets[0].backgroundColor =
            generateColors(chartData.labels.length);

        studyChart.update();
    }


    // ----------------------------------
    // 7. Update the selected period button
    // ----------------------------------

    function updateActiveButton(selectedPeriod) {
        periodButtons.forEach(function (button) {

            const isActive =
                button.dataset.period === selectedPeriod;

            button.classList.toggle("active", isActive);

            if (isActive) {
                button.setAttribute("aria-current", "page");
            } else {
                button.removeAttribute("aria-current");
            }
        });
    }


    // ----------------------------------
    // 8. Handle period selection
    // ----------------------------------

    let latestRequest = 0;

    periodButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            // Prevent the normal page reload
            event.preventDefault();

            // Get the selected period
            const period = button.dataset.period;

            // Track the latest request
            const requestId = ++latestRequest;

            // Hide previous errors
            errorMessage.hidden = true;

            // Build the request URL
            const url = new URL(button.href);

            url.searchParams.set("format", "json");

            // Request updated statistics from Django
            fetch(url)
                .then(function (response) {

                    if (!response.ok) {
                        throw new Error(
                            "Failed to load dashboard data"
                        );
                    }

                    return response.json();
                })
                .then(function (data) {

                    // Ignore outdated responses
                    if (requestId !== latestRequest) {
                        return;
                    }

                    totalMinutes.textContent =
                        `${data.total_minutes} minutes`;

                    sessionCount.textContent =
                        data.session_count;

                    updateMostStudied(data);
                    updateStudyTime(data.chart_data);
                    updateChart(data.chart_data);
                    updateActiveButton(period);

                    // Update browser URL
                    window.history.replaceState(
                        null,
                        "",
                        button.href
                    );
                })

                .catch(function (error) {

                    // Ignore errors from outdated requests
                    if (requestId !== latestRequest) {
                        return;
                    }

                    console.error(
                        "Dashboard update failed:",
                        error
                    );

                    errorMessage.hidden = false;
                });
        });
    });
});
