const PaintingStages = {
    init() {
        const stageForm = document.getElementById('stageForm');
        if (!stageForm) return;

        const stageModal = document.getElementById('stageModal');

        stageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(stageForm);
            fetch(stageForm.action, {
                method: 'POST',
                headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) location.reload();
                else alert('خطا: ' + JSON.stringify(data.errors || data));
            })
            .catch(() => alert('خطای ارتباط با سرور'));
        });

        document.querySelectorAll('.edit-stage').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                const form = document.getElementById('stageForm');
                fetch('/painting/stages/' + id + '/')
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('stageModalTitle').textContent = 'ویرایش مرحله';
                        document.getElementById('stageAction').value = 'edit';
                        document.getElementById('stageId').value = data.id;
                        form.querySelector('[name="process"]').value = data.process;
                        form.querySelector('[name="order"]').value = data.order;
                        form.querySelector('[name="name"]').value = data.name;
                        form.querySelector('[name="duration_minutes"]').value = data.duration_minutes;
                        form.querySelector('[name="drying_time_minutes"]').value = data.drying_time_minutes;
                        form.querySelector('[name="required_skill"]').value = data.required_skill;
                        if (stageModal && window.bootstrap) {
                            new bootstrap.Modal(stageModal).show();
                        }
                    });
            });
        });

        document.querySelectorAll('.delete-stage').forEach(btn => {
            btn.addEventListener('click', function() {
                if (!confirm('آیا از حذف این مرحله اطمینان دارید؟')) return;
                const id = this.dataset.id;
                fetch('/painting/stages/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                    body: new URLSearchParams({ csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '', action: 'delete', stage_id: id })
                })
                .then(res => res.json())
                .then(data => { if (data.success) location.reload(); });
            });
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PaintingStages.init());
} else {
    PaintingStages.init();
}
