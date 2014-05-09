function updateMaintainers() {
    var checkbox = document.getElementById("showMaintainers");
    if (checkbox.checked) {
        $(".framework-maintainer").show();
    } else {
        $(".framework-maintainer").hide();
    }
}

function updatePlatforms() {
    var doFilter = document.getElementById("platform-filter").checked;
    if (doFilter) {
        $("#platform-filter-group").show();
    } else {
        $("#platform-filter-group").hide();
        $(".framework-row").removeClass("not-available").removeClass("available");
        return;
    }

    var platformCheckboxes = $(".platform-checkbox");
    var wantedPlatforms = [];
    platformCheckboxes.each(function(idx, checkbox) {
        if (checkbox.checked) {
            var platform = checkbox.getAttribute("data-platform");
            wantedPlatforms.push(platform);
        }
    });
    $(".framework-row").each(function(idx, tr) {
        var fwPlatforms = tr.getAttribute("data-platforms").split(",");
        var show = wantedPlatforms.every(function(platform) {
            return fwPlatforms.indexOf(platform) != -1;
        });
        if (show) {
            $(tr).removeClass("not-available").addClass("available");
        } else {
            $(tr).removeClass("available").addClass("not-available");
        }
    });
}

function main() {
    $("#showMaintainers").click(updateMaintainers);
    $("#platform-filter").click(updatePlatforms);
    $(".platform-checkbox").click(updatePlatforms);
    updateMaintainers();
}
