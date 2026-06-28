/* ============================================================================
   CONFIGURACIÓN DEL BACKEND
   ============================================================================ */

const API_URL = 'http://localhost:8000/api/v1/password';
const BACKEND_HEALTH_URL = 'http://localhost:8000/health';

/* ============================================================================
   ESTADO DE LA APLICACIÓN
   ============================================================================ */

const appState = {
    currentPassword: null,
    history: JSON.parse(localStorage.getItem('passwordHistory')) || [],
    isLoading: false,
    lastError: null
};

/* ============================================================================
   ELEMENTOS DEL DOM
   ============================================================================ */

const DOM = {
    // Controles
    length: document.getElementById('length'),
    lengthValue: document.getElementById('lengthValue'),
    useUppercase: document.getElementById('useUppercase'),
    useLowercase: document.getElementById('useLowercase'),
    useDigits: document.getElementById('useDigits'),
    useSymbols: document.getElementById('useSymbols'),
    excludeAmbiguous: document.getElementById('excludeAmbiguous'),
    
    // Botones
    generateBtn: document.getElementById('generateBtn'),
    regenerateBtn: document.getElementById('regenerateBtn'),
    copyBtn: document.getElementById('copyBtn'),
    clearHistoryBtn: document.getElementById('clearHistoryBtn'),
    
    // Output
    passwordOutput: document.getElementById('passwordOutput'),
    resultPanel: document.querySelector('.result-panel'),
    errorMessage: document.getElementById('errorMessage'),
    
    // Fuerza
    strengthIndicator: document.getElementById('strengthIndicator'),
    strengthText: document.getElementById('strengthText'),
    entropyText: document.getElementById('entropyText'),
    
    // Info
    infoLength: document.getElementById('infoLength'),
    infoAlphabet: document.getElementById('infoAlphabet'),
    infoEntropy: document.getElementById('infoEntropy'),
    
    // Historial
    historyList: document.getElementById('historyList'),
    historyPanel: document.querySelector('.history-panel'),
    
    // Feedback
    copyFeedback: document.getElementById('copyFeedback'),
    
    // Backend status
    backendStatus: document.getElementById('backendStatus'),
    
    // Loader
    btnLoader: document.querySelector('.btn-loader'),
    btnText: document.querySelector('.btn-text')
};

/* ============================================================================
   MAPEO DE COLORES POR FORTALEZA
   ============================================================================ */

const strengthColors = {
    'very_weak': { color: '#ef4444', label: 'Muy débil' },
    'weak': { color: '#f97316', label: 'Débil' },
    'reasonable': { color: '#f59e0b', label: 'Razonable' },
    'strong': { color: '#84cc16', label: 'Fuerte' },
    'very_strong': { color: '#10b981', label: 'Muy fuerte' }
};

const strengthWidths = {
    'very_weak': 20,
    'weak': 40,
    'reasonable': 60,
    'strong': 80,
    'very_strong': 100
};

/* ============================================================================
   EVENT LISTENERS
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    console.log('✓ DOM cargado');
    initializeApp();
    checkBackendStatus();
});

// Actualizar valor del slider
DOM.length.addEventListener('input', (e) => {
    DOM.lengthValue.textContent = e.target.value;
});

// Botón generar
DOM.generateBtn.addEventListener('click', generatePassword);

// Botón regenerar
DOM.regenerateBtn.addEventListener('click', () => {
    generatePassword();
});

// Botón copiar
DOM.copyBtn.addEventListener('click', copyToClipboard);

// Botón limpiar historial
DOM.clearHistoryBtn.addEventListener('click', clearHistory);

/* ============================================================================
   FUNCIONES PRINCIPALES
   ============================================================================ */

/**
 * Inicializa la aplicación
 */
function initializeApp() {
    console.log('Inicializando aplicación...');
    renderHistory();
    
    // Verificar que al menos un tipo de carácter esté seleccionado
    const checkboxes = [
        DOM.useUppercase,
        DOM.useLowercase,
        DOM.useDigits,
        DOM.useSymbols
    ];
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', validateCheckboxes);
    });
    
    console.log('✓ Aplicación inicializada');
}

