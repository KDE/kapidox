function updateMaintainers() {
    var checkbox = document.getElementById("showMaintainers");
    if (checkbox.checked) {
        $(".framework-maintainer-column").show();
    } else {
        $(".framework-maintainer-column").hide();
    }
}

function updatePlatforms() {
    var doFilter = document.getElementById("platform-filter").checked;
    $(".framework-platform").removeClass("framework-platform-required");
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
    for (var idx=0; idx < wantedPlatforms.length; ++idx) {
        var platform = wantedPlatforms[idx];
        $(".framework-platform-" + platform).addClass("framework-platform-required");
    };
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

var g_noteElement;
var g_currentlyDescribedElement;

function initNoteTip() {
    g_noteElement = document.createElement("div");
    $(g_noteElement).addClass("note-tip");
    $(g_noteElement).html("<span class='note-tip-text'></span> <a class='note-close' href='#'>&#9447;</a>");

    $("body").append(g_noteElement);

    $(".note-close", g_noteElement).click(function() {
        hideNoteTip();
        return false;
    });

    $(".platform-note").click(function() {
        if (g_currentlyDescribedElement == this) {
            hideNoteTip();
        } else {
            var text = this.getAttribute("data-note");
            showNoteTip(this, text);
        }
        return false;
    });
}

function showNoteTip(anchorElement, text) {
    g_currentlyDescribedElement = anchorElement;

    var offset = $(anchorElement).offset();
    var note = $(g_noteElement);
    $(".note-tip-text", note).text(text);
    note.css({
            left: (offset.left + $(anchorElement).width() / 2 - note.outerWidth(true) / 2) + "px",
            top: (offset.top - note.outerHeight(true) - 6) + "px"
        })
        .fadeIn();
}

function hideNoteTip() {
    g_currentlyDescribedElement = null;
    $(g_noteElement).fadeOut();
}

function main() {
    $("#showMaintainers").click(updateMaintainers);
    $("#platform-filter").click(updatePlatforms);
    $(".platform-checkbox").click(updatePlatforms);
    initNoteTip();
    updateMaintainers();
}
