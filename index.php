<html>
<head>
    <link rel="stylesheet" type="text/css" href="style.css">
    <meta http-equiv="refresh" content="30">
    <script>
    function startTime() {
        var weekdays = ['Sunnuntai', 'Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai'];
        var today = new Date();
        var dayName = weekdays[today.getDay()];
        var d = today.getDate();
        var mo = today.getMonth()+1;
        var y = today.getFullYear();
        var h = today.getHours();
        var m = today.getMinutes();
        var s = today.getSeconds();
        m = checkTime(m);
        s = checkTime(s);
        document.getElementById('clock').innerHTML =
        dayName + " " + d + "." + mo + "." + y + " " + h + ":" + m + ":" + s;
        var t = setTimeout(startTime, 500);
    }
    function checkTime(i) {
        if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
        return i;
    }
    </script>
</head>
<body onload="startTime()">
<a href="index.php?p=1"></a>
<a href="index.php?p=2"></a>
<a href="index.php?p=3"></a>
<div id="content">
<p id="clock"></p>
<br>
<?php
function parse_weather_data($json_all, $column)
{
    $weather_syms_path = "svgs/";

    echo "<div id='column'>";

    foreach ($json_all as $key => $value) {
        if ($value['column'] == $column)
        {
            echo "<p id='elem'>";
            echo $value['weekday_short'] . " ";
            echo $value['time'] . ": ";
            echo $value['temperature'] . "&#8451; ";
            if ($value['night'] == 'True')
            {
                if (strlen($value['wsymbol']) == 1)
                {
                    $n_prefix = "10";
                }
                else
                {
                    $n_prefix = "1";
                }
            }
            else
            {
                $n_prefix = "";
            }
            echo "<img id='weather-icon' src='" . $weather_syms_path . $n_prefix . $value['wsymbol'] . ".svg' />";
            echo "</p>";
        }
    }

    echo "</div>";
}
$json_db_file = "weather_data.json";

if ($_GET["p"] == "1")
{
    echo "jee";
}
elseif ($_GET["p"] == "2")
{
    echo "Sivu 2 tassa!";
}
else
{
    $json_content = file_get_contents($json_db_file);
    $json_a = json_decode($json_content, true);

    parse_weather_data($json_a, "left");
    parse_weather_data($json_a, "right");

    foreach ($json_a as $key => $value)
    {
        if ($value['updated'])
        {
            $updated = $value['updated'];
        }
    }
    echo "<div id='footer'>Viimeisin päivitys: " . $updated . "</div>";
}
?>
</div>
</body>
</html>