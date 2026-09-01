const OrderItem = {
    init() {
        const filterForm = document.getElementById('filter-form');
        if (!filterForm) return;

        const categorySelect = filterForm.querySelector('#id_category');
        const productSelect = filterForm.querySelector('#id_product');
        const colorSelect = filterForm.querySelector('#id_color');

        if (categorySelect && productSelect) {
            categorySelect.addEventListener('change', () => {
                const categoryId = categorySelect.value;
                if (!categoryId) {
                    productSelect.innerHTML = '<option value="">همه محصولات</option>';
                    return;
                }
                fetch(`/ajax/load-products/?category_id=${categoryId}`)
                    .then(r => r.json())
                    .then(data => {
                        productSelect.innerHTML = '<option value="">همه محصولات</option>' +
                            data.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
                    });
            });
        }

        if (productSelect && colorSelect) {
            productSelect.addEventListener('change', () => {
                const productId = productSelect.value;
                if (!productId) {
                    colorSelect.innerHTML = '<option value="">همه رنگ‌ها</option>';
                    return;
                }
                fetch(`/ajax/load-product-colors/?product_id=${productId}`)
                    .then(r => r.json())
                    .then(data => {
                        colorSelect.innerHTML = '<option value="">همه رنگ‌ها</option>' +
                            data.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
                    });
            });
        }
    }
};


