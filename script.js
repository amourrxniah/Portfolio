document.addEventListener('DOMContentLoaded', () => {
    //scroll animations using AOS
    AOS.init({
        duration: 1000, //animation speed
        offset: 200, //start animation when scrolling
    });

    //typewriter logic
    const typewriterElements = document.querySelectorAll('.typewriter');
    let delay = 0;

    typewriterElements.forEach((el) => {
        const text = el.dataset.text;
        el.textContent = '';
        let index = 0;

        //span element to wrap text being typed
        const typingSpan = document.createElement('span');
        el.appendChild(typingSpan);

        function typeChar() {
            if (index < text.length) {
                typingSpan.textContent += text.charAt(index);
                index++;
                setTimeout(typeChar, 70); //adjust typing speed
            } else {
                //when typing finished, stop animation
                typingSpan.classList.add('finished');

                //add slight delay before removing
                setTimeout(() => {
                    typingSpan.classList.remove('typing');
                    typingSpan.style.borderRight = 'none';
                })
            }
        }

        //start typing effect and add 'typing' class
        typingSpan.classList.add('typing');
        typeChar();
    });

    //animate skill chart with specific colours
    const skillColors = {
        "Communication": "#5a67d8",
        "Teamwork": "#48bb78",
        "Problem Solving": "#ed64a6",
        "Creativity": "#4299e1"
    };

    const skillElements = document.querySelectorAll('.skill');

    function animateSkills() {
        skillElements.forEach(skill => {
            const percent = parseInt(skill.getAttribute('data-percent'));
            const skillName = skill.getAttribute('data-skill');
            const color = skillColors[skillName] || 'var(--primary-color)';
    
            //animate gradient
            let current = 0;
            const speed = 10;
            const increment = 1;

            //start with hidden + scaled
            skill.style.opacity = '0';
            skill.style.transition = 'scale(0.8)';
            setTimeout(() => {
                skill.style.transition = 'transform 1s ease, opacity 1s ease';
                skill.style.opacity = '1';
                skill.style.transform = 'scale(1)';
            }, 100);
    
            function fill() {
                if (current <= percent) {
                    skill.style.background = `conic-gradient(${color} 0% ${current}%, #e2e8f0 ${current}% 100%)`;
                    current += increment;
                    requestAnimationFrame(fill);
                }
            };
            fill();
        });
        hasAnimated = true;
    };

    //trigger animation on scroll into view
    const skillsSection = document.querySelector('.skills-chart');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateSkills();
            }
        });
    }, {
        threshold: 0.5
    });

    if (skillsSection) observer.observe(skillsSection);
});

