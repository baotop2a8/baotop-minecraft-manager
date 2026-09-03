document.addEventListener("DOMContentLoaded", function () {

    /* Smooth scrolling */
    const internalLinks = document.querySelectorAll('a[href^="#"]');

    internalLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {

            const targetId = this.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (!target) {
                return;
            }

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });


    /* Download button animation */
    const downloadButtons = document.querySelectorAll('a[download]');

    downloadButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const originalText = button.textContent;

            button.classList.add("downloading");
            button.textContent = "Downloading...";

            setTimeout(function () {
                button.textContent = originalText;
                button.classList.remove("downloading");
            }, 1200);

        });

    });


    /* Current year */
    const yearElement = document.getElementById("year");

    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }


    /* Header scroll effect */
    const header = document.querySelector(".header");

    window.addEventListener("scroll", function () {

        if (!header) {
            return;
        }

        if (window.scrollY > 30) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }

    });


    /* Version card animation delay */
    const cards = document.querySelectorAll(".version-card");

    cards.forEach(function (card, index) {
        card.style.animationDelay = (index * 0.04) + "s";
    });

});