/**
 * Valida que al menos un tipo de carácter esté seleccionado
 */
function validateCheckboxes() {
    const checked = [
        DOM.useUppercase.checked,
        DOM.useLowercase.checked,
        DOM.useDigits.checked,
        DOM.useSymbols.checked
    ].some(c => c === true);
    
    DOM.generateBtn.disabled = !checked;
    
    if (!checked) {
        showError('Debes seleccionar al menos un tipo de carácter');
    } else {
        hideError();
    }
}

/**
 * Verifica el estado del Backend
 */
async function checkBackendStatus() {
    try {
        const response = await fetch(BACKEND_HEALTH_URL, {
            method: 'GET',
            mode: 'cors'
        });
        
        if (response.ok) {
            DOM.backendStatus.textContent = 'Conectado';
            DOM.backendStatus.className = 'status-online';
            console.log('✓ Backend activo');
        } else {
            setBackendOffline();
        }
    } catch (error) {
        setBackendOffline();
    }
}

/**
 * Marca el backend como desconectado
 */
function setBackendOffline() {
    DOM.backendStatus.textContent = 'Desconectado';
    DOM.backendStatus.className = 'status-offline';
    console.warn('⚠ Backend desconectado');
    showError('No se puede conectar con el Backend. Verifica que esté ejecutándose en http://localhost:8000');
}

/**
 * Genera una nueva contraseña
 */
async function generatePassword() {
    console.log('Generando contraseña...');
    
    // Validar
    if (!validateCheckboxes) {
        return;
    }
    
    // Mostrar loader
    setLoading(true);
    hideError();
    
    try {
        // Construir payload
        const payload = {
            length: parseInt(DOM.length.value),
            useUppercase: DOM.useUppercase.checked,
            useLowercase: DOM.useLowercase.checked,
            useDigits: DOM.useDigits.checked,
            useSymbols: DOM.useSymbols.checked,
            excludeAmbiguous: DOM.excludeAmbiguous.checked
        };
        
        console.log('📤 Enviando al Backend:', payload);
        
        // Hacer petición
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        // Manejar respuesta
        if (!response.ok) {
            const errorData = await response.json();
            
            if (response.status === 429) {
                throw new Error('Demasiadas solicitudes. Espera 1 minuto e intenta de nuevo.');
            } else if (response.status === 400) {
                throw new Error(`Error de validación: ${errorData.detail}`);
            } else if (response.status === 500) {
                throw new Error('Error en el servidor. Intenta de nuevo.');
            } else {
                throw new Error(`Error ${response.status}: ${errorData.detail}`);
            }
        }
        
        // Procesar respuesta exitosa
        const data = await response.json();
        console.log('📥 Respuesta del Backend:', data);
        
        // Guardar en estado
        appState.currentPassword = data;
        
        // Actualizar UI
        displayPassword(data);
        addToHistory(data);
        showSuccessMessage();
        
        console.log('✓ Contraseña generada exitosamente');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        showError(error.message);
        setBackendOffline();
    } finally {
        setLoading(false);
    }
}

/**
 * Muestra la contraseña en la interfaz
 */
function displayPassword(passwordData) {
    console.log('Mostrando contraseña...');
    
    // Mostrar panel de resultado
    DOM.resultPanel.style.display = 'block';
    
    // Llenar campo de contraseña
    DOM.passwordOutput.value = passwordData.password;
    
    // Mostrar fortaleza
    const strength = passwordData.strength;
    const strengthInfo = strengthColors[strength] || strengthColors['very_weak'];
    
    DOM.strengthText.textContent = strengthInfo.label;
    DOM.strengthText.style.color = strengthInfo.color;
    
    DOM.strengthIndicator.style.width = strengthWidths[strength] + '%';
    DOM.strengthIndicator.style.background = strengthInfo.color;
    
    // Mostrar entropía
    DOM.entropyText.textContent = `Entropía: ${passwordData.entropyBits} bits`;
    
    // Mostrar información
    DOM.infoLength.textContent = passwordData.length;
    DOM.infoAlphabet.textContent = passwordData.alphabetSize;
    DOM.infoEntropy.textContent = `${passwordData.entropyBits} bits`;
    
    // Habilitar botón regenerar
    DOM.regenerateBtn.disabled = false;
    
    console.log('✓ Contraseña mostrada en UI');
}

