/* ===========================
   Animated Counter
=========================== */

const counters = document.querySelectorAll(".counter");

function animateCounter() {

    counters.forEach(counter => {

        const target = Number(counter.dataset.target);

        const update = () => {

            const value = Number(counter.innerText);

            const increment = Math.ceil(target / 70);

            if (value < target) {

                counter.innerText = Math.min(value + increment, target);

                setTimeout(update, 25);

            } else {

                counter.innerText = target;

            }

        };

        update();

    });

}

/* ===========================
   Counter Observer
=========================== */

const statsSection = document.querySelector(".stats-section");

if (statsSection && counters.length) {

    const observer = new IntersectionObserver(entries => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                animateCounter();

                observer.disconnect();

            }

        });

    });

    observer.observe(statsSection);

}

/* ===========================
   Navbar Scroll
=========================== */

const navbar = document.querySelector(".premium-navbar");

if (navbar) {

    window.addEventListener("scroll", () => {

        if (window.scrollY > 50) {

            navbar.classList.add("scrolled");

        } else {

            navbar.classList.remove("scrolled");

        }

    });

}