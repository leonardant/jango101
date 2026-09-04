(function () {
    "use strict";


    function initialiseRelatedUserButtons() {

        const select = document.getElementById("id_user");

        if (!select) {
            return;
        }

        const changeButton = document.getElementById("change_id_user");
        const viewButton = document.getElementById("view_id_user");


        function updateRelatedLinks() {

            const userId = select.value;

            /*
             * Pencil / Change button
             */
            if (changeButton) {

                const template =
                    changeButton.getAttribute("data-href-template");

                if (template && userId) {

                    const url = template.replace(
                        "__fk__",
                        userId
                    );

                    changeButton.setAttribute(
                        "href",
                        url
                    );

                } else {

                    changeButton.removeAttribute("href");
                }
            }


            /*
             * Eye / View button
             */
            if (viewButton) {

                const template =
                    viewButton.getAttribute("data-href-template");

                if (template && userId) {

                    const url = template.replace(
                        "__fk__",
                        userId
                    );

                    viewButton.setAttribute(
                        "href",
                        url
                    );

                } else {

                    viewButton.removeAttribute("href");
                }
            }
        }


        /*
         * Set links immediately when page loads
         */
        updateRelatedLinks();


        /*
         * Update links if admin changes the selected user
         */
        select.addEventListener(
            "change",
            function () {

                updateRelatedLinks();

                /*
                 * Reload the page so the credential page
                 * reflects the newly selected user.
                 */
                if (select.value) {

                    /*
                     * Only reload if this is an existing
                     * credential being edited.
                     */
                    const currentUrl =
                        new URL(window.location.href);

                    currentUrl.searchParams.set(
                        "user",
                        select.value
                    );
                }
            }
        );


        /*
         * Handle pencil explicitly.
         *
         * Open the Django admin change page as a popup.
         */
        if (changeButton) {

            changeButton.addEventListener(
                "click",
                function (event) {

                    const href =
                        changeButton.getAttribute("href");

                    if (!href) {

                        event.preventDefault();

                        return;
                    }

                    event.preventDefault();


                    window.open(
                        href,
                        "change_related_user",
                        [
                            "height=800",
                            "width=1000",
                            "resizable=yes",
                            "scrollbars=yes"
                        ].join(",")
                    );
                }
            );
        }


        /*
         * The eye button can behave as a normal link.
         *
         * No JavaScript interception is required.
         */
    }


    /*
     * =====================================
     * Generate new client secret
     * =====================================
     */

    function initialiseGenerateSecretButton() {

        const button =
            document.querySelector(
                ".regenerate-secret-button"
            );

        if (!button) {
            return;
        }


        button.addEventListener(
            "click",
            async function () {

                const url =
                    button.dataset.url;

                if (!url) {
                    alert(
                        "Unable to determine the regenerate secret URL."
                    );

                    return;
                }


                if (
                    !confirm(
                        "Generate a new client secret? " +
                        "The existing secret will stop working."
                    )
                ) {
                    return;
                }


                button.disabled = true;

                const originalText =
                    button.textContent;

                button.textContent =
                    "Generating...";


                try {

                    const csrfToken =
                        document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        )?.value;


                    const response =
                        await fetch(
                            url,
                            {
                                method: "POST",

                                headers: {
                                    "X-CSRFToken":
                                        csrfToken,

                                    "X-Requested-With":
                                        "XMLHttpRequest",
                                },
                            }
                        );


                    if (!response.ok) {

                        throw new Error(
                            "Unable to generate new secret."
                        );
                    }


                    const data =
                        await response.json();


                    showSecretModal(
                        data.client_secret
                    );


                } catch (error) {

                    console.error(error);

                    alert(
                        "Unable to generate a new client secret."
                    );

                } finally {

                    button.disabled = false;

                    button.textContent =
                        originalText;
                }
            }
        );
    }


    /*
     * =====================================
     * Secret modal
     * =====================================
     */

    function showSecretModal(secret) {

        const overlay =
            document.createElement("div");

        overlay.className =
            "client-secret-modal-overlay";


        overlay.innerHTML = `
            <div class="client-secret-modal">

                <h2>New client secret</h2>

                <p>
                    Copy this secret now.
                    It will not be shown again.
                </p>

                <div class="client-secret-box">
                    <code></code>
                </div>

                <p class="client-secret-warning">
                    Once this window is closed,
                    the secret cannot be retrieved again.
                </p>

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


        overlay.querySelector("code").textContent =
            secret;


        document.body.appendChild(
            overlay
        );


        const copyButton =
            overlay.querySelector(
                ".copy-secret-button"
            );


        copyButton.addEventListener(
            "click",
            async function () {

                try {

                    await navigator.clipboard.writeText(
                        secret
                    );

                    copyButton.textContent =
                        "Copied!";

                } catch (error) {

                    console.error(error);
                }
            }
        );


        const closeButton =
            overlay.querySelector(
                ".close-secret-button"
            );


        closeButton.addEventListener(
            "click",
            function () {

                overlay.remove();
            }
        );
    }


    /*
     * =====================================
     * Initialise everything
     * =====================================
     */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initialiseRelatedUserButtons();

            initialiseGenerateSecretButton();
        }
    );

})();