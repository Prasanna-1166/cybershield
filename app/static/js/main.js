// main.js
// --------
// Two small, dependency-free behaviors used across every page:
//   1. Theme toggle (Auto / Light / Dark), persisted in localStorage.
//   2. Auto-dismissing toast notifications for flashed messages.
// Game timers, hint logic, and analyzer-specific behavior live in their
// own page-level <script> blocks (game/play.html, dashboard/report.html).

(function initTheme() {
    var STORAGE_KEY = "cs-theme";
    var ORDER = ["system", "light", "dark"];
    var LABELS = { system: "Auto", light: "Light", dark: "Dark" };

    function current() {
        return document.documentElement.getAttribute("data-theme") || "system";
    }

    function apply(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        var label = document.getElementById("csThemeToggleLabel");
        if (label) label.textContent = LABELS[theme] || "Auto";
    }

    document.addEventListener("DOMContentLoaded", function () {
        apply(current()); // sync the button label with whatever the head script already set

        var btn = document.getElementById("csThemeToggle");
        if (!btn) return;
        btn.addEventListener("click", function () {
            var next = ORDER[(ORDER.indexOf(current()) + 1) % ORDER.length];
            apply(next);
            try { localStorage.setItem(STORAGE_KEY, next); } catch (e) { /* ignore */ }
        });
    });
})();

(function initToasts() {
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".cs-toast").forEach(function (toast) {
            setTimeout(function () {
                toast.style.transition = "opacity 0.25s ease";
                toast.style.opacity = "0";
                setTimeout(function () { toast.remove(); }, 250);
            }, 6000);
        });
    });
})();
