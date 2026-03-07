// Modern Portfolio JavaScript

// Utility Functions
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Hide loading screen first
    hideLoadingScreen();
    // Then initialize portfolio
    setTimeout(() => {
        initializePortfolio();
    }, 100);
});

// Hide Loading Screen
function hideLoadingScreen() {
    const loadingScreen = $('#loading-screen');
    if (loadingScreen) {
        // Add fade out animation
        loadingScreen.style.opacity = '0';
        loadingScreen.style.transition = 'opacity 0.5s ease-out';
        
        // Remove loading screen after animation
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }
}

// Initialize Portfolio
function initializePortfolio() {
    setupNavigation();
    setupScrollEffects();
    setupAnimations();
    setupFormHandling();
    setupThemeToggle();
    setupParticles();
}

// Navigation Setup
function setupNavigation() {
    const navbar = $('#navbar');
    const navToggle = $('#nav-toggle');
    const navMenu = $('#nav-menu');
    const navLinks = $$('.nav-link');

    // Mobile menu toggle
    navToggle?.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Close mobile menu when clicking on links
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Active navigation highlighting
    const sections = $$('section');
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '-100px 0px -100px 0px'
    };

    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('data-section') === sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        navObserver.observe(section);
    });
}

// Scroll Effects
function setupScrollEffects() {
    // Smooth scrolling for anchor links
    $$('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = $(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 70;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroSection = $('#home');
        if (heroSection) {
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        }
    });
}

// Animations
function setupAnimations() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);

    // Observe elements with animation classes
    $$('.fade-in, .slide-up, .slide-left, .slide-right').forEach(el => {
        observer.observe(el);
    });

    // Typewriter effect
    setupTypewriter();
}

// Typewriter Effect
function setupTypewriter() {
    const typewriterElement = $('.typewriter');
    if (!typewriterElement) return;

    const texts = ['Software Developer', 'Problem Solver', 'Creative Thinker', 'Team Player'];
    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typingSpeed = 100;
    const deletingSpeed = 50;
    const pauseTime = 2000;

    function type() {
        const currentText = texts[textIndex];
        
        if (isDeleting) {
            typewriterElement.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typewriterElement.textContent = currentText.substring(0, charIndex + 1);
            charIndex++;
        }

        let speed = isDeleting ? deletingSpeed : typingSpeed;

        if (!isDeleting && charIndex === currentText.length) {
            speed = pauseTime;
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            textIndex = (textIndex + 1) % texts.length;
        }

        setTimeout(type, speed);
    }

    type();
}

// Form Handling
function setupFormHandling() {
    const contactForm = $('#contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Show success message
            showNotification('Message sent successfully!', 'success');
            
            // Reset form
            this.reset();
        });
    }
}

// Theme Toggle
function setupThemeToggle() {
    const themeToggle = $('#theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
        }
    }
}

// Particles Setup
function setupParticles() {
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            particles: {
                number: { value: 80 },
                color: { value: '#00d4ff' },
                shape: { type: 'circle' },
                opacity: { value: 0.5 },
                size: { value: 3 },
                move: {
                    enable: true,
                    speed: 2,
                    direction: 'none',
                    random: false,
                    straight: false,
                    out_mode: 'out',
                    bounce: false
                }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: { enable: true, mode: 'repulse' },
                    onclick: { enable: true, mode: 'push' },
                    resize: true
                }
            },
            retina_detect: true
        });
    }
}

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Window Load Event (fallback for loading screen)
window.addEventListener('load', function() {
    // Ensure loading screen is hidden even if DOMContentLoaded didn't fire properly
    setTimeout(() => {
        const loadingScreen = $('#loading-screen');
        if (loadingScreen && loadingScreen.style.display !== 'none') {
            hideLoadingScreen();
        }
    }, 1000);
});