/*
==================================================
Chart.js Configuration
AI Fitness & Diet Recommendation System
==================================================
*/

document.addEventListener("DOMContentLoaded", function () {

    initializeWeightChart();

});


/* ==========================================
   Weight Progress Chart
========================================== */

function initializeWeightChart() {

    const canvas = document.getElementById("weightChart");

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {

        type: "line",

        data: {

            labels: [
                "Week 1",
                "Week 2",
                "Week 3",
                "Week 4",
                "Week 5",
                "Week 6"
            ],

            labels: chartLabels,

            datasets: [

            {

                label: "Weight (kg)",

                data: chartWeights,

                borderColor: "#0d6efd",

                backgroundColor: "rgba(13,110,253,.15)",

                fill: true,

                tension: .35

            }

        ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: true,

                    position: "top"

                }

            },

            scales: {

                y: {

                    beginAtZero: false,

                    title: {

                        display: true,

                        text: "Weight (kg)"

                    }

                },

                x: {

                    title: {

                        display: true,

                        text: "Progress"

                    }

                }

            }

        }

    });

}