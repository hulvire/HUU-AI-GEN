(function () {
    "use strict";

    const APP_NAME = "HUU-AI-GEN";
    const INITIALIZED_ATTRIBUTE =
        "data-huu-animations-initialized";

    function prefersReducedMotion() {
        return window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;
    }

    function findElements() {
        return {
            header: document.querySelector(
                ".app-header"
            ),
            eyebrow: document.querySelector(
                ".app-header__eyebrow"
            ),
            title: document.querySelector(
                ".app-header__title"
            ),
            description: document.querySelector(
                ".app-header__description"
            ),
            meta: document.querySelector(
                ".app-header__meta"
            ),
            glow: document.querySelector(
                ".app-header__glow"
            ),
            sidebar: document.querySelector(
                "#generator-sidebar"
            ),
            preview: document.querySelector(
                "#preview"
            ),
            sections: document.querySelectorAll(
                ".settings-section"
            ),
        };
    }

    function hasRequiredElements(elements) {
        return Boolean(
            elements.header
            && elements.title
            && elements.sidebar
        );
    }

    function wasAlreadyInitialized(header) {
        return (
            header.getAttribute(
                INITIALIZED_ATTRIBUTE
            ) === "true"
        );
    }

    function markAsInitialized(header) {
        header.setAttribute(
            INITIALIZED_ATTRIBUTE,
            "true"
        );
    }

    function revealWithoutAnimation(elements) {
        const targets = [
            elements.header,
            elements.eyebrow,
            elements.title,
            elements.description,
            elements.meta,
            elements.glow,
            elements.sidebar,
            elements.preview,
            ...elements.sections,
        ].filter(Boolean);

        if (
            typeof window.gsap !== "undefined"
            && targets.length > 0
        ) {
            window.gsap.set(
                targets,
                {
                    clearProps: "all",
                }
            );
        }
    }

    function createIntroAnimation(elements) {
        const timeline = window.gsap.timeline({
            defaults: {
                ease: "power3.out",
            },
        });

        timeline.fromTo(
            elements.header,
            {
                opacity: 0,
                y: 24,
            },
            {
                opacity: 1,
                y: 0,
                duration: 0.7,
            }
        );

        if (elements.glow) {
            timeline.fromTo(
                elements.glow,
                {
                    opacity: 0,
                    scale: 0.7,
                },
                {
                    opacity: 1,
                    scale: 1,
                    duration: 1.2,
                },
                "-=0.65"
            );
        }

        if (elements.eyebrow) {
            timeline.fromTo(
                elements.eyebrow,
                {
                    opacity: 0,
                    y: 12,
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.4,
                },
                "-=0.85"
            );
        }

        timeline.fromTo(
            elements.title,
            {
                opacity: 0,
                y: 34,
                filter: "blur(10px)",
            },
            {
                opacity: 1,
                y: 0,
                filter: "blur(0px)",
                duration: 0.8,
            },
            "-=0.55"
        );

        const headerDetails = [
            elements.description,
            elements.meta,
        ].filter(Boolean);

        if (headerDetails.length > 0) {
            timeline.fromTo(
                headerDetails,
                {
                    opacity: 0,
                    y: 18,
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.55,
                    stagger: 0.1,
                },
                "-=0.45"
            );
        }

        timeline.fromTo(
            elements.sidebar,
            {
                opacity: 0,
                x: -26,
            },
            {
                opacity: 1,
                x: 0,
                duration: 0.65,
            },
            "-=0.4"
        );

        if (elements.preview) {
            timeline.fromTo(
                elements.preview,
                {
                    opacity: 0,
                    x: 26,
                },
                {
                    opacity: 1,
                    x: 0,
                    duration: 0.65,
                },
                "<"
            );
        }

        if (elements.sections.length > 0) {
            timeline.fromTo(
                elements.sections,
                {
                    opacity: 0,
                    y: 12,
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.35,
                    stagger: 0.07,
                },
                "-=0.35"
            );
        }
    }

    function initializeAnimations() {
        if (typeof window.gsap === "undefined") {
            console.warn(
                `[${APP_NAME}] GSAP is not available.`
            );

            return false;
        }

        const elements = findElements();

        if (!hasRequiredElements(elements)) {
            return false;
        }

        if (wasAlreadyInitialized(elements.header)) {
            return true;
        }

        markAsInitialized(elements.header);

        if (prefersReducedMotion()) {
            revealWithoutAnimation(elements);
            return true;
        }

        createIntroAnimation(elements);

        console.info(
            `[${APP_NAME}] UI animations initialized.`
        );

        return true;
    }

    function waitForInterface() {
        if (initializeAnimations()) {
            return;
        }

        const observer = new MutationObserver(
            () => {
                if (initializeAnimations()) {
                    observer.disconnect();
                }
            }
        );

        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true,
            }
        );

        window.setTimeout(
            () => {
                observer.disconnect();
            },
            10000
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            waitForInterface,
            {
                once: true,
            }
        );
    } else {
        waitForInterface();
    }
})();

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

