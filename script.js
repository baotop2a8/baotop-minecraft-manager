document.addEventListener("DOMContentLoaded", function () {

    // Smooth scrolling for internal links
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId = this.getAttribute("href");

            if (targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });

    });


    // Add a small visual effect when downloading
    document.querySelectorAll(
        'a[href$=".py"]'
    ).forEach(function (button) {

        button.addEventListener("click", function () {

            const originalText = this.textContent;

            this.textContent = "Downloading...";

            setTimeout(function () {
                button.textContent = originalText;
            }, 1200);

        });

    });


    // Current year in footer
    const year = new Date().getFullYear();

    document.querySelectorAll("footer").forEach(function (footer) {

        footer.innerHTML = footer.innerHTML.replace(
            "© 2026",
            "© " + year
        );

    });

});
