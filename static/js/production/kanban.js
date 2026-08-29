const Kanban = {
    init() {
        let dragged = null;
        const movedTaskIds = new Set();

        const loadMovedTaskIds = () => {
            try {
                const raw = localStorage.getItem('movedPaintTasks');
                if (raw) {
                    JSON.parse(raw).forEach(id => movedTaskIds.add(id));
                }
            } catch (e) {}
        };

        const saveMovedTaskIds = () => {
            try {
                localStorage.setItem('movedPaintTasks', JSON.stringify(Array.from(movedTaskIds)));
            } catch (e) {}
        };

        const applyMovedClasses = () => {
            movedTaskIds.forEach(id => {
                const card = document.querySelector(`.kanban-card[data-task-id="${id}"]`);
                if (card) card.classList.add('moved-by-drag');
            });
        };

        loadMovedTaskIds();
        applyMovedClasses();

        document.querySelectorAll('.kanban-card').forEach(card => {
            card.addEventListener('dragstart', () => {
                dragged = card;
                card.classList.add('dragging');
            });
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                dragged = null;
            });
        });

        document.querySelectorAll('.kanban-col').forEach(col => {
            col.addEventListener('dragover', (e) => {
                e.preventDefault();
                col.classList.add('drag-over');
            });
            col.addEventListener('dragleave', () => {
                col.classList.remove('drag-over');
            });
            col.addEventListener('drop', (e) => {
                e.preventDefault();
                col.classList.remove('drag-over');
                if (!dragged) return;

                const taskId = parseInt(dragged.dataset.taskId, 10);
                const isUnscheduled = col.dataset.unscheduled === 'true';
                const container = col.querySelector('.kanban-cards');
                const empty = container.querySelector('.kanban-empty');
                if (empty) empty.remove();
                container.appendChild(dragged);

                movedTaskIds.add(taskId);
                saveMovedTaskIds();
                dragged.classList.add('moved-by-drag');

                document.querySelectorAll('.kanban-col').forEach(c => {
                    const count = c.querySelectorAll('.kanban-card').length;
                    c.querySelector('.badge-count').textContent = count;
                });

                if (isUnscheduled) {
                    this.unassignWorker(taskId);
                } else {
                    const workerId = col.dataset.workerId;
                    this.assignWorker(taskId, workerId, col.dataset.date);
                }
            });
        });

        const resetBtn = document.getElementById('resetScheduleBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                if (!confirm('آیا از بازنشانی زمان‌بندی این روز اطمینان دارید؟\nتمام تخصیص‌های دستی حذف و زمان‌بندی مجدد انجام می‌شود.')) {
                    return;
                }
                const originalHtml = resetBtn.innerHTML;
                resetBtn.disabled = true;
                resetBtn.innerHTML = '<span class="loading-spinner"></span> در حال بازنشانی...';

                fetch('{% url "painting_reset_schedule" %}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': Csrf.getToken()
                    },
                    body: JSON.stringify({ date: '{{ selected_date_str }}' })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message || 'زمان‌بندی بازنشانی شد.');
                        window.location.reload();
                    } else {
                        alert(data.error || 'خطا در بازنشانی.');
                        resetBtn.disabled = false;
                        resetBtn.innerHTML = originalHtml;
                    }
                })
                .catch(() => {
                    alert('خطای ارتباط با سرور');
                    resetBtn.disabled = false;
                    resetBtn.innerHTML = originalHtml;
                });
            });
        }
    },

    assignWorker(taskId, workerId, date, allowOvertime = false) {
        const postData = {
            csrfmiddlewaretoken: Csrf.getToken(),
            task_id: taskId,
            worker_id: workerId,
            target_date: date
        };
        if (allowOvertime) postData.allow_overtime = 'true';

        fetch('{% url "painting_assign_worker" %}', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': Csrf.getToken()
            },
            body: JSON.stringify(postData)
        })
        .then(res => res.json())
        .then(data => {
            if (!data || !data.success) {
                if (data && data.requires_overtime_confirmation) {
                    if (confirm(data.error || 'این تغییر باعث خروج از ساعت کاری می‌شود. آیا ادامه می‌دهید؟')) {
                        this.assignWorker(taskId, workerId, date, true);
                    }
                    return;
                }
                alert('خطا در تخصیص — صفحه را رفرش کنید');
            }
        })
        .catch(() => alert('خطا در تخصیص — صفحه را رفرش کنید'));
    },

    unassignWorker(taskId) {
        fetch('{% url "painting_unassign_worker" %}', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': Csrf.getToken()
            },
            body: JSON.stringify({ task_id: taskId })
        })
        .then(res => res.json())
        .then(data => {
            if (!data || !data.success) {
                alert('خطا در حذف برنامه‌ریزی — صفحه را رفرش کنید');
            }
        })
        .catch(() => alert('خطا در حذف برنامه‌ریزی — صفحه را رفرش کنید'));
    }
};
