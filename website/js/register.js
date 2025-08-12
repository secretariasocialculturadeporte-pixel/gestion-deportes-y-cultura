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
            plan: document.querySelector('input[name="plan"]:checked').value,
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
                // The backend now sends a URL to redirect to.
                if (result.checkout_url) {
                    // This is a paid plan, redirect to Stripe Checkout
                    showMessage('¡Registro casi completo! Serás redirigido a nuestra pasarela de pago segura para finalizar la suscripción.', 'success');
                    setTimeout(() => {
                        window.location.href = result.checkout_url;
                    }, 3000);
                } else if (result.redirect_url) {
                    // This is a free trial, redirect to the login page
                    showMessage('¡Registro de prueba exitoso! Serás redirigido a la página de inicio de sesión.', 'success');
                     setTimeout(() => {
                        window.location.href = result.redirect_url;
                    }, 3000);
                } else {
                     showMessage('Respuesta inesperada del servidor.', 'error');
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
