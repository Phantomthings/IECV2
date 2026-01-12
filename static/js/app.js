document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const pageTitle = document.querySelector('.page-title');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const viewName = this.dataset.view;
            
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            views.forEach(view => view.classList.remove('active'));
            document.getElementById(`view-${viewName}`).classList.add('active');
            
            pageTitle.textContent = this.querySelector('.label').textContent;
        });
    });
    
    function updateTimestamp() {
        const now = new Date();
        const formatted = now.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('timestamp').textContent = formatted;
    }
    
    function updateTimestamp() {
        const now = new Date();
        const formatted = now.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('timestamp').textContent = formatted;
    }

    updateTimestamp();
    setInterval(updateTimestamp, 1000);
});