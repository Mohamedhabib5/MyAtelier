(function () {
    if (window.__myAtelierMobileNavBound) {
        return;
    }
    window.__myAtelierMobileNavBound = true;

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") {
            return;
        }

        var shell = document.getElementById("app-shell");
        if (!shell || !shell.classList.contains("mobile-menu-open")) {
            return;
        }

        var closeButton = document.getElementById("btn-sidebar-close-escape");
        if (closeButton) {
            closeButton.click();
        }
    });
})();
