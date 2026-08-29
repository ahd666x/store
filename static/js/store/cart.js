const Cart = {
    init() {
        document.addEventListener('htmx:afterSwap', (evt) => {
            const target = evt.detail.target;
            if (!target) return;
            const id = target.id;
            if (id === 'cart-count' || id === 'cart-count-mobile' || id === 'cart-count-mobile-menu' || id === 'cart-count-home') {
                const countText = target.textContent.trim();
                const count = parseInt(countText, 10);
                if (!isNaN(count) && count > 0) {
                    target.classList.remove('hidden');
                }
            }
        });
    },

    add(productId) {
        htmx.ajax('POST', `/cart/add/${productId}/`, {
            target: '#cart-count',
            swap: 'outerHTML'
        }).then(() => {
            const desktopCount = document.getElementById('cart-count');
            const mobileCount = document.getElementById('cart-count-mobile');
            const mobileMenuCount = document.getElementById('cart-count-mobile-menu');
            const homeCount = document.getElementById('cart-count-home');

            if (desktopCount && desktopCount.textContent) {
                const count = desktopCount.textContent.trim();
                if (mobileCount) mobileCount.textContent = count;
                if (mobileMenuCount) mobileMenuCount.textContent = count;
                if (homeCount) homeCount.textContent = count;
            }

            Toast.show('محصول به سبد خرید اضافه شد', 'success');
        });
    }
};
