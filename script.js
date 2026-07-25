async function queryAPI() {
    let url = 'data.json';
    try {
        let res = await fetch(url + '?t=' + Date.now());  // cache-buster: always fetch fresh data
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}

function hideSpinners() {
    //disable spinners (all present, regardless of numbering)
    document.querySelectorAll('[id^="spinner"]').forEach(function (s) {
        s.style.display = "none";
    });
}

async function updateBoxes() {

    try {
        let data = await queryAPI();
        // on a failed fetch, leave existing values but still clear the spinners (finally)
        if (!data) return;
        //update box-values
        var datetime = new Date(data["datetime"]);
        var options = {
            timeZone: "Europe/Berlin",
            hour12: false,
            year: "2-digit",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        };
        var formattedDatetime = datetime.toLocaleString("de-DE", options);

        document.querySelector("#datetime").innerHTML = " " + formattedDatetime + " Ortszeit";
        document.querySelector("#temperature").innerHTML = '<span">' + data["temperature"]["string"] + ' °C</span>';
        document.querySelector("#dewpoint").innerHTML = '<span">' + data["dewpoint"]["string"] + ' °C</span>';
        document.querySelector("#humidity").innerHTML = '<span">' + data["humidity"]["value"] + '</span><span class="mobile-font""> %</span>';
        document.querySelector("#pressure").innerHTML = '<span">' + data["pressure"]["value"] + '</span><span class="mobile-font""> hPa</span>';
        document.querySelector("#ground-pressure").innerHTML = data["ground-pressure"]["value"] + " " + data["ground-pressure"]["unit"]
        document.querySelector("#speed").innerHTML = '<span">' + data["wind_speed"]["string"] + '</span><span class="mobile-font""> km/h</span>';
        document.querySelector("#direction").innerHTML = '<span class="mobile-font">' + data["wind_direction"]["string"] + '</span>';
        document.querySelector("#strahl").innerHTML = '<span">' + data["global_radiation"]["string"] + '</span><span class="mobile-font""> W/m²</span>';
        document.querySelector("#precip").innerHTML = '<span">' + data["precip_1h"]["string"] + '</span><span class="mobile-font""> mm</span>';
        var cbhStr = data["cbh"]["string"];
        if (cbhStr.startsWith("keine ")) {
            // shorten 'keine Daten' / 'keine Wolke' to just 'keine' on small screens
            cbhStr = 'keine<span class="hide-mobile"> ' + cbhStr.slice(6) + '</span>';
        }
        document.querySelector("#cbh").innerHTML = '<span">' + cbhStr + '</span>';
    } finally {
        hideSpinners();
    }

}

updateBoxes()

setInterval(function () {
    updateBoxes()
}, 30000);
