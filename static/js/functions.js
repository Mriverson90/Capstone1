
////// News functions //////

// Roto News 
async function getNews(){
    try{
        const res = await axios.get('https://api.sportsdata.io/v3/nfl/scores/json/News?key=c47a6083958840289435307cb1b9297c');
        renderNews(res.data);
    } catch (e){
        alert("Something went wrong")
    }
}
function renderNews(news){
    const ul = document.querySelector("#news");
    for(let article of news){
        ul.append(makeNewsLI(article));
    }
}
function makeNewsLI(article){
    const newLi = document.createElement('LI');
    const title = document.createElement('A');
    title.setAttribute('href', `${article.Url}`);
    title.innerText = article.Title;
    newLi.append(title);
    return newLi;
}

// ESPN News //
async function getEspnNews(){
    try{
        const res = await axios.get('http://site.api.espn.com/apis/site/v2/sports/football/nfl/news');
        renderEspnNews(res.data.articles)
    } catch(e){
        alert('Something went wrong')
    }
}
function renderEspnNews(res){
    const ul = document.querySelector("#espnNews");
    for(let article of res){
        ul.append(makeEspnNewsLI(article));
    }
}
function makeEspnNewsLI(article){
    const newLi = document.createElement('LI');
    const title = document.createElement('A');
    title.setAttribute('href', `${article.links.web}`);
    title.innerText = article.headline;
    newLi.append(title);
    return newLi;
}
////// Get Player By Name Function - Need reduce to seperate functions //////
async function getPlayerByName(name){
    const players = await axios.get('https://api.sportsdata.io/v3/nfl/scores/json/Players?key=c47a6083958840289435307cb1b9297c');
    const ul = document.querySelector('#playerUL');
    const nameLI = document.createElement('LI');
    for(let player of players.data){
        if(player.Name.toLowerCase() === name.toLowerCase()){
            console.log(player.Name);
            nameLI.innerText = player.Name;
            ul.append(nameLI);
            // renderPlayerByName(players)
        }
    }
}

const form2 = document.querySelector('#nameSearch');
form2.addEventListener('submit', function(e){
    const input = document.querySelector('#playerName');
    e.preventDefault();
    getPlayerByName(input.value);
    input.value = '';
})
////// Get Player By id //////
async function trySomething(id){
    const playerInfo = await axios.get(`https://api.sportsdata.io/v3/nfl/scores/json/Player/${id}?key=c47a6083958840289435307cb1b9297c`);
    console.log(playerInfo.data);
    console.log(`Name: ${playerInfo.data.Name}`);
    console.log(`Number: ${playerInfo.data.Number}`);
    console.log(`Age: ${playerInfo.data.Age}`);
}
////// Get Fantasy Players - Offensive players (QB,RB,WR,TE,K) //////
async function getFantasyPlayers(){
    const players = await axios.get('https://api.sportsdata.io/v3/nfl/scores/json/Players?key=c47a6083958840289435307cb1b9297c');
    for(let player of players.data){
        if(player.Position === "K" || player.Position === "QB" || player.Position === "RB" || player.Position === "WR" || player.Position === "TE"){
            console.log(player.Name)
        }
    }
}

