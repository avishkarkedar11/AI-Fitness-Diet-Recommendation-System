/* ===========================
   Animated Counter
=========================== */

const counters = document.querySelectorAll(".counter");

const animateCounter = () => {

    counters.forEach(counter => {

        const target = +counter.dataset.target;

        const update = () => {

            const value = +counter.innerText;

            const increment = Math.ceil(target / 70);

            if(value < target){

                counter.innerText = value + increment;

                setTimeout(update,25);

            }else{

                counter.innerText = target;

            }

        };

        update();

    });

};

const observer = new IntersectionObserver(entries=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            animateCounter();

            observer.disconnect();

        }

    });

});

observer.observe(document.querySelector(".stats-section"));

const navbar = document.querySelector(".premium-navbar");

window.addEventListener("scroll",()=>{

if(window.scrollY>50){

navbar.classList.add("scrolled");

}else{

navbar.classList.remove("scrolled");

}

});