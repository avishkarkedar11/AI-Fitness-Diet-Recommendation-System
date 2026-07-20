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

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    /* Gradient */

    const gradient = ctx.createLinearGradient(0, 0, 0, 420);

    gradient.addColorStop(0, "rgba(59,130,246,0.35)");
    gradient.addColorStop(0.5, "rgba(59,130,246,0.15)");
    gradient.addColorStop(1, "rgba(59,130,246,0)");

    new Chart(ctx, {

        type: "line",

        data: {

            labels: chartLabels,

            datasets: [

                {

                    label: "Weight",

                    data: chartWeights,

                    borderColor: "#2563EB",

                    backgroundColor: gradient,

                    fill: true,

                    borderWidth: 4,

                    tension: 0.45,

                    pointRadius: 6,

                    pointHoverRadius: 9,

                    pointBorderWidth: 3,

                    pointBackgroundColor: "#2563EB",

                    pointBorderColor: "#ffffff",

                    hitRadius: 15,

                    hoverBorderWidth: 4

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            interaction: {

                mode: "index",

                intersect: false

            },

            animation: {

                duration: 1800,

                easing: "easeOutQuart"

            },

            layout: {

                padding: {

                    top: 20,

                    left: 10,

                    right: 20,

                    bottom: 10

                }

            },

            plugins: {

                legend: {

                    display: true,

                    align: "start",

                    labels: {

                        usePointStyle: true,

                        pointStyle: "circle",

                        boxWidth: 10,

                        color: "#475569",

                        font: {

                            size: 13,

                            weight: "600"

                        }

                    }

                },

                tooltip: {

                    backgroundColor: "#0F172A",

                    titleColor: "#ffffff",

                    bodyColor: "#ffffff",

                    padding: 14,

                    cornerRadius: 14,

                    displayColors: false,

                    callbacks: {

                        label: function(context) {

                            return "Weight : " + context.parsed.y + " kg";

                        }

                    }

                }

            },

            scales: {

                x: {

                    grid: {

                        display: false

                    },

                    ticks: {

                        color: "#64748B",

                        font: {

                            size: 12

                        }

                    }

                },

                y: {

                    beginAtZero: false,

                    grace: "8%",

                    grid: {

                        color: "rgba(148,163,184,.15)",

                        drawBorder: false

                    },

                    ticks: {

                        color: "#64748B",

                        callback(value){

                            return value + " kg";

                        }

                    }

                }

            }

        }

    });

}

/* ==========================================
   Dynamic Greeting
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    const greeting = document.getElementById("dashboardGreeting");

    if (!greeting) return;

    const hour = new Date().getHours();

    let text = "Welcome,";

    if (hour >= 5 && hour < 12) {

        text = "🌅 Good Morning,";

    }

    else if (hour >= 12 && hour < 17) {

        text = "☀️ Good Afternoon,";

    }

    else if (hour >= 17 && hour < 21) {

        text = "🌇 Good Evening,";

    }

    else {

        text = "🌙 Good Night,";

    }

    greeting.textContent = text;

});

/* ==========================================
   Dynamic Goal Progress
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    const start = parseFloat(document.getElementById("startWeight")?.dataset.value);

    const current = parseFloat(document.getElementById("currentWeight")?.dataset.value);

    const goal = parseFloat(document.getElementById("goalWeight")?.dataset.value);

    const bar = document.getElementById("goalBar");

    const percent = document.getElementById("goalPercent");

    if (!bar || !percent) return;

    if (isNaN(start) || isNaN(current) || isNaN(goal)) return;

    let progress = ((current - start) / (goal - start)) * 100;

    progress = Math.max(0, Math.min(progress, 100));

    bar.style.width = progress + "%";

    percent.innerHTML = Math.round(progress) + "%";

});