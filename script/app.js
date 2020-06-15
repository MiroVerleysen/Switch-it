const lanIP = `${window.location.hostname}:5000`;
const socketio = io(lanIP);
let stroomChart;
let vermogenChart;

//#region ***  DOM references ***

//#endregion

//#region ***  Callback-Visualisation - show___ ***
const showRecentStroom = function (jsonObject) {
  console.log(jsonObject);
  let waarden = jsonObject.data;
  let htmlString = '';
  for (let item of waarden) {
    htmlString += `<li>sensor ID: ${item.sensorID} - waarde: ${item.waarde} Ampère - tijd: ${item.tijd}</li>`;
  }

  document.querySelector('.js-placeholder-stroom-recent').innerHTML = htmlString;
};

const showStroomChart = function (jsonObject) {
  let dates = []
  let waardes = []
  jsonObject.data.forEach(element => {
    dates.push(element.datum)
  });
  jsonObject.data.forEach(element => {
    waardes.push(element.waarde)
  });
  const ctx = document.getElementById("stroomChart");
  stroomChart.data.datasets[0].data = waardes;
  stroomChart.data.labels = dates;
  stroomChart.update();
}

const showVermogenChart = function (jsonObject) {
  let dates = []
  let waardes = []
  jsonObject.data.forEach(element => {
    dates.push(element.datum)
  });
  jsonObject.data.forEach(element => {
    waardes.push(element.waarde * 230)
  });
  vermogenChart.data.datasets[0].data = waardes;
  vermogenChart.data.labels = dates;
  vermogenChart.update();

}

const showGepland = function (jsonObject) {
  console.log(jsonObject);
  let waarden = jsonObject.data;
  let htmlString = '';
  let status = ""
  let tijdstip = ""
  for (let item of waarden) {
    if (item.status == "0") {
      status = "uit"
    }
    else {
      status = "aan"
    }
    tijdstip = item.tijdstip
    tijdstip = tijdstip.slice(5, -7)
    htmlString += `<li>Om: ${tijdstip} uur gaat het stopcontact: <b class="paars">${status}</b>.</li>`;
  }

  document.querySelector('.js-placeholder-gepland').innerHTML = htmlString;
};
//#endregion

//#region ***  Callback-No Visualisation - callback___  ***
const callBackBijError = function (data) {
  console.log('oeps er is iets mis gegaan');
  console.log(data);
};
//#endregion

//#region ***  Data Access - get___ ***
const getRecentStroom = function () {
  var e = document.getElementById("Stroom");
  var strUser = e.options[e.selectedIndex].value;
  //STAP A2 -> Roep de API op voor de data die je wil tonen
  handleData(`http://${window.location.host}:5000/read_sensor_recent/2.${strUser}`, showStroomChart, callBackBijError);
};

const getRecentVermogen = function () {
  var e = document.getElementById("Vermogen");
  var strUser = e.options[e.selectedIndex].value;
  //STAP A2 -> Roep de API op voor de data die je wil tonen
  handleData(`http://${window.location.host}:5000/read_sensor_recent/2.${strUser}`, showVermogenChart, callBackBijError);
};

const getGepland = function () {
  handleData(`http://${window.location.host}:5000/read_gepland_all`, showGepland, callBackBijError);
};
//#endregion

//#region ***  Event Listeners - listenTo___ ***
const listentoUI = function () {
  document.querySelector(".js-power-btn").addEventListener("click", function () {
    socketio.emit("F2B_schakelen")
  })

  document.querySelector(".js-plan-btn").addEventListener("click", function () {
    var aan = document.getElementById("js-timeaan").value;
    console.log(aan);
    var uit = document.getElementById("js-timeuit").value;
    console.log(uit);
    var today = new Date();
    var maand = 0;
    var dag = 0;
    var minuten = 0;
    var uur = 0;
    if (today.getMonth() + 1 < 10) {
      maand = ('0' + (today.getMonth() + 1)).slice(-2)
    }
    else {
      maand = (today.getMonth() + 1)
    }
    if (today.getDate() < 10) {
      dag = (('0' + today.getDate()).slice(-2))
    }
    else {
      dag = today.getDate()
    }
    var date = today.getFullYear() + '-' + maand + '-' + dag;
    if (today.getMinutes() < 10) {
      minuten = (('0' + today.getMinutes()).slice(-2))
    }
    else {
      minuten = today.getMinutes()
    }
    if (today.getHours() < 10) {
      uur = (('0' + today.getHours()).slice(-2))
    }
    else {
      uur = today.getHours()
    }
    var time = uur + ":" + minuten;
    var dateTime = date + 'T' + time;
    if (aan < uit) {
      if (dateTime + 1 < aan) {
        socketio.emit("F2B_plannen", `${aan};${uit}`);
        alert("Succesvol gepland.");
      }
      else {
        alert("De inschakel tijd kan niet voor het huidige tijdstip gepland staan.");
      }
    }
    else {
      alert("Zorg ervoor dat de uitschakeltijd later dan de inschakel tijd is.");
    }
  })

  document.querySelector(".js-stroom_dropdown").addEventListener("change", function () {

    let value = document.querySelector(".js-stroom_dropdown").options[document.querySelector(".js-stroom_dropdown").selectedIndex].value
    handleData(`http://${window.location.host}:5000/read_sensor_recent/2.${value}`, showStroomChart, callBackBijError);
  })

  document.querySelector(".js-vermogen_dropdown").addEventListener("change", function () {

    let value = document.querySelector(".js-vermogen_dropdown").options[document.querySelector(".js-vermogen_dropdown").selectedIndex].value
    handleData(`http://${window.location.host}:5000/read_sensor_recent/2.${value}`, showVermogenChart, callBackBijError);
  })
}