/**
 * Copia la contraseña al portapapeles
 */
async function copyToClipboard() {
    if (!appState.currentPassword) return;
    
    try {
        await navigator.clipboard.writeText(DOM.passwordOutput.value);
        console.log('✓ Contraseña copiada al portapapeles');
        
        // Mostrar feedback
        DOM.copyFeedback.style.display = 'block';
        setTimeout(() => {
            DOM.copyFeedback.style.display = 'none';
        }, 2000);
        
    } catch (error) {
        console.error('❌ Error al copiar:', error);
        showError('No se pudo copiar al portapapeles');
    }
}

/**
 * Agrega una contraseña al historial
 */
function addToHistory(passwordData) {
    const historyItem = {
        password: passwordData.password,
        strength: passwordData.strength,
        entropyBits: passwordData.entropyBits,
        timestamp: new Date().toLocaleTimeString()
    };
    
    appState.history.unshift(historyItem);
    
    // Limitar a 10 últimas contraseñas
    if (appState.history.length > 10) {
        appState.history.pop();
    }
    
    // Guardar en localStorage
    localStorage.setItem('passwordHistory', JSON.stringify(appState.history));
    
    // Mostrar historial
    if (appState.history.length > 0) {
        DOM.historyPanel.style.display = 'block';
    }
    
    renderHistory();
    console.log('✓ Contraseña agregada al historial');
}

/**
 * Renderiza el historial en la UI
 */
function renderHistory() {
    DOM.historyList.innerHTML = '';
    
    appState.history.forEach(item => {
        const strengthInfo = strengthColors[item.strength];
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        historyItem.innerHTML = `
            <span class="history-password">${item.password}</span>
            <span class="history-strength" style="background: ${strengthInfo.color}20; color: ${strengthInfo.color}">
                ${strengthInfo.label}
            </span>
            <span class="history-time">${item.timestamp}</span>
        `;
        
        DOM.historyList.appendChild(historyItem);
    });
}

/**
 * Limpia el historial
 */
function clearHistory() {
    if (confirm('¿Estás seguro de que quieres limpiar el historial?')) {
        appState.history = [];
        localStorage.removeItem('passwordHistory');
        DOM.historyPanel.style.display = 'none';
        renderHistory();
        console.log('✓ Historial limpiado');
    }
}

/* ============================================================================
   FUNCIONES DE UI
   ============================================================================ */

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    DOM.errorMessage.textContent = `❌ ${message}`;
    DOM.errorMessage.style.display = 'block';
    appState.lastError = message;
}

/**
 * Oculta el mensaje de error
 */
function hideError() {
    DOM.errorMessage.style.display = 'none';
    appState.lastError = null;
}

/**
 * Muestra un mensaje de éxito
 */
function showSuccessMessage() {
    console.log('✓ Éxito');
}

/**
 * Establece el estado de carga
 */
function setLoading(isLoading) {
    appState.isLoading = isLoading;
    DOM.generateBtn.disabled = isLoading;
    DOM.btnLoader.style.display = isLoading ? 'inline-block' : 'none';
    DOM.btnText.style.display = isLoading ? 'none' : 'inline';
}

/* ============================================================================
   VERIFICACIÓN DE COMPATIBILIDAD
   ============================================================================ */

console.log('🔐 Generador Seguro de Contraseñas - Frontend v1.0.0');
console.log('Backend URL:', API_URL);
console.log('Navegador:', navigator.userAgent.split(' ').slice(-2).join(' '));