const Toast = {
    show(message, type) {
        type = type || 'success';
        const container = document.querySelector('[data-toast-container]');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'pointer-events-auto flex items-start gap-3 p-4 rounded-lg shadow-elevation-3 border max-w-sm';
        toast.setAttribute('data-toast', type);

        const colors = {
            success: 'bg-success-50 border-success-200 text-success-800',
            error: 'bg-danger-50 border-danger-200 text-danger-800',
            warning: 'bg-warning-50 border-warning-200 text-warning-800',
            info: 'bg-info-50 border-info-200 text-info-800'
        };
        toast.classList.add(...(colors[type] || colors.info).split(' '));

        const icons = {
            success: '<svg class="w-5 h-5 text-success-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
            error: '<svg class="w-5 h-5 text-danger-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
            warning: '<svg class="w-5 h-5 text-warning-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
            info: '<svg class="w-5 h-5 text-info-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
        };

        toast.innerHTML = `${icons[type] || icons.info}<div class="flex-1 text-sm">${message}</div><button class="flex-shrink-0 text-stone-400 hover:text-stone-600" aria-label="بستن" data-toast-close><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>`;

        container.appendChild(toast);

        const closeBtn = toast.querySelector('[data-toast-close]');
        const remove = () => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(4px)';
            toast.style.transition = 'all 0.2s ease';
            setTimeout(() => toast.remove(), 200);
        };
        closeBtn.addEventListener('click', remove);
        setTimeout(remove, 5000);
    }
};
