const CascadeSelect = {
    init() {
        const configs = window.CascadeConfig || [];
        configs.forEach(cfg => {
            const categoryEl = document.querySelector(cfg.categorySelector);
            const productEl = document.querySelector(cfg.productSelector);
            if (!categoryEl || !productEl) return;

            const loadProducts = async (categoryId) => {
                if (!categoryId) {
                    productEl.innerHTML = '<option value="">---------</option>';
                    if (cfg.onSubmit) {
                        const form = categoryEl.closest('form');
                        if (form) form.submit();
                    }
                    return;
                }
                try {
                    const response = await fetch(`${cfg.url}?category=${categoryId}`);
                    const data = await response.json();
                    productEl.innerHTML = '<option value="">---------</option>';
                    data.forEach(product => {
                        const option = document.createElement('option');
                        option.value = product.id;
                        option.textContent = product.name;
                        productEl.appendChild(option);
                    });
                    if (cfg.initialProduct) productEl.value = cfg.initialProduct;
                    if (cfg.onSubmit) {
                        const form = categoryEl.closest('form');
                        if (form) form.submit();
                    }
                } catch (error) {
                    console.error('خطا در بارگذاری محصولات:', error);
                }
            };

            categoryEl.addEventListener('change', () => {
                loadProducts(categoryEl.value);
            });

            if (categoryEl.value) {
                loadProducts(categoryEl.value);
            }
        });
    }
};
