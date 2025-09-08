document.addEventListener('DOMContentLoaded', function() {
    const filterSection = document.getElementById('changelist-filter');
    
    if (filterSection) {
        const heading = filterSection.querySelector('h2');
        const filterList = filterSection.querySelector('ul');
        const mainContent = document.querySelector('#content-main');
        
        // إضافة زر التبديل مع سهم
        const toggleArrow = document.createElement('span');
        heading.appendChild(toggleArrow);
        
        // إضافة زر منفصل في الزاوية
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
        
        // حالة الطي (false = مفتوح, true = مطوي)
        let isCollapsed = localStorage.getItem('adminFiltersCollapsed') === 'true';

        // وظيفة تحديث العرض بناءً على الحالة
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

        // تطبيق الحالة المحفوظة عند التحميل
        updateUI();

        // وظيفة طي/فتح الـ filters
        function toggleFilters() {
            isCollapsed = !isCollapsed;
            localStorage.setItem('adminFiltersCollapsed', isCollapsed);
            updateUI();
        }
        
        // إضافة event listeners
        toggleArrow.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleFilters();
        });
        
        floatingToggle.addEventListener('click', toggleFilters);
        
        // منع طي الـ filters عند النقر على العناصر داخلها
        filterList.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});