document.addEventListener('DOMContentLoaded', () => {
    const registrationForm = document.getElementById('form-registro');
    const messageDiv = document.getElementById('form-mensaje');
    const findNearbyBtn = document.getElementById('find-nearby-btn');
    const nearbyResultsContainer = document.getElementById('nearby-results');

    // --- Geolocation Logic ---
    findNearbyBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            nearbyResultsContainer.innerHTML = '<p>La geolocalización no es soportada por tu navegador.</p>';
            return;
        }

        nearbyResultsContainer.innerHTML = '<p>Obteniendo tu ubicación...</p>';

        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;

            try {
                const response = await fetch(`/api/empresas_cercanas?lat=${latitude}&lon=${longitude}`);
                const tenants = await response.json();

                if (response.ok) {
                    renderNearbyTenants(tenants);
                } else {
                    nearbyResultsContainer.innerHTML = `<p>Error: ${tenants.error}</p>`;
                }
            } catch (error) {
                nearbyResultsContainer.innerHTML = '<p>Error al contactar el servidor.</p>';
            }

        }, () => {
            nearbyResultsContainer.innerHTML = '<p>No se pudo obtener tu ubicación. Por favor, asegúrate de haber dado permiso.</p>';
        });
    });

    function renderNearbyTenants(tenants) {
        if (tenants.length === 0) {
            nearbyResultsContainer.innerHTML = '<p>No se encontraron organizaciones cercanas. ¡Puedes ser la primera en tu área!</p>';
            return;
        }

        let html = '<h3>Organizaciones Cercanas:</h3><ul>';
        tenants.forEach(tenant => {
            html += `<li>${tenant.nombre_empresa} (${tenant.distancia_km} km) - ${tenant.municipio}</li>`;
        });
        html += '</ul>';
        nearbyResultsContainer.innerHTML = html;
    }


    // --- Registration Form Logic ---
    registrationForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission

        // Collect form data
        const formData = {
            nombre_empresa: document.getElementById('nombre_empresa').value,
            nombre_admin: document.getElementById('nombre_admin').value,
            correo_admin: document.getElementById('correo_admin').value,
            usuario_admin: document.getElementById('usuario_admin').value,
            password_admin: document.getElementById('password_admin').value,
        };

        // Basic validation
        if (Object.values(formData).some(val => val.trim() === '')) {
            showMessage('Por favor, completa todos los campos.', 'error');
            return;
        }

        showMessage('Registrando, por favor espera...', 'info');

        try {
            const response = await fetch('/api/register_tenant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (response.ok) {
                const selectedPlan = document.querySelector('input[name="plan"]:checked').value;

                if (selectedPlan === 'gratis') {
                    showMessage(`¡Registro exitoso! La empresa '${result.empresa}' ha sido creada. Serás redirigido a la página de inicio de sesión.`, 'success');
                    setTimeout(() => {
                        window.location.href = "/"; // Redirect to the Flet app login
                    }, 4000);
                } else {
                    // For paid plans, redirect to a dummy payment link
                    showMessage(`¡Registro exitoso! Serás redirigido a PayPal para completar tu pago.`, 'success');
                    const planName = selectedPlan === 'pro_mensual' ? "Plan Pro Mensual" : "Plan Pro Anual";
                    const planAmount = selectedPlan === 'pro_mensual' ? "100.00" : "1000.00";

                    // This is a placeholder URL. A real integration would use the PayPal SDK.
                    const paypalURL = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=your-email@example.com&item_name=${encodeURIComponent(planName)}&amount=${planAmount}&currency_code=USD`;

                    setTimeout(() => {
                        window.location.href = paypalURL;
                    }, 4000);
                }
            } else {
                showMessage(result.error || 'Ocurrió un error desconocido.', 'error');
            }
        } catch (error) {
            console.error('Error en el registro:', error);
            showMessage('No se pudo conectar con el servidor. Intenta de nuevo más tarde.', 'error');
        }
    });

    function showMessage(message, type) {
        messageDiv.textContent = message;
        messageDiv.className = `message-${type}`; // e.g., message-error, message-success
    }
});
