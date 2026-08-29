const PaintingReadyList = {
    init() {
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        const scheduleDate = document.getElementById('scheduleDate')?.value || '';
        const searchInput = document.getElementById('searchInput');
        const clearBtn = document.getElementById('clearSearch');
        const searchForm = document.getElementById('searchForm');
        const warningsBox = document.getElementById('warningsBox');

        if (!searchInput) return;

        const toggleClearBtn = () => {
            if (searchInput.value.length > 0) {
                clearBtn?.classList.add('show');
            } else {
                clearBtn?.classList.remove('show');
            }
        };

        toggleClearBtn();
        searchInput?.addEventListener('input', toggleClearBtn);

        clearBtn?.addEventListener('click', function() {
            searchInput.value = '';
            toggleClearBtn();
            searchForm?.submit();
        });

        searchInput?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchForm?.submit();
            }
        });

        const updateSummary = () => {
            const checked = document.querySelectorAll('.item-checkbox:checked');
            let minutes = 0;
            checked.forEach(cb => {
                minutes += parseInt(cb.dataset.minutes) || 0;
            });
            const selCount = document.getElementById('selCount');
            const selMinutes = document.getElementById('selMinutes');
            const addBtn = document.getElementById('addSelectedToScheduleBtn');
            const deleteBtn = document.getElementById('deleteSelectedTasksBtn');
            if (selCount) selCount.textContent = checked.length;
            if (selMinutes) selMinutes.textContent = minutes;
            if (addBtn) addBtn.disabled = checked.length === 0;
            if (deleteBtn) deleteBtn.disabled = checked.length === 0;
        };

        document.getElementById('selectAllItems')?.addEventListener('change', function() {
            document.querySelectorAll('.item-checkbox:not(:disabled)').forEach(cb => {
                cb.checked = this.checked;
            });
            updateSummary();
        });

        document.querySelectorAll('.item-checkbox').forEach(cb => {
            cb.addEventListener('change', updateSummary);
        });

        document.getElementById('addSelectedToScheduleBtn')?.addEventListener('click', function() {
            const itemIds = Array.from(document.querySelectorAll('.item-checkbox:checked')).map(cb => cb.value);
            if (!itemIds.length) return;

            const btn = this;
            const originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner"></span> در حال برنامه‌ریزی...';
            if (warningsBox) {
                warningsBox.classList.remove('error', 'success');
                warningsBox.textContent = '';
            }

            fetch('/painting/add-to-schedule/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrf },
                body: new URLSearchParams({ csrfmiddlewaretoken: csrf, 'item_ids[]': itemIds, date: scheduleDate })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (warningsBox) {
                        warningsBox.classList.add('success').textContent = data.message || 'با موفقیت انجام شد.';
                    }
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        window.location.href = '/painting/schedule/';
                    }
                } else {
                    if (warningsBox) {
                        warningsBox.classList.add('error').textContent = data.error || 'خطا در انجام عملیات.';
                    }
                    btn.disabled = false;
                    btn.innerHTML = originalHtml;
                }
            })
            .catch(err => {
                if (warningsBox) {
                    warningsBox.classList.add('error').textContent = 'خطای ارتباط با سرور';
                }
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            });
        });

        document.getElementById('deleteSelectedTasksBtn')?.addEventListener('click', function() {
            const itemIds = Array.from(document.querySelectorAll('.item-checkbox:checked')).map(cb => cb.value);
            if (!itemIds.length) return;

            if (!confirm(itemIds.length + ' آیتم انتخاب‌شده — برنامه‌ریزی نقاشی آن‌ها (در وضعیت در انتظار) حذف شود؟')) {
                return;
            }

            const btn = this;
            const originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner"></span> در حال حذف برنامه...';
            if (warningsBox) {
                warningsBox.classList.remove('error', 'success');
                warningsBox.textContent = '';
            }

            fetch('/painting/delete-tasks/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrf },
                body: new URLSearchParams({ csrfmiddlewaretoken: csrf, 'item_ids[]': itemIds })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (warningsBox) {
                        warningsBox.classList.add('success').textContent = data.message || 'برنامه‌ریزی حذف شد.';
                    }
                    window.location.reload();
                } else {
                    if (warningsBox) {
                        warningsBox.classList.add('error').textContent = data.error || 'خطا در حذف برنامه‌ریزی.';
                    }
                    btn.disabled = false;
                    btn.innerHTML = originalHtml;
                }
            })
            .catch(() => {
                if (warningsBox) {
                    warningsBox.classList.add('error').textContent = 'خطای ارتباط با سرور';
                }
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            });
        });

        updateSummary();
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PaintingReadyList.init());
} else {
    PaintingReadyList.init();
}
