let championJson = {};

async function getLatestDDragon() {
    try {
        const versionsResponse = await fetch("https://ddragon.leagueoflegends.com/api/versions.json");
        if (!versionsResponse.ok) throw new Error("Failed to fetch versions");

        const versions = await versionsResponse.json();
        const latest = versions[0];

        const ddragonResponse = await fetch(`https://ddragon.leagueoflegends.com/cdn/${latest}/data/en_US/champion.json`);
        if (!ddragonResponse.ok) throw new Error("Failed to fetch champion data");

        const champions = await ddragonResponse.json();
        championJson = champions.data; // Armazena apenas os dados dos campeões
        return championJson;
    } catch (error) {
        console.error("Error fetching data:", error);
        document.getElementById("champions-list").innerHTML = "<p>Error loading data. Please try again later.</p>";
    }
}

async function getChampionByKey(key) {
    const champions = await getLatestDDragon();
    if (!champions) return false;

    for (let championName in champions) {
        if (!champions.hasOwnProperty(championName)) {continue;}
        if (champions[championName]["key"] === key.toString()) {
            return champions[championName];
        }
    }
    return false;
}

function displayChampionInfo(champion) {
    const championsListDiv = document.getElementById("champions-list");
    if (champion) {
        const iconUrl = `https://ddragon.leagueoflegends.com/cdn/img/champion/${champion.image.full}`;
        championsListDiv.innerHTML = `
            <h2>${champion.name} (${champion.title})</h2>
            <img src="https://lolcdn.darkintaqt.com/cdn/champion/${champion.key}/tile" alt="${champion.name} icon" style="width: 100px; height: 100px;">
            <p><strong>Blurb:</strong> ${champion.blurb}</p>
            <p><strong>Tags:</strong> ${champion.tags.join(", ")}</p>
            <p><strong>Partype:</strong> ${champion.partype}</p>
        `;
    } else {
        championsListDiv.innerHTML = `<p>Champion not found.</p>`;
    }
}

async function main() {
    const champion = await getChampionByKey(45); // 45 é a chave do Veigar
    displayChampionInfo(champion);
}

main();
