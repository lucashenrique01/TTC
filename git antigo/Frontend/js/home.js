
document.getElementById("pesquisa-jogador").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Extrai o nome do jogador e a tag da barra de pesquisa
    const pesquisaInput = document.getElementById("barra_pesquisa").value;
    const [nomeJogador, tag] = pesquisaInput.split('#');
    sessionStorage.setItem("nomeJogador",nomeJogador);
    sessionStorage.setItem("tag",tag);

    // Verifica se o formato de entrada é válido
    if (!nomeJogador || !tag) {
        alert("Por favor, insira o nome do jogador seguido de # e a tag.");
        return;
    }

    // Monta a URL com os parâmetros apropriados
    const apiKey = sessionStorage.getItem("apiKey");
    const uri = `https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${nomeJogador}/${tag}?api_key=${apiKey}`;

    try {
        // Faz a chamada à API
        const response = await fetch(uri);
        if (!response.ok) throw new Error("Não foi possível encontrar o jogador.");

        // Converte a resposta para JSON e salva o `puuid` no `sessionStorage`
        const data = await response.json();
        sessionStorage.setItem("puuid", data.puuid);

        alert("Puuid salvo com sucesso!");
        // Aqui você pode chamar outras funções para usar o `puuid` conforme necessário

    } catch (error) {
        console.error("Erro ao buscar o puuid:", error);
        alert("Erro ao buscar o puuid. Verifique o nome do jogador e tag.");
    }
});