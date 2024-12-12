let championImageJson = {};

function getApiKeyFromSession() {
    return sessionStorage.getItem("apiKey");
}

async function getLatestDDragon() {
    try {
        const versionsResponse = await fetch("https://ddragon.leagueoflegends.com/api/versions.json");
        if (!versionsResponse.ok) throw new Error("Failed to fetch versions");

        const versions = await versionsResponse.json();
        const latest = versions[0];

        const ddragonResponse = await fetch(`https://ddragon.leagueoflegends.com/cdn/${latest}/data/en_US/champion.json`);
        if (!ddragonResponse.ok) throw new Error("Failed to fetch champion data");

        const champions = await ddragonResponse.json();
        championImageJson = champions.data; 
        return championImageJson;
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

async function getFeaturedGames() {
    try {
        const apiKey = getApiKeyFromSession();
        if (!apiKey) throw new Error("API key not found in session storage");

        const response = await fetch(`https://br1.api.riotgames.com/lol/spectator/v5/featured-games?api_key=${apiKey}`);
        if (!response.ok) throw new Error("Failed to fetch featured games");

        const gamesData = await response.json();
        return gamesData;
    } catch (error) {
        console.error("Error fetching featured games:", error);
        return null;
    }
}

async function getChampionByKey(key) {
    if (!championImageJson || Object.keys(championImageJson).length === 0) {
        await getLatestDDragon();
    }

    for (let championName in championImageJson) {
        if (championImageJson[championName]["key"] === key.toString()) {
            return championImageJson[championName];
        }
    }
    return null;
}

const createTeamHtml = async (team, className) => {
    return Promise.all(
        team.map(async (participant) => {
            const time = participant.teamId;
            const championId = participant.championId;
            const riotId = participant.riotId; 
            const championInfo = await getChampionByKey(championId);

            if (championInfo && time === 100) {
                return `
                    <div class="card-jogador-${className}">
                        <p>${riotId}</p>
                        <img src="https://lolcdn.darkintaqt.com/cdn/champion/${championInfo.key}/tile" alt="${championInfo.name}" />
                    </div>
                `;
            } 
            else if (championInfo && time === 200) {
                return `
                    <div class="card-jogador-${className}">
                        <img src="https://lolcdn.darkintaqt.com/cdn/champion/${championInfo.key}/tile" alt="${championInfo.name}" />
                        <p>${riotId}</p>
                    </div>
                `;
            } else {
                return `
                    <div class="card-jogador-${className}">
                        <p>${riotId}</p>
                        <p>Champion not found</p>
                    </div>
                `;
            }
        })
    );
};

async function replaceChampionIdsWithNamesForGames() {
    const featuredGames = await getFeaturedGames();
    if (!featuredGames) return;

    //const gameList = featuredGames.gameList.filter(game => game.gameMode !== "ARAM");
    const gameList = featuredGames.gameList;

    let allGamesHtml = ""; 

    for (let i = 0; i < gameList.length; i++) {
        const game = gameList[i];
        const gameParticipants = game.participants;

        const blueTeam = gameParticipants.filter(participant => participant.teamId === 100);
        const redTeam = gameParticipants.filter(participant => participant.teamId === 200);

        const blueTeamHtml = (await createTeamHtml(blueTeam, "azul")).join("");
        const redTeamHtml = (await createTeamHtml(redTeam, "vermelho")).join("");

        allGamesHtml += `
            <div class="card partida-card">
                <div class="card vitoria-azul">
                    <div class="card-titulo">
                     <p>Ranqueada Solo/Duo</p>
                    </div>
                    <div class="card-jogadores">
                        <div id="blue-team-${i}" class="team">
                            ${blueTeamHtml}
                        </div>
                        <div id="red-team-${i}" class="team">
                            ${redTeamHtml}
                        </div>                           
                    </div>
                </div>
            </div>
        `;
    }

    document.getElementById("featured-games").innerHTML = allGamesHtml;
}



async function main() {
    await getLatestDDragon(); 
    await replaceChampionIdsWithNamesForGames();
}

main();
