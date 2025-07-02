document.addEventListener('DOMContentLoaded', function() {
    // Adicionar ao carrinho com quantidade
    const formsCarrinho = document.querySelectorAll('form[action^="/carrinho/adicionar"]');
    formsCarrinho.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const quantidade = this.querySelector('input[name="quantidade"]').value;
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `quantidade=${quantidade}`
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        });
    });

    // Atualizar carrinho sem recarregar a página
    const formsAtualizar = document.querySelectorAll('form[action^="/carrinho/atualizar"]');
    formsAtualizar.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        });
    });
});