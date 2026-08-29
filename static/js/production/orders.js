const Orders = {
    init() {
        const selectAllCheckbox = document.getElementById('select-all');
        const orderCheckboxes = document.querySelectorAll('.order-checkbox');
        const batchExportBtn = document.getElementById('batch-export-btn');
        const selectedCountSpan = document.getElementById('selected-count');

        if (!selectAllCheckbox || !orderCheckboxes.length) return;

        const updateSelectedCount = () => {
            const checkedBoxes = document.querySelectorAll('.order-checkbox:checked');
            const count = checkedBoxes.length;
            if (selectedCountSpan) selectedCountSpan.textContent = count + ' سفارش انتخاب شده';
            if (batchExportBtn) batchExportBtn.disabled = count === 0;
        };

        selectAllCheckbox.addEventListener('change', function(e) {
            orderCheckboxes.forEach(cb => cb.checked = e.target.checked);
            updateSelectedCount();
        });

        orderCheckboxes.forEach(cb => {
            cb.addEventListener('change', updateSelectedCount);
            cb.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });

        updateSelectedCount();

        document.querySelectorAll('.generate-tasks').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const url = this.dataset.url;
                if (confirm('آیا مطمئنید که می‌خواهید دستور تولید صادر شود؟')) {
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('خطا: ' + (data.error || 'نامشخص'));
                        }
                    })
                    .catch(err => alert('خطای شبکه'));
                }
            });
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Orders.init());
} else {
    Orders.init();
}
