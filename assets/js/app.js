(function () {
    "use strict";

    const TRIGGER_SELECTOR =
        ".huu-collapsible__trigger";

    function toggleSection(trigger) {
        const section = trigger.closest(
            ".huu-collapsible"
        );

        if (!section) {
            return;
        }

        const willOpen =
            !section.classList.contains(
                "is-open"
            );

        section.classList.toggle(
            "is-open",
            willOpen
        );

        trigger.setAttribute(
            "aria-expanded",
            String(willOpen)
        );
    }

    document.addEventListener(
        "click",
        (event) => {
            const target = event.target;

            if (!(target instanceof Element)) {
                return;
            }

            const trigger = target.closest(
                TRIGGER_SELECTOR
            );

            if (!trigger) {
                return;
            }

            event.preventDefault();
            toggleSection(trigger);
        }
    );
})();