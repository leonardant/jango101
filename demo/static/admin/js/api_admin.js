document.addEventListener("DOMContentLoaded", function () {

    const select = document.getElementById("id_user");

    const changeLink = document.getElementById("change_id_user");
    const viewLink = document.getElementById("view_id_user");

    if (!select) {
        return;
    }

    function updateRelatedLinks() {

        const userId = select.value;

        if (changeLink) {

            if (userId) {

                const template =
                    changeLink.dataset.hrefTemplate;

                changeLink.href = template.replace(
                    "__fk__",
                    userId
                );

            } else {

                changeLink.removeAttribute("href");

            }
        }


        if (viewLink) {

            if (userId) {

                const template =
                    viewLink.dataset.hrefTemplate;

                viewLink.href = template.replace(
                    "__fk__",
                    userId
                );

            } else {

                viewLink.removeAttribute("href");

            }
        }
    }


    // Set links when page loads
    updateRelatedLinks();


    // Update links when user changes
    select.addEventListener(
        "change",
        updateRelatedLinks
    );

});

document.addEventListener("DOMContentLoaded", function () {

    const regenerateButton =
        document.querySelector(
            ".regenerate-secret-button"
        );

    if (!regenerateButton) {
        return;
    }


    regenerateButton.addEventListener(
        "click",
        async function () {

            const confirmed = confirm(
                "Generate a new client secret?\n\n" +
                "The existing secret will immediately stop working."
            );

            if (!confirmed) {
                return;
            }


            try {

                const response = await fetch(
                    regenerateButton.dataset.url,
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCookie("csrftoken"),
                        },
                    }
                );


                if (!response.ok) {

                    throw new Error(
                        "Unable to generate a new secret."
                    );

                }


                const data =
                    await response.json();


                showClientSecretModal(
                    data.client_secret
                );

            }

            catch (error) {

                alert(
                    "An error occurred while generating " +
                    "the new client secret."
                );

            }

        }
    );


    // =====================================
    // Get Django CSRF token
    // =====================================

    function getCookie(name) {

        let cookieValue = null;

        const cookies =
            document.cookie.split(";");


        for (
            let i = 0;
            i < cookies.length;
            i++
        ) {

            const cookie =
                cookies[i].trim();


            if (
                cookie.startsWith(
                    name + "="
                )
            ) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;

            }

        }

        return cookieValue;
    }


    // =====================================
    // Display secret modal
    // =====================================

    function showClientSecretModal(secret) {

        const modal = document.createElement(
            "div"
        );

        modal.className =
            "client-secret-modal-overlay";


        modal.innerHTML = `

            <div class="client-secret-modal">

                <h2>
                    New Client Secret Generated
                </h2>

                <p>
                    Copy this secret now.
                    You will not be able to see it again.
                </p>

                <div class="client-secret-warning">
                    This window will close automatically
                    in 60 seconds.
                </div>

                <div class="client-secret-box">

                    <code>
                        ${secret}
                    </code>

                </div>

                <div class="client-secret-actions">

                    <button
                        type="button"
                        class="button copy-secret-button"
                    >
                        Copy secret
                    </button>

                    <button
                        type="button"
                        class="button close-secret-button"
                    >
                        Close
                    </button>

                </div>

            </div>
        `;


        document.body.appendChild(
            modal
        );


        // Copy button
        const copyButton =
            modal.querySelector(
                ".copy-secret-button"
            );


        copyButton.addEventListener(
            "click",
            async function () {

                await navigator.clipboard.writeText(
                    secret
                );

                copyButton.textContent =
                    "Copied!";
            }
        );


        // Close button
        const closeButton =
            modal.querySelector(
                ".close-secret-button"
            );


        function closeModal() {

            // Remove the secret from memory/DOM
            modal.remove();

        }


        closeButton.addEventListener(
            "click",
            closeModal
        );


        // Automatically disappear after 60 seconds
        setTimeout(
            closeModal,
            60000
        );

    }

});