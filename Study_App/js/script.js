document.addEventListener("DOMContentLoaded", function() {
    //navigation history for back button
    let navigationHistory = ['dashboard'];

    //back button functionality
    const backButton = document.getElementById('back-button');
    backButton.addEventListener('click', function() {
        if (navigationHistory.length > 1) {
            //remove current page from history
            navigationHistory.pop();
            //go to previous page
            const previousPage = navigationHistory[navigationHistory.length - 1];
            setActiveSection(previousPage);
        }
    });

    //sidebar nav
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.querySelector('.menu-toggle');
    const navItems = document.querySelectorAll('nav-item');
    const contentSections  = document.querySelectorAll('.content-section');

    //toggle sidebar
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        menuToggle.classList.toggle('sidebar-open');
    });

    //initial setup - sidebar hidden
    sidebar.classList.remove('active');
    menuToggle.classList.remove('sidebar-open');

    //initialise active section
    function setActiveSection(sectionId) {
        //add to navigation history if its a new section
        if (navigationHistory[navigationHistory.length - 1] !== sectionId) {
            navigationHistory.push(sectionId);
        }

        //show/hide back button (dont show on dashboard)
        if (sectionId === 'dashboard') {
            backButton.style.display = 'none';
        } else {
            backButton.style.display = 'flex';
        }

        //hide all sections
        contentSections.forEach(section => {
            section.classList.remove('active');
        });

        //show selected section
        document.getElementById(sectionId).classList.add('active');

        //update active nav item
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-section') === sectionId) {
                item.classList.add('active');
            }
        });

        //close sidebar on mobile after selection
        if (window.innerWidth < 768) {
            sidebar.classList.remove('active');
            menuToggle.classList.remove('sidebar-open');
        }

        //initialise charts if stats section is active
        if (sectionId === 'stats') {
            initCharts();
        }

        //load flashcards if flashcards section is active
        if (sectionId === 'flashcards') {
            loadFlashcards();
        }
    }

    //nav item click event
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            setActiveSection(sectionId)
        });
    });

    //start studying button
    const startStudyingBtn = document.getElementById('start-studying-btn');
    if (startStudyingBtn) {
        startStudyingBtn.addEventListener('click', function() {
            setActiveSection('study');
        });
    }

    //view all flashcards button
    const viewAllFlashcardsBtn = document.getElementById('view-all-flashcards');
    if (viewAllFlashcardsBtn) {
        viewAllFlashcardsBtn.addEventListener('click', function() {
            setActiveSection('flashcards');
        });
    }

    //view all flashcards button in flashcards section
    const viewAllCardsBtn = document.getElementById('view-all-cards-btn');
    if (viewAllCardsBtn) {
        viewAllCardsBtn.addEventListener('click', function() {
            //show all flashcards (if you had filtering, this would remove filters)
            alert("Showing all flashcards");
        });
    }

    //quick action buttons
    const quickCreateFlashcard = document.getElementById('quick-create-flashcard');
    const quickStudy = document.getElementById('quick-study');
    const quickStats = document.getElementById('quick-stats');
    const quickTetris = document.getElementById('quick-tetris');

    if (quickCreateFlashcard) {
        quickCreateFlashcard.addEventListener('click', function() {
            document.getElementById('create-flashcard-btn').click();
        });
    }

    if (quickStudy) {
        quickStudy.addEventListener('click', function() {
            setActiveSection('study');
        });
    }

    if (quickStats) {
        quickStats.addEventListener('click', function() {
            setActiveSection('stats');
        });
    }

    if (quickTetris) {
        quickTetris.addEventListener('click', function() {
            setActiveSection('tetris');
            document.getElementById('open-tetris').click();
        });
    }

    //study option buttons
    const studyOptionButtons = document.querySelectorAll('.study-option-btn');
    studyOptionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mode = this.getAttribute('data-mode');
            alert(`Starting ${mode.replace('-', ' ')}`)
            //add to recent activity
            addRecentActivity(`Started ${mode.replace('-', ' ')} session`, 'study');
            //study mode logic here
        });
    });

    //initialise charts
    function initCharts() {
        //study time chart
        const studyTimeCtx = document.getElementById('study-time-chart');
        if (studyTimeCtx) {
            new Chart(studyTimeCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Study Time (hours)',
                        data: [1.5, 2, 0.5, 1.2, 2.5, 0, 1],
                        backgroundColor: '#4a90e2',
                        borderColor: '#3a70b2',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        //category chart
        const categoryCtx = document.getElementById('category-chart');
        if (categoryCtx) {
            new Chart(categoryCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Math', 'Science', 'History', 'Language', 'General'],
                    datasets: [{
                        data: [8, 6, 4, 5, 2],
                        backgroundColor: [
                            '#ff6b8b',
                            '#4a90e2',
                            '#ff9500',
                            '#4cd964',
                            '#8e44ad'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        }
        
        //mastery chart
        const masteryCtx = document.getElementById('mastery-chart');
        if (masteryCtx) {
            new Chart(masteryCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Mastery Progress (%)',
                        data: [25, 45, 60, 72],
                        fill: false,
                        borderColor: '#ff6b8b',
                        tension: 0.1
                    }]
                },
                options: {
                    reponsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }   

    //initialise charts when stats section is activated
    const statsSection = document.getElementById('stats');
    if (statsSection && statsSection.classList.contains('active')) {
        initCharts();
    }

    //initialise study streak
    function updateStreak() {
        const lastStudyDate = localStorage.getItem('lastStudyDate');
        const currentDate = new Date().toDateString();
        const streakCount = parseInt(localStorage.getItem('studyStreak')) || 0;

        if (lastStudyDate != currentDate) {
            //check if last study date was yesterday
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);

            if (lastStudyDate === yesterday.toDateString() || !lastStudyDate) {
                const newStreak = lastStudyDate ? streakCount + 1  : 1;
                localStorage.setItem('studyStreak', newStreak);
                localStorage.setItem('lastStudyDate', currentDate);

                document.querySelector('.streak-days').textContent = `${newStreak} days`;
            } else {
                //reset streak if missed a day
                localStorage.setItem('studyStreak', 1);
                localStorage.setItem('lastStudyDate', currentDate);
                document.querySelector('.streak-days').textContent = '1 day';
            }
        } else {
            document.querySelector('.streak-days').textContent = `${streakCount} days`;
        }
    }

    updateStreak();

    //close modal when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    //close modal with escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.classList.remove('active');
            });
            document.getElementById('flashcard-creator').classList.remove('active');
        }
    });


    //quick action buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.textContent.trim();
            if (text.includes('Create Flashcards')) {
                document.getElementById('create-flashcard-btn').click();
            } else if (text.includes('Quick Review')) {
                setActiveSection('study');
            } else if (text.includes('View Stats')) {
                setActiveSection('stats')
            } else if (text.includes('Play Tetris')) {
                setActiveSection('tetris')
                document.getElementById('open-tetris').click();
            } else if (text.includes('View All Flashcards')) {
                setActiveSection('flashcards');
            }
        });
    });

    //recent activity function
    function addRecentActivity(text, type = 'general') {
        const activityList = document.getElementById('activity-list');
        const now = new Date();
        const timeString = getTimeAgo(now);

        let icon = 'fas fa-check';
        if (type == 'create') icon = 'fas fa-plus';
        else if (type === 'study') icon = 'fas fa-book';
        else if (type === 'game') icon = 'fas fa-gamepad';
        else if (type === 'stats') icon = 'fas fa-chart-line';

        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon"><i class="${icon}"></i></div>
            <div class="activyt-details"><p>${text}</p><span>${timeString}</span></div>    
        `;

        //add to top of list
        activityList.insertBefore(activityItem, activityList.firstChild);

        //limit to 10 activities
        if (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }

    function getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3660)} hours ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        return `${Math.floor(diffInSeconds / 2592000)} months ago`;
    }
});