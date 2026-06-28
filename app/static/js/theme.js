/* StockMate - Theme and Sidebar Toggle Script */

(function() {
    // 1. Immediate theme state execution to avoid page flash
    const savedTheme = localStorage.getItem('sm-theme') || 'dark';
    if (savedTheme === 'light') {
        document.documentElement.classList.add('light-theme');
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.add('light-theme');
        });
    }

    // Immediate sidebar state check
    const savedSidebar = localStorage.getItem('sm-sidebar') || 'expanded';
    if (savedSidebar === 'collapsed') {
        document.addEventListener('DOMContentLoaded', () => {
            const sidebar = document.querySelector('.sidebar');
            const wrapper = document.querySelector('.main-wrapper');
            if (sidebar) sidebar.classList.add('collapsed');
            if (wrapper) wrapper.classList.add('full-screen');
        });
    }

    // 2. Setup Navbar control buttons dynamically on page load
    document.addEventListener('DOMContentLoaded', () => {
        const navbar = document.querySelector('.navbar-top');
        if (!navbar) return;

        // Find or build right controls container
        let rightContainer = navbar.querySelector('.d-flex.align-items-center');
        if (!rightContainer) {
            rightContainer = document.createElement('div');
            rightContainer.className = 'd-flex align-items-center gap-3';
            navbar.appendChild(rightContainer);
        }

        // Add Toggle Sidebar button (Burger menu) at the far left
        if (!document.getElementById('sidebarToggle')) {
            const toggleSidebarBtn = document.createElement('button');
            toggleSidebarBtn.id = 'sidebarToggle';
            toggleSidebarBtn.className = 'btn btn-outline-light me-3';
            toggleSidebarBtn.innerHTML = '<i class="bi bi-list fs-5"></i>';
            toggleSidebarBtn.type = 'button';
            
            // Insert at the absolute beginning of header
            navbar.insertBefore(toggleSidebarBtn, navbar.firstChild);

            toggleSidebarBtn.addEventListener('click', () => {
                const sidebar = document.querySelector('.sidebar');
                const wrapper = document.querySelector('.main-wrapper');
                if (sidebar && wrapper) {
                    sidebar.classList.toggle('collapsed');
                    wrapper.classList.toggle('full-screen');
                    const isCollapsed = sidebar.classList.contains('collapsed');
                    localStorage.setItem('sm-sidebar', isCollapsed ? 'collapsed' : 'expanded');
                }
            });
        }

        // Add Theme Toggle button (Sun/Moon) to the right navbar section
        if (!document.getElementById('themeToggle')) {
            const themeBtn = document.createElement('button');
            themeBtn.id = 'themeToggle';
            themeBtn.className = 'btn btn-outline-light me-2';
            
            const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
            themeBtn.innerHTML = currentTheme === 'light' ? '<i class="bi bi-moon-fill fs-5"></i>' : '<i class="bi bi-sun-fill fs-5"></i>';
            themeBtn.type = 'button';

            // Insert before details
            rightContainer.insertBefore(themeBtn, rightContainer.firstChild);

            themeBtn.addEventListener('click', () => {
                const isLight = document.body.classList.toggle('light-theme');
                document.documentElement.classList.toggle('light-theme', isLight);
                localStorage.setItem('sm-theme', isLight ? 'light' : 'dark');
                themeBtn.innerHTML = isLight ? '<i class="bi bi-moon-fill fs-5"></i>' : '<i class="bi bi-sun-fill fs-5"></i>';
            });
        }
    });

    // 3. Prevent back-forward cache restoration (bfcache) to force re-authentication check
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            window.location.reload();
        }
    });
})();
