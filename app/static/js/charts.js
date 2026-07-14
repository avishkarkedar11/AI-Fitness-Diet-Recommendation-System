/*
==================================================
Chart.js Configuration
AI Fitness & Diet Recommendation System
==================================================
*/

document.addEventListener("DOMContentLoaded", () => {

    initializeWeightChart();

});


/* ==================================================
   Weight Progress Chart
================================================== */

function initializeWeightChart() {

    const canvas = document.getElementById("weightChart");

    if (!canvas) {
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {

        type: "line",

        data: {

            labels: chartLabels,

            datasets: [

                {

                    label: "Weight (kg)",

                    data: chartWeights,

                    borderColor: "#0d6efd",

                    backgroundColor: "rgba(13,110,253,0.15)",

                    borderWidth: 3,

                    pointRadius: 5,

                    pointHoverRadius: 7,

                    pointBackgroundColor: "#0d6efd",

                    pointBorderColor: "#ffffff",

                    pointBorderWidth: 2,

                    fill: true,

                    tension: 0.35

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            interaction: {

                intersect: false,

                mode: "index"

            },

            plugins: {

                legend: {

                    display: true,

                    position: "top",

                    labels: {

                        usePointStyle: true,

                        padding: 20

                    }

                },

                tooltip: {

                    callbacks: {

                        label: function(context) {

                            return "Weight : " + context.parsed.y + " kg";

                        }

                    }

                }

            },

            scales: {

                x: {

                    title: {

                        display: true,

                        text: "Progress Date",

                        font: {

                            size: 14,

                            weight: "bold"

                        }

                    },

                    grid: {

                        display: false

                    }

                },

                y: {

                    title: {

                        display: true,

                        text: "Weight (kg)",

                        font: {

                            size: 14,

                            weight: "bold"

                        }

                    },

                    beginAtZero: false,

                    ticks: {

                        callback: function(value) {

                            return value + " kg";

                        }

                    }

                }

            }

        }

    });

}