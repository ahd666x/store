const Catalog = {
    initPriceCalc() {
        document.querySelectorAll('[data-price-calc]').forEach(form => {
            const basePrice = parseFloat(form.dataset.basePrice) || 0;
            const lengthPercent = parseFloat(form.dataset.lengthPercent) || 0;
            const widthPercent = parseFloat(form.dataset.widthPercent) || 0;
            const heightPercent = parseFloat(form.dataset.heightPercent) || 0;
            const defaults = {
                length: form.dataset.defaultLength ? parseFloat(form.dataset.defaultLength) : null,
                width: form.dataset.defaultWidth ? parseFloat(form.dataset.defaultWidth) : null,
                height: form.dataset.defaultHeight ? parseFloat(form.dataset.defaultHeight) : null,
            };
            const inputs = {
                length: form.querySelector('[data-dim="length"]'),
                width: form.querySelector('[data-dim="width"]'),
                height: form.querySelector('[data-dim="height"]'),
            };
            const priceEl = form.querySelector('[data-live-price]');
            if (!priceEl) return;

            const diff = (customVal, defaultVal) => {
                if (defaultVal === null || defaultVal === undefined) return 0;
                if (customVal === null || customVal === undefined || customVal === '') return 0;
                const parsed = parseFloat(customVal);
                if (isNaN(parsed)) return 0;
                return parsed - defaultVal;
            };

            const recalc = () => {
                try {
                    let diffs = 0;
                    if (inputs.length && !inputs.length.disabled) {
                        diffs += diff(inputs.length.value, defaults.length) * lengthPercent;
                    }
                    if (inputs.width && !inputs.width.disabled) {
                        diffs += diff(inputs.width.value, defaults.width) * widthPercent;
                    }
                    if (inputs.height && !inputs.height.disabled) {
                        diffs += diff(inputs.height.value, defaults.height) * heightPercent;
                    }
                    const priceIncrease = basePrice * (diffs / 100);
                    const finalPrice = Math.round(basePrice + priceIncrease);
                    priceEl.textContent = finalPrice.toLocaleString('fa-IR') + ' تومان';
                } catch (e) {
                    // silently handle
                }
            };

            Object.values(inputs).forEach(input => {
                if (input) input.addEventListener('input', recalc);
            });
            recalc();
        });
    },

    initFilters() {
        const applyFilters = () => {
            const search = document.getElementById('searchInput')?.value || document.getElementById('mobileSearchInput')?.value || '';
            const category = document.getElementById('categoryFilter')?.value || document.getElementById('mobileCategoryFilter')?.value || '';
            const sort = document.getElementById('sortFilter')?.value || document.getElementById('mobileSortFilter')?.value || '';
            const color = document.getElementById('colorFilter')?.value || document.getElementById('mobileColorFilter')?.value || '';
            const minPrice = document.getElementById('minPrice')?.value || document.getElementById('mobileMinPrice')?.value || '';
            const maxPrice = document.getElementById('maxPrice')?.value || document.getElementById('mobileMaxPrice')?.value || '';

            const url = new URL(window.location);
            if (search) url.searchParams.set('q', search);
            if (category) url.searchParams.set('category', category);
            if (sort) url.searchParams.set('sort', sort);
            if (color) url.searchParams.set('color', color);
            if (minPrice) url.searchParams.set('min_price', minPrice);
            if (maxPrice) url.searchParams.set('max_price', maxPrice);
            url.searchParams.set('page', '1');
            window.location = url.toString();
        };

        document.querySelectorAll('[data-filter-apply]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                applyFilters();
            });
        });

        const resetFilters = () => {
            window.location = '{% url "catalog:product_list" %}';
        };

        document.querySelectorAll('[data-filter-reset]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                resetFilters();
            });
        });
    },

    initClickableRows() {
        document.querySelectorAll('[data-href]').forEach(row => {
            row.addEventListener('click', (e) => {
                if (e.target.closest('a, button, input[type="checkbox"]')) return;
                const url = row.dataset.href;
                if (url) window.location.href = url;
            });
        });
    }
};
