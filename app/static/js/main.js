document.addEventListener('DOMContentLoaded', () => {
    const langToggleBtn = document.getElementById('lang-toggle');
    const htmlElement = document.documentElement;
    const bodyElement = document.body;

    // Check saved preference
    const currentLang = localStorage.getItem('vines_lang') || 'en';
    setLanguage(currentLang);

    if (langToggleBtn) {
        langToggleBtn.addEventListener('click', () => {
            const newLang = htmlElement.lang === 'en' ? 'ar' : 'en';
            setLanguage(newLang);
        });
    }

    function setLanguage(lang) {
        htmlElement.lang = lang;
        if (lang === 'ar') {
            htmlElement.dir = 'rtl';
            bodyElement.classList.add('rtl');
            if (langToggleBtn) langToggleBtn.textContent = 'EN';
        } else {
            htmlElement.dir = 'ltr';
            bodyElement.classList.remove('rtl');
            if (langToggleBtn) langToggleBtn.textContent = 'AR';
        }
        localStorage.setItem('vines_lang', lang);
    }

    /* Hero Slider Logic */
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.slide-dot');
    const prevBtn = document.getElementById('left-arrow');
    const nextBtn = document.getElementById('right-arrow');
    let currentSlide = 0;
    const slideIntervalTime = 5000;
    let slideInterval;

    function initSlider() {
        if (!slides.length) {
            console.warn('No slides found. Slider not initialized.');
            return;
        }

        // Show first slide immediately
        showSlide(currentSlide);

        // Start Auto Play
        startSlideInterval();

        // Event Listeners for Controls
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (isRTL()) {
                    nextSlide(); // in RTL, left arrow goes "next" (forward in visual sequence?) No, usually left is "back".
                    // Wait, user requirement: "In Arabic mode (dir="rtl"), the "Next" arrow goes left, "Previous" goes right."
                    // This implies the Left Arrow is "Next" button in RTL.
                    // My previous code: Left Arrow click -> if RTL -> nextSlide(). This creates "Next" behavior on Left Arrow. Correct.
                    nextSlide();
                } else {
                    prevSlide();
                }
                resetSlideInterval();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (isRTL()) {
                    prevSlide(); // Right arrow becomes Previous
                } else {
                    nextSlide();
                }
                resetSlideInterval();
            });
        }

        // Dot Navigation
        dots.forEach(dot => {
            dot.addEventListener('click', () => {
                const index = parseInt(dot.getAttribute('data-index'));
                currentSlide = index;
                showSlide(currentSlide);
                resetSlideInterval();
            });
        });
    }

    function showSlide(index) {
        // Wrap around logic
        if (index >= slides.length) {
            currentSlide = 0;
        } else if (index < 0) {
            currentSlide = slides.length - 1;
        } else {
            currentSlide = index;
        }

        // Update Slides State
        slides.forEach((slide, i) => {
            const content = slide.querySelector('.slide-content');

            // Explicitly remove classes first to ensure clean state
            slide.classList.remove('active', 'opacity-100', 'z-10', 'opacity-0', 'z-0');

            if (i === currentSlide) {
                slide.classList.add('active', 'opacity-100', 'z-10');
                if (content) {
                    content.classList.remove('animate-fade-in-up'); // reset animation
                    void content.offsetWidth; // trigger reflow
                    content.classList.add('animate-fade-in-up');
                }
            } else {
                slide.classList.add('opacity-0', 'z-0');
                if (content) content.classList.remove('animate-fade-in-up');
            }
        });

        // Update Dots
        dots.forEach((dot, i) => {
            if (i === currentSlide) {
                dot.classList.add('w-8', 'bg-white');
                dot.classList.remove('bg-white/50');
            } else {
                dot.classList.remove('w-8', 'bg-white');
                dot.classList.add('bg-white/50');
            }
        });
    }

    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    function prevSlide() {
        showSlide(currentSlide - 1);
    }

    function startSlideInterval() {
        if (slideInterval) clearInterval(slideInterval); // Ensure no duplicate intervals
        slideInterval = setInterval(() => {
            nextSlide();
        }, slideIntervalTime);
    }

    function resetSlideInterval() {
        clearInterval(slideInterval);
        startSlideInterval();
    }

    function isRTL() {
        return htmlElement.dir === 'rtl';
    }

    // Initialize Slider
    initSlider();

    // --- Product Modal Logic ---
    window.openProductModal = function (data) {
        const modal = document.getElementById('product-modal');
        const backdrop = document.getElementById('modal-backdrop');
        const panel = document.getElementById('modal-panel');

        if (!modal) return;

        // Populate Data
        document.getElementById('modal-image').src = data.image;
        document.getElementById('modal-code-badge').textContent = data.code;

        document.getElementById('modal-title-en').textContent = data.name_en;
        document.getElementById('modal-title-ar').textContent = data.name_ar;

        document.getElementById('modal-category-en').textContent = data.category_en;
        document.getElementById('modal-category-ar').textContent = data.category_ar;

        document.getElementById('modal-code').textContent = data.code;
        document.getElementById('modal-weight').textContent = data.weight;

        document.getElementById('modal-desc-en').textContent = data.description_en;
        document.getElementById('modal-desc-ar').textContent = data.description_ar;

        // Show Modal
        modal.classList.remove('hidden');

        // Disable Body Scroll
        document.body.style.overflow = 'hidden';

        // Animate In (Small delay to allow display:block to apply)
        setTimeout(() => {
            backdrop.classList.remove('opacity-0');
            panel.classList.remove('opacity-0', 'translate-y-4', 'scale-95');
            panel.classList.add('opacity-100', 'translate-y-0', 'scale-100');
        }, 10);
    };

    window.closeProductModal = function () {
        const modal = document.getElementById('product-modal');
        const backdrop = document.getElementById('modal-backdrop');
        const panel = document.getElementById('modal-panel');

        if (!modal) return;

        // Animate Out
        backdrop.classList.add('opacity-0');
        panel.classList.remove('opacity-100', 'translate-y-0', 'scale-100');
        panel.classList.add('opacity-0', 'translate-y-4', 'scale-95');

        // Hide after animation
        setTimeout(() => {
            modal.classList.add('hidden');
            document.body.style.overflow = ''; // Restore scroll
            // Clear Src to avoid old image flashing next time
            document.getElementById('modal-image').src = '';
        }, 300); // Match transition duration
    };

    // Close on Backdrop Click
    const modalBackdrop = document.getElementById('modal-backdrop');
    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', window.closeProductModal);
    }

    // Close on Escape Key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.closeProductModal();
        }
    });

});
