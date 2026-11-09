/**
 * SoleVault - Interactive E-Commerce & Order Tracking JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initCartBadges();
  initThumbnailGallery();
  initSizeSelectors();
  initQuantityControls();
  initPaymentTabs();
  initCheckoutForm();
  initTrackingSimulator();
  initDismissAlerts();
});

/* ==========================================================================
   TOAST NOTIFICATIONS
   ========================================================================== */
function showToast(message, type = 'success') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ==========================================================================
   NAVBAR CART BADGE ANIMATION
   ========================================================================== */
function updateCartCount(newCount) {
  const badge = document.getElementById('navCartBadge');
  if (badge) {
    badge.textContent = newCount;
    badge.classList.remove('bounce');
    void badge.offsetWidth; // Trigger reflow
    badge.classList.add('bounce');
  }
}

function initCartBadges() {
  // Handlers for Add to Cart forms via AJAX
  document.querySelectorAll('.ajax-add-cart-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span>Adding...</span>`;
      }

      const formData = new FormData(form);
      formData.append('ajax', 'true');

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: formData
        });
        const data = await response.json();
        if (data.success) {
          updateCartCount(data.cart_count);
          showToast(data.message || 'Added to your bag!');
        } else {
          showToast(data.message || 'Could not add to cart.', 'error');
        }
      } catch (err) {
        console.error(err);
        form.submit(); // fallback to standard submit
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      }
    });
  });
}

/* ==========================================================================
   PRODUCT DETAIL GALLERY & THUMBNAILS
   ========================================================================== */
function initThumbnailGallery() {
  const mainImg = document.getElementById('detailMainImage');
  const thumbs = document.querySelectorAll('.thumb-item');

  if (mainImg && thumbs.length) {
    thumbs.forEach(thumb => {
      thumb.addEventListener('click', () => {
        thumbs.forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');
        const newSrc = thumb.getAttribute('data-img-src');
        if (newSrc) {
          mainImg.src = newSrc;
        }
      });
    });
  }
}

/* ==========================================================================
   PRODUCT DETAIL SIZE SELECTOR
   ========================================================================== */
function initSizeSelectors() {
  const sizeInput = document.getElementById('selectedSizeInput');
  const sizeRadios = document.querySelectorAll('input[name="shoe_size_choice"]');

  if (sizeRadios.length && sizeInput) {
    sizeRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        if (radio.checked) {
          sizeInput.value = radio.value;
        }
      });
    });
  }
}

/* ==========================================================================
   QUANTITY CONTROLS (PRODUCT & CART)
   ========================================================================== */
function initQuantityControls() {
  // Product detail qty controls
  const decBtn = document.getElementById('qtyDec');
  const incBtn = document.getElementById('qtyInc');
  const qtyInput = document.getElementById('productQtyInput');

  if (decBtn && incBtn && qtyInput) {
    decBtn.addEventListener('click', () => {
      let val = parseInt(qtyInput.value) || 1;
      if (val > 1) {
        qtyInput.value = val - 1;
      }
    });

    incBtn.addEventListener('click', () => {
      let val = parseInt(qtyInput.value) || 1;
      if (val < 20) {
        qtyInput.value = val + 1;
      }
    });
  }

  // Cart page item quantity ajax updates
  document.querySelectorAll('.cart-qty-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const row = btn.closest('.cart-item-row');
      const action = btn.getAttribute('data-action');
      const url = btn.getAttribute('data-url');
      const csrfToken = getCookie('csrftoken');

      try {
        const formData = new FormData();
        formData.append('action', action);

        const res = await fetch(url, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
          },
          body: formData
        });

        const data = await res.json();
        if (data.success) {
          updateCartCount(data.cart_count);
          if (data.item_quantity <= 0 || action === 'remove') {
            row.style.opacity = '0';
            setTimeout(() => {
              row.remove();
              if (data.cart_count === 0) {
                window.location.reload();
              }
            }, 250);
          } else {
            const qtyDisplay = row.querySelector('.cart-item-qty-display');
            const subtotalDisplay = row.querySelector('.cart-item-subtotal-display');
            if (qtyDisplay) qtyDisplay.textContent = data.item_quantity;
            if (subtotalDisplay) subtotalDisplay.textContent = `$${data.item_subtotal}`;
          }

          // Update sidebar totals
          const subtotalElem = document.getElementById('summarySubtotal');
          const taxElem = document.getElementById('summaryTax');
          const shippingElem = document.getElementById('summaryShipping');
          const grandTotalElem = document.getElementById('summaryGrandTotal');

          if (subtotalElem) subtotalElem.textContent = `$${data.cart_subtotal}`;
          if (taxElem) taxElem.textContent = `$${data.cart_tax}`;
          if (shippingElem) shippingElem.textContent = parseFloat(data.cart_shipping) > 0 ? `$${data.cart_shipping}` : 'FREE';
          if (grandTotalElem) grandTotalElem.textContent = `$${data.cart_grand_total}`;
        }
      } catch (err) {
        console.error('Failed to update cart item', err);
      }
    });
  });
}

