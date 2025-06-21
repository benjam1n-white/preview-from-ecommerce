<script>
    {/* abrir modal de retroalimentacion */}
    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('fail', () => {
            document.getElementById('modalsTiendaForm').showModal();
        });
    });

    {/* // Mobile menu toggle functionality */}
    document.getElementById('mobile-menu-button').addEventListener('click', function() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
        
        // Disable scroll when sidebar is open
        document.body.classList.toggle('overflow-hidden');
    });
    
    // Close sidebar when clicking on overlay
    document.getElementById('sidebar-overlay').addEventListener('click', function() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        
        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    });

    function openEditModal(tiendaId, tiendaNombre) {
        // 1. Actualizar el título del modal
        const modalTitle = document.querySelector('#editarTiendaModal h3');
        modalTitle.textContent = `Editar Tienda: ${tiendaNombre}`;
        
        // 2. Limpiar el contenedor del formulario
        const formContainer = document.querySelector('#editarTiendaModal .m-4');
        formContainer.innerHTML = '<p>Cargando formulario...</p>';
        
        // 3. Mostrar el modal
        document.getElementById('editarTiendaModal').showModal();
        
        // 4. Cargar el formulario de edición via HTMX
        htmx.ajax('GET', `/tienda/editar/${tiendaId}/`, {
            target: '#editarTiendaModal .m-4',
            swap: 'innerHTML',
            onSuccess: function() {
                const form = document.querySelector('#editarTiendaModal form');
                if (form) {
                    const editUrl = `/tienda/editar/${tiendaId}/`;
                    
                    // Asignar los atributos HTMX correctamente
                    form.setAttribute('hx-post', editUrl);
                    form.setAttribute('hx-target', `#tienda-row-${tiendaId}`);
                    form.setAttribute('hx-swap', 'outerHTML');
                    form.setAttribute('hx-indicator', '#indicator');
                    
                    // Cerrar el modal después de guardar
                    form.setAttribute('hx-on:after-request', 'document.getElementById("editarTiendaModal").close()');
                    
                    // Asegurarse de que HTMX procese los nuevos atributos
                    htmx.process(form);
                }
            },
            onError: function() {
                formContainer.innerHTML = '<p class="text-error">Error al cargar el formulario</p>';
            }
            
        });
    }
    
     // Configuración del modal de confirmación para HTMX
    {% comment %} document.body.addEventListener('htmx:confirm', function(e) {
        e.preventDefault();
        const confirmModal = document.getElementById('confirmModal');
        const confirmMessage = document.getElementById('confirmMessage');
        const confirmDelete = document.getElementById('confirmDelete');
        
        confirmMessage.textContent = e.detail.question || '¿Estás seguro de que deseas realizar esta acción?';
        
        confirmDelete.onclick = function() {
            e.detail.issueRequest(true);
            confirmModal.close();
        };
        
        confirmModal.showModal();
    }); {% endcomment %}


    //Eliminar Tienda
     // Modal de eliminación
    let tiendaIdAEliminar = null;

    function abrirModalEliminar(id) {
        tiendaIdAEliminar = id;
        document.getElementById('confirmarEliminarModal').showModal();
    }

    document.getElementById('btnEliminarConfirmado').addEventListener('click', function() {
        if (tiendaIdAEliminar) {
            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            htmx.ajax('DELETE', `/tienda/eliminar/${tiendaIdAEliminar}/`, {
                target: `#tienda-row-${tiendaIdAEliminar}`,
                swap: 'delete',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                onSuccess: function() {
                    // Cerrar el modal
                    document.getElementById('confirmarEliminarModal').close();
                },
                onError: function() {
                    alert('Error al eliminar la tienda');
                    document.getElementById('confirmarEliminarModal').close();
                }
            });
        }
        tiendaIdAEliminar = null;
    });
// Función para agregar CSRF token a todas las peticiones HTMX
document.body.addEventListener('htmx:configRequest', (event) => {
    const csrfToken = "{{ csrf_token }}";
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken;
    }
});

document.addEventListener('htmx:afterSwap', function(event) {
    // Manejar éxito al agregar tienda
    if (event.detail.triggeringEvent?.target?.id === 'tienda-form' && 
        event.detail.xhr.status === 200) {
        // Cerrar modal y resetear formulario
        modalsTiendaForm.close();
        document.getElementById('tienda-form').reset();
        
        // Mostrar notificación de éxito
        htmx.trigger('#notification-area', 'notify', {
            message: 'Tienda agregada exitosamente',
            type: 'success'
        });
    }
    
    // Manejar errores de validación
    if (event.detail.triggeringEvent?.target?.id === 'tienda-form' && 
        event.detail.xhr.status === 400) {
        // Mantener el modal abierto y mostrar errores
        modalsTiendaForm.showModal();
    }
});

{% comment %} abrir y cerrar modal de añadir tiendas {% endcomment %}
document.addEventListener('DOMContentLoaded', function() {
    // Manejar cierre del modal después de éxito
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'tienda-form' && 
            event.detail.xhr.responseText.includes('success')) {
            setTimeout(() => {
                modalsTiendaForm.close();
                htmx.trigger('#tbodyTable', 'refresh');
            }, 2000);
        }
    });
    
    // Resetear formulario al abrir modal
    document.getElementById('modalsTiendaForm').addEventListener('show', function() {
        htmx.ajax('GET', '{% url "creat" %}', {
            target: '#tienda-form',
            swap: 'outerHTML'
        });
    });
});


</script>