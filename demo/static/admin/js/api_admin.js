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