/* ==========================================================================
   CHECKOUT PAYMENT METHOD TABS
   ========================================================================== */
function initPaymentTabs() {
  const tabs = document.querySelectorAll('.payment-tab-btn');
  const hiddenMethodInput = document.getElementById('paymentMethodInput');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const targetMethod = tab.getAttribute('data-method');
      if (hiddenMethodInput) {
        hiddenMethodInput.value = targetMethod;
      }

      document.querySelectorAll('.payment-pane').forEach(pane => {
        pane.classList.remove('active');
      });

      const activePane = document.getElementById(`pane-${targetMethod}`);
      if (activePane) {
        activePane.classList.add('active');
      }
    });
  });

  // Card input preview binding
  const cardNumInput = document.getElementById('cardNumInput');
  const cardHolderInput = document.getElementById('cardHolderInput');
  const cardExpiryInput = document.getElementById('cardExpiryInput');

  const cardMockNum = document.getElementById('cardMockNum');
  const cardMockHolder = document.getElementById('cardMockHolder');
  const cardMockExp = document.getElementById('cardMockExp');

  if (cardNumInput && cardMockNum) {
    cardNumInput.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '').substring(0, 16);
      let formatted = val != '' ? val.match(/.{1,4}/g).join(' ') : '•••• •••• •••• ••••';
      cardMockNum.textContent = formatted;
    });
  }

  if (cardHolderInput && cardMockHolder) {
    cardHolderInput.addEventListener('input', (e) => {
      cardMockHolder.textContent = e.target.value || 'YOUR NAME';
    });
  }

  if (cardExpiryInput && cardMockExp) {
    cardExpiryInput.addEventListener('input', (e) => {
      cardMockExp.textContent = e.target.value || 'MM/YY';
    });
  }
}

/* ==========================================================================
   CHECKOUT FORM SUBMISSION & PAYMENT COMPLETE MODAL POP-UP
   ========================================================================== */
function initCheckoutForm() {
  const checkoutForm = document.getElementById('checkoutForm');
  const modalBackdrop = document.getElementById('paymentModal');

  if (checkoutForm && modalBackdrop) {
    checkoutForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const payBtn = document.getElementById('submitPaymentBtn');
      const originalText = payBtn ? payBtn.innerHTML : '';
      if (payBtn) {
        payBtn.disabled = true;
        payBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
            <line x1="12" y1="2" x2="12" y2="6"></line>
            <line x1="12" y1="18" x2="12" y2="22"></line>
            <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
            <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
            <line x1="2" y1="12" x2="6" y2="12"></line>
            <line x1="18" y1="12" x2="22" y2="12"></line>
            <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
            <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
          </svg>
          <span>Processing Payment...</span>
        `;
      }

      // Simulate network authorization delay (800ms) for realistic buyer experience
      await new Promise(r => setTimeout(r, 800));

      const formData = new FormData(checkoutForm);
      formData.append('is_ajax', 'true');

      try {
        const response = await fetch(checkoutForm.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: formData
        });

        const data = await response.json();
        if (data.success) {
          // Fill pop-up modal details
          document.getElementById('modalOrderNum').textContent = data.order_number;
          document.getElementById('modalTrackingNum').textContent = data.tracking_number;
          document.getElementById('modalAmount').textContent = data.total_amount;
          document.getElementById('modalPaymentMethod').textContent = data.payment_method;

          // Configure track button link
          const trackBtn = document.getElementById('modalTrackBtn');
          if (trackBtn) {
            trackBtn.href = data.tracking_url;
          }

          // Reset cart badge to 0
          updateCartCount(0);

          // Reveal the modal with animation
          modalBackdrop.classList.add('show');
        } else {
          showToast(data.message || 'Payment failed. Please verify your details.', 'error');
          if (payBtn) {
            payBtn.disabled = false;
            payBtn.innerHTML = originalText;
          }
        }
      } catch (err) {
        console.error('Payment submission failed', err);
        checkoutForm.submit(); // Fallback
      }
    });
  }
}

/* ==========================================================================
   ORDER TRACKING SIMULATOR
   ========================================================================== */
function initTrackingSimulator() {
  const simBtn = document.getElementById('simulateProgressBtn');
  if (simBtn) {
    simBtn.addEventListener('click', async () => {
      const url = simBtn.getAttribute('data-url');
      const csrfToken = getCookie('csrftoken');

      simBtn.disabled = true;
      simBtn.innerHTML = 'Updating status...';

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
          }
        });
        const data = await response.json();
        if (data.success) {
          showToast(data.message, 'success');
          setTimeout(() => {
            window.location.reload();
          }, 800);
        } else {
          showToast(data.message, 'info');
          simBtn.disabled = false;
          simBtn.innerHTML = 'Advance Status (Demo)';
        }
      } catch (err) {
        console.error('Tracking advance error', err);
        simBtn.disabled = false;
        simBtn.innerHTML = 'Advance Status (Demo)';
      }
    });
  }
}

/* ==========================================================================
   HELPERS & UTILITIES
   ========================================================================== */
function initDismissAlerts() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
