document.addEventListener("DOMContentLoaded", () => {
    const bouton = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");

    if (!bouton) return;

    function appliquerIcone() {
        const theme = document.documentElement.getAttribute("data-theme");
        if (icon) {
            icon.textContent = theme === "dark" ? "☀️" : "🌙";
        }
    }

    appliquerIcone();

    bouton.addEventListener("click", () => {
        const themeActuel = document.documentElement.getAttribute("data-theme");

        if (themeActuel === "dark") {
            document.documentElement.removeAttribute("data-theme");
            localStorage.setItem("sdf-theme", "light");
        } else {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("sdf-theme", "dark");
        }

        appliquerIcone();
    });
});