function toggleNav() {
  let toggleTrigger = document.querySelectorAll(".js-toggle-nav");
  for (let i = 0; i < toggleTrigger.length; i++) {
    toggleTrigger[i].addEventListener("touchstart", function () {
      document.querySelector("html").classList.toggle("has-mobile-nav");
    })
  }
}

//#endregion

const loadSocketListeners = function () {
  socketio.on("B2F_geschakeld", function (data) {
    console.log(data)
    if (data.status == 1) {
      document.querySelector(".js-power-btn").innerHTML = "Uitschakelen"
      document.querySelector(".js-power-btn").classList.remove("c-link-cta")
      document.querySelector(".js-power-btn").classList.add("c-link-cta_uitschakelen")
    }
    else {
      document.querySelector(".js-power-btn").innerHTML = "Inschakelen"
      document.querySelector(".js-power-btn").classList.add("c-link-cta")
      document.querySelector(".js-power-btn").classList.remove("c-link-cta_uitschakelen")
    }
  })
};

//#region ***  INIT / DOMContentLoaded  ***

const initCharts = function () {
  const ctx = document.getElementById("stroomChart");
  stroomChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: null,
      datasets: [{
        label: "Stroom (in Ampère)",
        data: null,
        borderColor: 'rgba(31, 120, 180)',
        pointBackgroundColor: 'rgba(31, 120, 180)',
        pointBorderWidth: 5,
        fill: 0
      }]
    },
    options: {
      legend: {
        display: false
      },
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          },
          scaleLabel: {
            display: true
          },
        }],
        xAxes: [{
          ticks: {
            autoSkip: true,
            maxTicksLimit: 10
          }
        }]
      }
    }

  })

  const ctx2 = document.getElementById("vermogenChart");
  vermogenChart = new Chart(ctx2, {
    type: 'line',
    data: {
      labels: null,
      datasets: [{
        label: "Vermogen (in Watt)",
        data: null,
        borderColor: 'rgba(31, 120, 180)',
        pointBackgroundColor: 'rgba(31, 120, 180)',
        pointBorderWidth: 5,
        fill: 0
      }]
    },
    options: {
      legend: {
        display: false
      },
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          },
          scaleLabel: {
            display: true
          },
        }],
        xAxes: [{
          ticks: {
            autoSkip: true,
            maxTicksLimit: 10
          }
        }]
      }
    }
  });
};

const init = function () {
  socketio.emit("F2B_getdata")
  socketio.on("B2F_sentdata", function (data) {
    if (data.status == 1) {
      document.querySelector(".js-power-btn").innerHTML = "Uitschakelen"
      document.querySelector(".js-power-btn").classList.remove("c-link-cta")
      document.querySelector(".js-power-btn").classList.add("c-link-cta_uitschakelen")
    }
    else {
      document.querySelector(".js-power-btn").innerHTML = "Inschakelen"
      document.querySelector(".js-power-btn").classList.add("c-link-cta")
      document.querySelector(".js-power-btn").classList.remove("c-link-cta_uitschakelen")
    }
  })
  initCharts();
  handleData(`http://${window.location.host}:5000/read_gepland_all`, showGepland, callBackBijError);
  getRecentStroom();
  getRecentVermogen();
  loadSocketListeners();
  listentoUI();
  socketio.on("B2F_newStroomData", function () {
    let value = document.querySelector(".js-stroom_dropdown").options[document.querySelector(".js-stroom_dropdown").selectedIndex].value
    handleData(`http://${window.location.host}:5000/read_sensor_recent/2.${value}`, showStroomChart, callBackBijError);

    let waarde = document.querySelector(".js-vermogen_dropdown").options[document.querySelector(".js-vermogen_dropdown").selectedIndex].value
    handleData(`http://${window.location.host}:5000/read_sensor_recent/2.${waarde}`, showVermogenChart, callBackBijError);
  })
  socketio.on("B2F_gepland", function () {
    handleData(`http://${window.location.host}:5000/read_gepland_all`, showGepland, callBackBijError);
  })
};


document.addEventListener('DOMContentLoaded', init);
document.addEventListener('DOMContentLoaded', function () {
  toggleNav();
})

//#endregion
