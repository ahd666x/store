const PaintingAssignmentRules = {
    init() {
        const ruleModal = document.getElementById('ruleModal');
        const ruleTypeSelect = document.getElementById('ruleType');
        const priorityField = document.getElementById('priorityField');
        const ruleForm = document.getElementById('ruleForm');

        if (!ruleForm) return;

        const updatePriorityVisibility = () => {
            if (ruleTypeSelect.value === 'priority') {
                priorityField.style.display = '';
            } else {
                priorityField.style.display = 'none';
            }
        };

        updatePriorityVisibility();
        ruleTypeSelect?.addEventListener('change', updatePriorityVisibility);

        document.getElementById('addRuleBtn')?.addEventListener('click', function() {
            document.getElementById('ruleId').value = '';
            document.getElementById('modalTitle').textContent = 'جدید';
            document.getElementById('ruleWorker').value = '';
            document.getElementById('ruleStage').value = '';
            document.getElementById('ruleProcess').value = '';
            document.getElementById('ruleColors').value = '';
            ruleTypeSelect.value = 'priority';
            document.getElementById('rulePriority').value = 100;
            document.getElementById('ruleActive').checked = true;
            updatePriorityVisibility();
            if (ruleModal && window.bootstrap) {
                new bootstrap.Modal(ruleModal).show();
            }
        });

        document.querySelectorAll('.edit-rule').forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('ruleId').value = this.dataset.id;
                document.getElementById('modalTitle').textContent = 'ویرایش';
                document.getElementById('ruleWorker').value = this.dataset.worker;
                document.getElementById('ruleStage').value = this.dataset.stage || '';
                document.getElementById('ruleProcess').value = this.dataset.process || '';
                document.getElementById('ruleColors').value = this.dataset.colors || '';
                ruleTypeSelect.value = this.dataset.ruleType || 'priority';
                document.getElementById('ruleActive').checked = this.dataset.active === 'true';
                updatePriorityVisibility();
                if (ruleModal && window.bootstrap) {
                    new bootstrap.Modal(ruleModal).show();
                }
            });
        });

        ruleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const ruleId = document.getElementById('ruleId').value;
            const action = ruleId ? 'edit' : 'create';
            const formData = new FormData(this);
            const data = {
                csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                action: action,
                rule_id: ruleId,
                worker: formData.get('worker'),
                stage: formData.get('stage'),
                process: formData.get('process'),
                color_codes: formData.get('color_codes'),
                rule_type: formData.get('rule_type'),
                priority: formData.get('priority'),
                is_active: formData.get('is_active') === 'on'
            };
            fetch('/painting/assignment-rules/', {
                method: 'POST',
                headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                body: new URLSearchParams(data)
            })
            .then(res => res.json())
            .then(resp => {
                if (resp.success) window.location.reload();
                else alert(resp.error || 'خطا در ذخیره ');
            })
            .catch(() => alert('خطای ارتباط با سرور'));
        });

        document.querySelectorAll('.delete-rule').forEach(btn => {
            btn.addEventListener('click', function() {
                if (!confirm('آیا از حذف این  مطمئن هستید؟')) return;
                const id = this.dataset.id;
                fetch('/painting/assignment-rules/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                    body: new URLSearchParams({ csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '', action: 'delete', rule_id: id })
                })
                .then(res => res.json())
                .then(resp => {
                    if (resp.success) window.location.reload();
                    else alert(resp.error || 'خطا');
                })
                .catch(() => alert('خطای ارتباط با سرور'));
            });
        });

        document.querySelectorAll('.toggle-active').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                fetch('/painting/assignment-rules/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
                    body: new URLSearchParams({ csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '', action: 'toggle_active', rule_id: id })
                })
                .then(res => res.json())
                .then(resp => {
                    if (resp.success) window.location.reload();
                    else alert(resp.error || 'خطا');
                })
                .catch(() => alert('خطای ارتباط با سرور'));
            });
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PaintingAssignmentRules.init());
} else {
    PaintingAssignmentRules.init();
}
