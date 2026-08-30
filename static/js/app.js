const App = {
    init() {
        Cart.init();
        Catalog.initPriceCalc();
        Catalog.initFilters();
        Catalog.initClickableRows();
        Scanner.init();
        Kanban.init();
        Orders.init();
        OrderItem.init();

        const hasWorkersTable = document.getElementById('workerTableBody');
        if (hasWorkersTable && typeof WORKERS_BASE !== 'undefined') {
            Workers.init();
        }

        CascadeSelect.init();
        ColorFields.init();

        document.querySelectorAll('.size-rule-preset').forEach(select => {
            const customInput = select.parentElement.querySelector('.size-rule-custom');
            const hiddenInput = select.parentElement.querySelector('.size-rule-hidden');
            if (!customInput || !hiddenInput) return;

            const syncRuleField = () => {
                const presetVal = select.value;
                if (!presetVal) {
                    select.style.display = '';
                    customInput.style.display = 'none';
                    hiddenInput.value = '';
                    return;
                }
                if (presetVal === 'custom') {
                    select.style.display = 'none';
                    customInput.style.display = '';
                    hiddenInput.value = customInput.value;
                } else {
                    select.style.display = '';
                    customInput.style.display = 'none';
                    hiddenInput.value = presetVal;
                }
            };

            select.addEventListener('change', syncRuleField);
            customInput.addEventListener('input', () => {
                if (select.value === 'custom') {
                    hiddenInput.value = customInput.value;
                }
            });

            if (hiddenInput.value && select.options.length) {
                const options = Array.from(select.options);
                const matched = options.find(opt => opt.value === hiddenInput.value);
                if (matched) {
                    select.value = hiddenInput.value;
                } else {
                    select.value = 'custom';
                    customInput.value = hiddenInput.value;
                }
            }
            syncRuleField();
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}
