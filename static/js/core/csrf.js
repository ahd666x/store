const Csrf = {
    getToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    getHeader() {
        const token = this.getToken();
        return token ? { 'X-CSRFToken': token } : {};
    },

    getFormData(form) {
        if (!form) return null;
        const formData = new FormData(form);
        const token = this.getToken();
        if (token && !formData.has('csrfmiddlewaretoken')) {
            formData.append('csrfmiddlewaretoken', token);
        }
        return formData;
    }
};
