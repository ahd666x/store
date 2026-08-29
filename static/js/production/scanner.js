const Scanner = {
    init() {
        this.initPartScanner();
        this.initPackagingUnit();
    },

    initPartScanner() {
        const scanFormCnc = document.querySelector('form[action*="scan_part_cnc"]');
        if (scanFormCnc) {
            scanFormCnc.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(scanFormCnc);
                let barcode = formData.get('barcode').trim().replace(/\.cnc$/i, '');
                formData.set('barcode', barcode);

                try {
                    const response = await fetch(scanFormCnc.action, {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok && response.headers.get('Content-Type').includes('application/octet-stream')) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        const disposition = response.headers.get('Content-Disposition');
                        a.download = disposition ? disposition.split('filename=')[1].replace(/"/g, '') : 'file.cnc';
                        a.click();
                        window.URL.revokeObjectURL(url);

                        alert('✅  CNC تکمیل و فایل دانلود شد.');
                        document.getElementById('barcode').value = '';
                        document.getElementById('barcode').focus();
                    } else {
                        const errorText = await response.text();
                        alert('⚠️ ' + (errorText || 'خطایی رخ داد.'));
                        window.location.reload();
                    }
                } catch (error) {
                    alert('❌ خطای شبکه: ' + error.message);
                    window.location.reload();
                }
            });
        }

        const scanFormDr = document.querySelector('form[action*="scan_part_dr"]');
        if (scanFormDr) {
            scanFormDr.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(scanFormDr);
                let barcode = formData.get('barcode').trim().replace(/\.xml$/i, '');
                formData.set('barcode', barcode);

                try {
                    const response = await fetch(scanFormDr.action, {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok && response.headers.get('Content-Type').includes('application/xml')) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        const disposition = response.headers.get('Content-Disposition');
                        a.download = disposition ? disposition.split('filename=')[1].replace(/"/g, '') : 'file.xml';
                        a.click();
                        window.URL.revokeObjectURL(url);

                        alert('✅  سوراخکاری تکمیل و فایل XML دانلود شد.');
                        document.getElementById('barcode').value = '';
                        document.getElementById('barcode').focus();
                    } else {
                        const errorText = await response.text();
                        alert('⚠️ ' + (errorText || 'خطایی رخ داد.'));
                        window.location.reload();
                    }
                } catch (error) {
                    alert('❌ خطای شبکه: ' + error.message);
                    window.location.reload();
                }
            });
        }
    },

    initPackagingUnit() {
        const shipForm = document.getElementById('ship-form');
        if (shipForm) {
            shipForm.addEventListener('submit', (e) => {
                const p1 = shipForm.querySelector('input[name="plate_part1"]').value;
                const letter = shipForm.querySelector('.plate-letter-input').value;
                const p2 = shipForm.querySelector('input[name="plate_part2"]').value;
                const p3 = shipForm.querySelector('input[name="plate_part3"]').value;
                const fullPlate = p1 + letter + p2 + '-' + p3;
                document.getElementById('full-plate').value = fullPlate;
            });

            const savedPlate = shipForm.dataset.savedPlate;
            if (savedPlate && savedPlate !== 'نامشخص' && savedPlate !== '') {
                const parts = savedPlate.match(/^(\d+)(\D?)(\d+)-(\d+)$/);
                if (parts) {
                    shipForm.querySelector('input[name="plate_part1"]').value = parts[1];
                    shipForm.querySelector('.plate-letter-input').value = parts[2] || '';
                    shipForm.querySelector('input[name="plate_part2"]').value = parts[3];
                    shipForm.querySelector('input[name="plate_part3"]').value = parts[4];
                } else {
                    shipForm.querySelector('input[name="plate_part1"]').value = savedPlate;
                }
            }
        }
    }
};
