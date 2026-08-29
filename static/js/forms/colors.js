const ColorFields = {
    update(defaults) {
        const allowedParts = Object.keys(defaults);
        document.querySelectorAll('.color-field').forEach(el => {
            const part = el.getAttribute('data-part');
            if (allowedParts.includes(part)) {
                el.style.display = '';
                const select = el.querySelector('select');
                if (select && defaults[part]) {
                    select.value = defaults[part];
                } else if (select) {
                    select.value = '';
                }
            } else {
                el.style.display = 'none';
                const select = el.querySelector('select');
                if (select) select.value = '';
            }
        });
    },

    reset() {
        document.querySelectorAll('.color-field').forEach(el => {
            el.style.display = '';
            const select = el.querySelector('select');
            if (select) select.value = '';
        });
    },

    init() {
        const configs = window.ColorFieldsConfig || [];
        configs.forEach(cfg => {
            const productEl = document.querySelector(cfg.productSelector);
            if (!productEl) return;

            const loadColors = async (productId) => {
                if (!productId) {
                    ColorFields.reset();
                    return;
                }
                try {
                    const response = await fetch(`${cfg.url.replace('0', productId)}/`);
                    const data = await response.json();
                    ColorFields.update(data.defaults);
                } catch (error) {
                    console.error('خطا در بارگذاری رنگ‌ها:', error);
                }
            };

            productEl.addEventListener('change', () => {
                loadColors(productEl.value);
            });

            if (cfg.initialProduct) {
                loadColors(cfg.initialProduct);
            }
        });
    }
};
