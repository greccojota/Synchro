/**
 * Address Search Module
 * Handles CEP lookup and geolocation functionality
 */
class AddressSearch {
    constructor() {
        this.localInput = document.getElementById('local');
        this.searchCepBtn = document.getElementById('searchCep');
        this.useLocationBtn = document.getElementById('useLocation');
        this.addressSuggestions = document.getElementById('addressSuggestions');
        this.addressDetails = document.getElementById('addressDetails');
        this.addressInfo = this.addressDetails?.querySelector('.address-info');
        
        if (this.localInput) {
            this.initEventListeners();
        }
    }

    initEventListeners() {
        this.searchCepBtn?.addEventListener('click', () => this.searchByCep());
        this.useLocationBtn?.addEventListener('click', () => this.useGeolocation());
        this.localInput.addEventListener('input', (e) => this.handleInput(e));
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.address-search-container')) {
                this.hideSuggestions();
            }
        });
    }

    async searchByCep() {
        const input = this.localInput.value.trim();
        const cepPattern = /^\d{5}-?\d{3}$/;
        
        if (!cepPattern.test(input.replace(/\D/g, ''))) {
            this.showError('Digite um CEP válido (ex: 01234-567)');
            return;
        }

        const cep = input.replace(/\D/g, '');
        this.setLoading(true);

        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await response.json();

            if (data.erro) {
                this.showError('CEP não encontrado');
                return;
            }

            this.displayAddressInfo(data);
            this.localInput.value = this.formatFullAddress(data);
        } catch (error) {
            this.showError('Erro ao buscar CEP. Tente novamente.');
        } finally {
            this.setLoading(false);
        }
    }

    async useGeolocation() {
        if (!navigator.geolocation) {
            this.showError('Geolocalização não suportada pelo navegador');
            return;
        }

        this.setLoading(true, 'Obtendo localização...');

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                try {
                    const { latitude, longitude } = position.coords;
                    
                    const response = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&addressdetails=1`
                    );
                    const data = await response.json();

                    if (data && data.display_name) {
                        this.displayLocationInfo(data);
                        this.localInput.value = this.formatLocationAddress(data);
                    } else {
                        this.showError('Não foi possível obter o endereço da localização');
                    }
                } catch (error) {
                    this.showError('Erro ao obter endereço da localização');
                } finally {
                    this.setLoading(false);
                }
            },
            (error) => {
                this.setLoading(false);
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        this.showError('Permissão de localização negada');
                        break;
                    case error.POSITION_UNAVAILABLE:
                        this.showError('Localização indisponível');
                        break;
                    case error.TIMEOUT:
                        this.showError('Timeout ao obter localização');
                        break;
                    default:
                        this.showError('Erro desconhecido ao obter localização');
                        break;
                }
            }
        );
    }

    handleInput(e) {
        const value = e.target.value.trim();
        
        // Auto-format CEP
        if (/^\d{5}$/.test(value)) {
            e.target.value = value + '-';
        }
        
        // Hide details when input changes
        this.hideAddressDetails();
    }

    displayAddressInfo(data) {
        if (!this.addressInfo) return;
        
        this.addressInfo.innerHTML = `
            <div><strong>CEP:</strong> ${data.cep}</div>
            <div><strong>Logradouro:</strong> ${data.logradouro}</div>
            <div><strong>Bairro:</strong> ${data.bairro}</div>
            <div><strong>Cidade:</strong> ${data.localidade}</div>
            <div><strong>Estado:</strong> ${data.uf}</div>
        `;
        this.showAddressDetails();
    }

    displayLocationInfo(data) {
        if (!this.addressInfo) return;
        
        const address = data.address;
        this.addressInfo.innerHTML = `
            <div><strong>Endereço:</strong> ${data.display_name}</div>
            <div><strong>Cidade:</strong> ${address.city || address.town || address.village || 'N/A'}</div>
            <div><strong>Estado:</strong> ${address.state || 'N/A'}</div>
            <div><strong>País:</strong> ${address.country || 'N/A'}</div>
        `;
        this.showAddressDetails();
    }

    formatFullAddress(data) {
        let address = '';
        if (data.logradouro) address += data.logradouro;
        if (data.bairro) address += (address ? ', ' : '') + data.bairro;
        if (data.localidade) address += (address ? ', ' : '') + data.localidade;
        if (data.uf) address += (address ? ' - ' : '') + data.uf;
        if (data.cep) address += (address ? ' - CEP: ' : 'CEP: ') + data.cep;
        return address;
    }

    formatLocationAddress(data) {
        return data.display_name;
    }

    showAddressDetails() {
        if (this.addressDetails) {
            this.addressDetails.style.display = 'block';
        }
    }

    hideAddressDetails() {
        if (this.addressDetails) {
            this.addressDetails.style.display = 'none';
        }
    }

    hideSuggestions() {
        if (this.addressSuggestions) {
            this.addressSuggestions.style.display = 'none';
        }
    }

    setLoading(loading, message = 'Buscando...') {
        if (!this.searchCepBtn || !this.useLocationBtn) return;
        
        if (loading) {
            this.searchCepBtn.disabled = true;
            this.useLocationBtn.disabled = true;
            this.searchCepBtn.innerHTML = `<i data-feather="loader"></i> ${message}`;
        } else {
            this.searchCepBtn.disabled = false;
            this.useLocationBtn.disabled = false;
            this.searchCepBtn.innerHTML = `<i data-feather="search"></i> Buscar CEP`;
        }
        
        // Reinitialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.style.marginTop = '0.5rem';
        errorDiv.innerHTML = `<strong>Erro:</strong> ${message}`;
        
        const container = document.querySelector('.address-search-container');
        if (container) {
            container.appendChild(errorDiv);
            
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 5000);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AddressSearch();
});