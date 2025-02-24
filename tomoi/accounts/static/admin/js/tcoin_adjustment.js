document.addEventListener('DOMContentLoaded', function() {
    const tcoinInput = document.querySelector('#id_tcoin');
    const descInput = document.querySelector('#id_description');
    
    if (tcoinInput) {
        tcoinInput.addEventListener('change', function() {
            const oldValue = parseInt(this.defaultValue);
            const newValue = parseInt(this.value);
            const change = newValue - oldValue;
            
            if (!descInput.value && change !== 0) {
                descInput.value = `Admin điều chỉnh ${change > 0 ? '+' : ''}${change} TCoin`;
            }
        });
    }
}); 