const Loading = {
    show() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.add('show');
    },

    hide() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.remove('show');
    },

    withPromise(asyncFn) {
        this.show();
        try {
            return await asyncFn();
        } finally {
            this.hide();
        }
    }
};
