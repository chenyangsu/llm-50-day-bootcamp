// Task checkboxes persist to localStorage; the banner works out which day you are on.
// This file is inlined into every page by scripts/build.py -- it must not contain a
// literal closing script tag.
(function () {
  "use strict";
  var KEY = "llm50:";

  function pageKey() {
    var m = location.pathname.match(/([^/]+)\.html?$/);
    return m ? m[1] : "index";
  }

  function todayISO() {
    var d = new Date();
    function p(n) { return (n < 10 ? "0" : "") + n; }
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate());
  }

  function currentDay() {
    var today = todayISO();
    var last = BOOTCAMP_DAYS[BOOTCAMP_DAYS.length - 1];
    if (today < BOOTCAMP_START) return { state: "before", day: BOOTCAMP_DAYS[0] };
    if (today > last.date) return { state: "after", day: last };
    for (var i = 0; i < BOOTCAMP_DAYS.length; i++) {
      if (BOOTCAMP_DAYS[i].date === today) return { state: "on", day: BOOTCAMP_DAYS[i] };
    }
    return { state: "after", day: last };
  }

  function dayHref(day) {
    var prefix = /\/days\//.test(location.pathname) ? "" : "days/";
    return prefix + "day-" + (day.day < 10 ? "0" : "") + day.day + ".html";
  }

  function longDate(iso) {
    var parts = iso.split("-");
    var d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    return d.toLocaleDateString(undefined, {
      weekday: "long", day: "numeric", month: "long", year: "numeric"
    });
  }

  function renderBanner() {
    var host = document.getElementById("today-banner");
    if (!host) return;
    var cur = currentDay();
    var d = cur.day;
    var link = '<a href="' + dayHref(d) + '">Day ' + d.day + " — " + d.title + "</a>";
    if (cur.state === "before") {
      var setupHref = (/\/days\//.test(location.pathname) ? "../" : "") + "setup.html";
      host.innerHTML = "<strong>Starts " + longDate(BOOTCAMP_START) + ".</strong> First up: " + link +
        '. Tonight is for <a href="' + setupHref + '">setup</a>.';
    } else if (cur.state === "after") {
      host.innerHTML = "<strong>Finished " + longDate(d.date) + ".</strong> Last day was " + link + ".";
    } else {
      host.innerHTML = "<strong>Today is day " + d.day + " of " + BOOTCAMP_DAYS.length +
        ".</strong> " + link;
    }
    host.classList.add("live");
  }

  function markTimeline() {
    var table = document.querySelector(".timeline");
    if (!table) return;
    var today = todayISO();
    var rows = table.querySelectorAll("tr");
    for (var i = 0; i < rows.length; i++) {
      var a = rows[i].querySelector('a[href*="day-"]');
      if (!a) continue;
      var m = a.getAttribute("href").match(/day-(\d+)/);
      if (!m) continue;
      var num = Number(m[1]);
      var rec = null;
      for (var j = 0; j < BOOTCAMP_DAYS.length; j++) {
        if (BOOTCAMP_DAYS[j].day === num) { rec = BOOTCAMP_DAYS[j]; break; }
      }
      if (!rec) continue;
      if (rec.date < today) rows[i].classList.add("row-past");
      else if (rec.date === today) rows[i].classList.add("row-today");
    }
  }

  function wireTasks() {
    var boxes = document.querySelectorAll("input.task-check");
    if (!boxes.length) return;
    var page = pageKey();

    var bar = document.createElement("div");
    bar.className = "task-progress";
    bar.innerHTML = '<div class="task-progress-fill"></div><span class="task-progress-label"></span>';
    var firstList = document.querySelector(".task-list");
    firstList.parentNode.insertBefore(bar, firstList);
    var fill = bar.querySelector(".task-progress-fill");
    var label = bar.querySelector(".task-progress-label");

    function refresh() {
      var done = 0;
      for (var i = 0; i < boxes.length; i++) if (boxes[i].checked) done++;
      var pct = Math.round((done / boxes.length) * 100);
      fill.style.width = pct + "%";
      label.textContent = done + " of " + boxes.length + " done";
      bar.classList.toggle("complete", done === boxes.length);
    }

    Array.prototype.forEach.call(boxes, function (box, i) {
      var storeKey = KEY + page + ":" + i;
      var wrap = box.closest(".task");
      if (localStorage.getItem(storeKey) === "1") {
        box.checked = true;
        if (wrap) wrap.classList.add("done");
      }
      box.addEventListener("change", function () {
        localStorage.setItem(storeKey, box.checked ? "1" : "0");
        if (wrap) wrap.classList.toggle("done", box.checked);
        refresh();
      });
    });

    refresh();
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    try { renderBanner(); } catch (e) {}
    try { markTimeline(); } catch (e) {}
    try { wireTasks(); } catch (e) {}
  });
})();
