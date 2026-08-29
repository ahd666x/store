const PaintingProcesses = {
    init() {
        const processForm = document.getElementById('processForm');
        if (!processForm) return;

        const processModal = document.getElementById('processModal');

        processForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(processForm);
            fetch(processForm.action, {
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

        document.querySelectorAll('.edit-process').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                fetch('/painting/processes/' + id + '/')
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('modalTitle').textContent = 'ویرایش روند';
                        document.getElementById('formAction').value = 'edit';
                        document.getElementById('processId').value = data.id;
                        processForm.querySelector('[name="name"]').value = data.name;
                        processForm.querySelector('[name="code"]').value = data.code;
                        processForm.querySelector('[name="color_codes"]').value = JSON.stringify(data.color_codes);
                        processForm.querySelector('[name="description"]').value = data.description;
                        processForm.querySelector('[name="is_active"]').checked = data.is_active;
                        if (processModal && window.bootstrap) {
                            new bootstrap.Modal(processModal).show();
                        }
                    });
            });
        });

        document.querySelectorAll('.delete-process').forEach(btn => {
            btn.addEventListener('click', function() {
                if (!confirm('آیا از حذف این روند اطمینان دارید؟')) return;
                const id = this.dataset.id;
                fetch('/painting/processes/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                    body: new URLSearchParams({ csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '', action: 'delete', process_id: id })
                })
                .then(res => res.json())
                .then(data => { if (data.success) location.reload(); });
            });
        });

        document.querySelectorAll('.toggle-process').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                fetch('/painting/processes/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                    body: new URLSearchParams({ csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '', action: 'toggle_active', process_id: id })
                })
                .then(res => res.json())
                .then(data => { if (data.success) location.reload(); });
            });
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PaintingProcesses.init());
} else {
    PaintingProcesses.init();
}
