// ===========================
// Interactive Controls & State
// ===========================

// Theme Toggle
function initThemeToggle() {
    const toggle = document.querySelector('.theme-toggle');
    const html = document.documentElement;

    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);

    toggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// Scroll-based Section Animations
function initScrollAnimations() {
    const sections = document.querySelectorAll('.section');
    const steps = document.querySelectorAll('.step');

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        }
    );

    sections.forEach((section) => observer.observe(section));
    steps.forEach((step) => observer.observe(step));
}

// Transition Slider (Standard vs Attention)
function initTransitionSlider() {
    const slider = document.getElementById('transition-slider');
    if (!slider) return;

    slider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        renderComparisonDiagram(value);
    });

    // Animate on first view
    const section = document.getElementById('insight');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    // Auto-animate slider once
                    let value = 0;
                    const interval = setInterval(() => {
                        value += 2;
                        if (value > 100) {
                            clearInterval(interval);
                            return;
                        }
                        slider.value = value;
                        renderComparisonDiagram(value);
                    }, 20);
                    observer.unobserve(section);
                }
            });
        },
        { threshold: 0.3 }
    );

    observer.observe(section);
}

// Mechanism Animation Button
function initMechanismAnimation() {
    const button = document.getElementById('animate-mechanism');
    if (!button) return;

    button.addEventListener('click', () => {
        animateMechanism();
    });

    // Auto-animate on first view
    const section = document.getElementById('how-it-works');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    setTimeout(() => animateMechanism(), 500);
                    observer.unobserve(section);
                }
            });
        },
        { threshold: 0.3 }
    );

    observer.observe(section);
}

// Block Number Slider
function initBlockSlider() {
    const slider = document.getElementById('num-blocks');
    const countDisplay = document.getElementById('block-count');
    if (!slider || !countDisplay) return;

    slider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        countDisplay.textContent = value;
        renderBlockDiagram(value);
    });
}

// Animate Results Bars
function initResultsAnimation() {
    const section = document.getElementById('results');
    const bars = document.querySelectorAll('.bar');

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    // Reset bars
                    bars.forEach((bar) => {
                        const originalWidth = bar.style.width;
                        bar.style.width = '0%';

                        // Animate to original width
                        setTimeout(() => {
                            bar.style.width = originalWidth;
                        }, 100);
                    });

                    observer.unobserve(section);
                }
            });
        },
        { threshold: 0.2 }
    );

    observer.observe(section);
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Handle window resize
function initResizeHandler() {
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            // Re-render all diagrams on resize
            initDiagrams();
        }, 250);
    });
}

// Initialize all interactive features
function initInteractive() {
    initThemeToggle();
    initScrollAnimations();
    initTransitionSlider();
    initMechanismAnimation();
    initBlockSlider();
    initResultsAnimation();
    initSmoothScroll();
    initResizeHandler();

    // Make sections visible on load (in case JS loads late)
    setTimeout(() => {
        const firstSection = document.querySelector('.section');
        if (firstSection && !firstSection.classList.contains('visible')) {
            firstSection.classList.add('visible');
        }
    }, 100);
}

// Run on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInteractive);
} else {
    initInteractive();
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Press 'D' to toggle dark mode
    if (e.key === 'd' || e.key === 'D') {
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            const toggle = document.querySelector('.theme-toggle');
            if (toggle) toggle.click();
        }
    }
});
