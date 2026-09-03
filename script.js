document.addEventListener("DOMContentLoaded", function () {


    /*
     * ============================================
     * GITHUB REPOSITORY
     * ============================================
     */

    const GITHUB_OWNER = "baotop2a8";

    const GITHUB_REPO = "baotop-minecraft-manager";

    const GITHUB_API =
     `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/downloads`;



    /*
     * ============================================
     * ELEMENTS
     * ============================================
     */

    const betaContainer =
        document.getElementById("beta-versions");


    const releaseContainer =
        document.getElementById("release-versions");


    const recommendedTitle =
        document.getElementById("recommended-title");


    const recommendedDescription =
        document.getElementById("recommended-description");


    const recommendedDownload =
        document.getElementById("recommended-download");


    const downloadButton =
        document.getElementById("download-button");


    const downloadDescription =
        document.getElementById("download-description");


    const heroDownload =
        document.getElementById("hero-download");



    /*
     * ============================================
     * SMOOTH SCROLL
     * ============================================
     */

    const internalLinks =
        document.querySelectorAll('a[href^="#"]');


    internalLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId =
                this.getAttribute("href");


            if (!targetId || targetId === "#") {
                return;
            }


            const target =
                document.querySelector(targetId);


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



    /*
     * ============================================
     * YEAR
     * ============================================
     */

    const yearElement =
        document.getElementById("year");


    if (yearElement) {

        yearElement.textContent =
            new Date().getFullYear();

    }



    /*
     * ============================================
     * HEADER SCROLL
     * ============================================
     */

    const header =
        document.querySelector(".header");


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



    /*
     * ============================================
     * PARSE VERSION
     * ============================================
     *
     * Supported:
     *
     * MinecraftServerManager_v2.py
     * MinecraftServerManager_v5.py
     *
     * MinecraftServerManager_v6(beta1).py
     * MinecraftServerManager_v6(beta2).py
     * MinecraftServerManager_v6(beta3).py
     *
     */


    function parseVersion(filename) {

        const releaseMatch =
            filename.match(
                /^MinecraftServerManager_v(\d+)\.py$/i
            );


        if (releaseMatch) {

            return {

                filename: filename,

                version:
                    parseInt(
                        releaseMatch[1],
                        10
                    ),

                beta: 0,

                isBeta: false

            };

        }



        const betaMatch =
            filename.match(
                /^MinecraftServerManager_v(\d+)\(beta(\d+)\)\.py$/i
            );


        if (betaMatch) {

            return {

                filename: filename,

                version:
                    parseInt(
                        betaMatch[1],
                        10
                    ),

                beta:
                    parseInt(
                        betaMatch[2],
                        10
                    ),

                isBeta: true

            };

        }


        /*
         * Any unrelated file is ignored.
         *
         * Examples:
         *
         * blabla.txt
         * README.md
         * test.py
         * icon.ico
         *
         */

        return null;

    }



    /*
     * ============================================
     * DISPLAY VERSION NAME
     * ============================================
     */

    function getDisplayName(item) {

        if (item.isBeta) {

            return (
                `V${item.version} Beta ${item.beta}`
            );

        }


        return `V${item.version}`;

    }



    /*
     * ============================================
     * SORT
     * ============================================
     */

    function sortVersions(a, b) {

        /*
         * Newer major version first
         */

        if (a.version !== b.version) {

            return b.version - a.version;

        }


        /*
         * For same version:
         *
         * Beta 4
         * Beta 3
         * Beta 2
         * Beta 1
         */

        return b.beta - a.beta;

    }



    /*
     * ============================================
     * CREATE CARD
     * ============================================
     */

    function createVersionCard(
        item,
        options = {}
    ) {

        const card =
            document.createElement("div");


        card.className =
            "version-card";


        if (options.latest) {

            card.classList.add(
                "latest-version"
            );

        }


        if (options.recommended) {

            card.classList.add(
                "recommended-version"
            );

        }



        /*
         * INFO
         */

        const info =
            document.createElement("div");



        /*
         * TAG
         */

        if (options.latest) {

            const tag =
                document.createElement("span");


            tag.className =
                "version-tag";


            tag.textContent =
                "LATEST BETA";


            info.appendChild(tag);

        }


        if (options.recommended) {

            const tag =
                document.createElement("span");


            tag.className =
                "version-tag recommended-tag";


            tag.textContent =
                "⭐ RECOMMENDED";


            info.appendChild(tag);

        }



        /*
         * TITLE
         */

        const title =
            document.createElement("h3");


        title.textContent =
            getDisplayName(item);


        info.appendChild(title);



        /*
         * FILE NAME
         */

        const filename =
            document.createElement("p");


        filename.textContent =
            item.filename;


        info.appendChild(filename);



        /*
         * DOWNLOAD BUTTON
         */

        const button =
            document.createElement("a");


        button.href =
            item.download_url;


        button.download =
            item.filename;


        button.textContent =
            "Download";



        button.addEventListener(
            "click",
            function () {

                const originalText =
                    button.textContent;


                button.textContent =
                    "Downloading...";


                setTimeout(
                    function () {

                        button.textContent =
                            originalText;

                    },
                    1200
                );

            }
        );


        card.appendChild(info);

        card.appendChild(button);


        return card;

    }



    /*
     * ============================================
     * SET RECOMMENDED RELEASE
     * ============================================
     */

    function setRecommendedRelease(
        release
    ) {

        if (!release) {

            recommendedTitle.textContent =
                "No Release Available";


            recommendedDescription.textContent =
                "No stable release was found in the GitHub repository.";


            recommendedDownload.textContent =
                "Unavailable";


            recommendedDownload.classList.add(
                "disabled"
            );


            downloadButton.textContent =
                "Unavailable";


            downloadButton.classList.add(
                "disabled"
            );


            downloadDescription.textContent =
                "No stable release is currently available.";


            return;

        }



        const displayName =
            getDisplayName(release);



        recommendedTitle.innerHTML =
            `Minecraft Server Manager <strong>${displayName}</strong>`;


        recommendedDescription.textContent =
            "The newest stable release recommended for most users.";


        recommendedDownload.href =
            release.download_url;


        recommendedDownload.download =
            release.filename;


        recommendedDownload.textContent =
            `⬇ Download ${displayName}`;


        recommendedDownload.classList.remove(
            "disabled"
        );



        downloadButton.href =
            release.download_url;


        downloadButton.download =
            release.filename;


        downloadButton.textContent =
            `⬇ Download ${displayName}`;


        downloadButton.classList.remove(
            "disabled"
        );


        downloadDescription.textContent =
            `Recommended stable release: ${displayName}`;

    }



    /*
     * ============================================
     * LOAD GITHUB VERSIONS
     * ============================================
     */

    async function loadVersions() {

        try {

            /*
             * Request GitHub repository files
             */

            const response =
                await fetch(
                    GITHUB_API,
                    {
                        headers: {
                            "Accept":
                                "application/vnd.github+json"
                        }
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `GitHub API returned ${response.status}`
                );

            }


            const files =
                await response.json();



            /*
             * Make sure GitHub returned an array
             */

            if (!Array.isArray(files)) {

                throw new Error(
                    "GitHub API did not return a file list."
                );

            }



            /*
             * Parse files
             */

            const versions =
                files

                    .filter(function (file) {

                        return (
                            file.type === "file"
                        );

                    })

                    .map(function (file) {

                        const parsed =
                            parseVersion(
                                file.name
                            );


                        if (!parsed) {

                            return null;

                        }


                        parsed.download_url =
                            file.download_url;


                        return parsed;

                    })

                    .filter(function (item) {

                        return item !== null;

                    });



            /*
             * Separate Beta
             */

            const betaVersions =
                versions

                    .filter(function (item) {

                        return item.isBeta;

                    })

                    .sort(sortVersions);



            /*
             * Separate Release
             */

            const releaseVersions =
                versions

                    .filter(function (item) {

                        return !item.isBeta;

                    })

                    .sort(sortVersions);



            /*
             * Clear containers
             */

            betaContainer.innerHTML = "";

            releaseContainer.innerHTML = "";



            /*
             * ========================================
             * RECOMMENDED RELEASE
             * ========================================
             */

            if (
                releaseVersions.length > 0
            ) {

                const recommended =
                    releaseVersions[0];


                setRecommendedRelease(
                    recommended
                );



                /*
                 * Release cards
                 */

                releaseVersions.forEach(
                    function (item) {

                        releaseContainer.appendChild(

                            createVersionCard(
                                item
                            )

                        );

                    }
                );

            } else {

                setRecommendedRelease(
                    null
                );


                releaseContainer.innerHTML =
                    `
                    <div class="empty-message">
                        No stable releases available.
                    </div>
                    `;

            }



            /*
             * ========================================
             * BETA
             * ========================================
             */

            if (
                betaVersions.length > 0
            ) {

                betaVersions.forEach(
                    function (
                        item,
                        index
                    ) {

                        betaContainer.appendChild(

                            createVersionCard(
                                item,
                                {
                                    latest:
                                        index === 0
                                }
                            )

                        );

                    }
                );

            } else {

                betaContainer.innerHTML =
                    `
                    <div class="empty-message">
                        No beta versions available.
                    </div>
                    `;

            }



            /*
             * ========================================
             * CARD ANIMATION
             * ========================================
             */

            const cards =
                document.querySelectorAll(
                    ".version-card"
                );


            cards.forEach(
                function (
                    card,
                    index
                ) {

                    card.style.animationDelay =
                        `${index * 0.04}s`;

                }
            );



            /*
             * ========================================
             * HERO DOWNLOAD
             * ========================================
             */

            if (
                releaseVersions.length > 0
            ) {

                const latestRelease =
                    releaseVersions[0];


                heroDownload.href =
                    latestRelease.download_url;


                heroDownload.download =
                    latestRelease.filename;


                heroDownload.textContent =
                    `⬇ Download ${getDisplayName(latestRelease)}`;

            } else if (
                betaVersions.length > 0
            ) {

                const latestBeta =
                    betaVersions[0];


                heroDownload.href =
                    latestBeta.download_url;


                heroDownload.download =
                    latestBeta.filename;


                heroDownload.textContent =
                    `⬇ Download ${getDisplayName(latestBeta)}`;

            }



        } catch (error) {

            console.error(
                "GitHub version loading error:",
                error
            );


            betaContainer.innerHTML =
                `
                <div class="empty-message">
                    ❌ Failed to load beta versions from GitHub.
                    <br><br>
                    Please try refreshing the page.
                </div>
                `;


            releaseContainer.innerHTML =
                `
                <div class="empty-message">
                    ❌ Failed to load releases from GitHub.
                    <br><br>
                    Please try refreshing the page.
                </div>
                `;


            recommendedTitle.textContent =
                "Unable to load versions";


            recommendedDescription.textContent =
                "GitHub could not be reached right now.";


            recommendedDownload.textContent =
                "Try Again";


            recommendedDownload.href =
                "#versions";

        }

    }



    /*
     * ============================================
     * START
     * ============================================
     */

    loadVersions();

});
