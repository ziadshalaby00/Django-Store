document.addEventListener('DOMContentLoaded', function() {
    const filterSection = document.getElementById('changelist-filter');
    
    if (filterSection) {
        const heading = filterSection.querySelector('h2');
        const filterList = filterSection.querySelector('ul');
        const mainContent = document.querySelector('#content-main');
        
        const toggleArrow = document.createElement('span');
        heading.appendChild(toggleArrow);
        
        const floatingToggle = document.createElement('div');
        floatingToggle.style.position = 'fixed';
        floatingToggle.style.right = '0';
        floatingToggle.style.top = '50%';
        floatingToggle.style.transform = 'translateY(-50%)';
        floatingToggle.style.background = '#79aec8';
        floatingToggle.style.color = 'white';
        floatingToggle.style.padding = '10px';
        floatingToggle.style.borderRadius = '5px 0 0 5px';
        floatingToggle.style.cursor = 'pointer';
        floatingToggle.style.zIndex = '1000';
        floatingToggle.style.boxShadow = '0 0 10px rgba(0,0,0,0.3)';
        document.body.appendChild(floatingToggle);
        
        let isCollapsed = localStorage.getItem('adminFiltersCollapsed') === 'true';

        function updateUI() {
            if (isCollapsed) {
                filterSection.style.display = 'none';
                mainContent.style.marginRight = '0';
                floatingToggle.textContent = '◀';
            } else {
                filterSection.style.display = 'block';
                mainContent.style.marginRight = '0';
                floatingToggle.textContent = '▶';
            }
        }

        updateUI();

        function toggleFilters() {
            isCollapsed = !isCollapsed;
            localStorage.setItem('adminFiltersCollapsed', isCollapsed);
            updateUI();
        }
        
        toggleArrow.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleFilters();
        });
        
        floatingToggle.addEventListener('click', toggleFilters);
        
        filterList.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});