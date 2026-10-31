// EasyShare / ShareShelf AI Frontend JS

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto dismiss alerts after 6 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) {
          bsAlert.close();
        }
      } catch (e) {
        // Fallback fade
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
      }
    }, 6000);
  });

  // 2. Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 3. File upload validation (Max 16MB)
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        const file = this.files[0];
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
          alert('Selected file is too large! Please select an image under 16 MB.');
          this.value = '';
        }
      }
    });
  });

  // 4. Password visibility toggle (if present)
  const togglePasswordBtns = document.querySelectorAll('.toggle-password');
  togglePasswordBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        const isPassword = input.getAttribute('type') === 'password';
        input.setAttribute('type', isPassword ? 'text' : 'password');
        const icon = this.querySelector('i');
        if (icon) {
          icon.classList.toggle('bi-eye');
          icon.classList.toggle('bi-eye-slash');
        }
      }
    });
  });
});
