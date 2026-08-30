document.addEventListener('alpine:init', () => {
    Alpine.data('navbar', () => ({
        open: false,
        toggle() {
            this.open = !this.open
        },
        close() {
            this.open = false
        }
    }))

    Alpine.data('modal', () => ({
        id: '',
        titleId: '',
        open: false,
        show() {
            this.open = true
            this.$nextTick(() => {
                const root = document.getElementById(this.id)
                if (!root) return
                const focusable = root.querySelector('[autofocus], button, [href], input, select, textarea')
                if (focusable) focusable.focus()
            })
        },
        hide() {
            this.open = false
        },
        toggle() {
            this.open = !this.open
        }
    }))

    Alpine.data('dropdown', () => ({
        open: false,
        toggle() {
            this.open = !this.open
        },
        close() {
            this.open = false
        }
    }))

    Alpine.data('alert', () => ({
        visible: true,
        hide() {
            this.visible = false
        }
    }))

    Alpine.data('toast', () => ({
        visible: false,
        message: '',
        show(message) {
            this.message = message
            this.visible = true
        },
        hide() {
            this.visible = false
        }
    }))

    document.addEventListener('click', (e) => {
        if (!e.target.closest('[x-data*="dropdown"]')) {
            document.querySelectorAll('[x-data*="dropdown"]').forEach(el => {
                if (el.__x) el.__x.$data.open = false
            })
        }
    })
})
