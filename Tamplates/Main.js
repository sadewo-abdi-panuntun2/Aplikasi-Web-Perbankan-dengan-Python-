// Format input uang
document.addEventListener('DOMContentLoaded', function() {
    // Format input jumlah uang
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', formatCurrencyInput);
        input.addEventListener('blur', formatCurrencyDisplay);
    });
    
    // Validasi form transfer
    const transferForm = document.querySelector('form[action="/transfer"]');
    if (transferForm) {
        transferForm.addEventListener('submit', validateTransfer);
    }
});

function formatCurrencyInput(e) {
    let value = e.target.value.replace(/[^\d]/g, '');
    e.target.value = value;
}

function formatCurrencyDisplay(e) {
    let value = parseInt(e.target.value) || 0;
    e.target.value = value.toLocaleString('id-ID');
}

function validateTransfer(e) {
    const amountInput = document.querySelector('input[name="amount"]');
    const recipientInput = document.querySelector('input[name="recipient_account"]');
    const balance = parseFloat(document.querySelector('.balance-amount')?.textContent?.replace(/[^\d]/g, '') || 0);
    const amount = parseInt(amountInput.value.replace(/[^\d]/g, '')) || 0;
    
    if (amount < 1000) {
        alert('Minimum transfer adalah Rp 1,000');
        e.preventDefault();
        return false;
    }
    
    if (amount > balance) {
        alert('Saldo tidak mencukupi');
        e.preventDefault();
        return false;
    }
    
    const recipient = recipientInput.value.trim();
    if (!/^\d{16}$/.test(recipient)) {
        alert('Nomor rekening harus 16 digit');
        e.preventDefault();
        return false;
    }
    
    return true;
}

// Auto-refresh saldo setiap 30 detik
if (window.location.pathname === '/dashboard') {
    setInterval(refreshBalance, 30000);
}

function refreshBalance() {
    fetch('/api/balance')
        .then(response => response.json())
        .then(data => {
            const balanceElement = document.querySelector('.balance-amount');
            if (balanceElement) {
                balanceElement.textContent = 'Rp ' + parseFloat(data.balance).toLocaleString('id-ID', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        })
        .catch(error => console.error('Error refreshing balance:', error));
}
