const PaintingHolidays = {
    init() {
        const addHolidayForm = document.getElementById('addHolidayForm');
        if (!addHolidayForm) return;

        addHolidayForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(addHolidayForm);
            fetch('/painting/holidays/', {
                method: 'POST',
                headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                body: formData
            })
            .then(res => res.json())
            .then(resp => {
                if (resp.success) location.reload();
                else alert(resp.error || 'خطا');
            })
            .catch(() => alert('خطای ارتباط با سرور'));
        });

        document.querySelectorAll('.delete-holiday').forEach(btn => {
            btn.addEventListener('click', function() {
                if (!confirm('آیا از حذف این تعطیلی اطمینان دارید؟')) return;
                const id = this.dataset.id;
                fetch('/painting/holidays/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                    body: new URLSearchParams({ csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '', action: 'delete', holiday_id: id })
                })
                .then(res => res.json())
                .then(resp => {
                    if (resp.success) location.reload();
                    else alert(resp.error || 'خطا');
                })
                .catch(() => alert('خطای ارتباط با سرور'));
            });
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PaintingHolidays.init());
} else {
    PaintingHolidays.init();
}
