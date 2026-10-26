/* Runs in <head> before paint (after the stylesheets): marks JS and motion support so CSS can hide reveal targets.
   html.fonts-in: the two web fonts are loaded (or 700 ms passed). The first screen's reveals ([data-intro]) are CSS
   animations that start on it, so they never wait for the JS bundle. The build marks the page's first <section>;
   markFold() below marks every other reveal already in the viewport at that moment (the tiles right under the
   Services and Coverage titles, the Contact photo on phones...), with the build's delays. main.js skips [data-intro].
   Failsafe: if main.js has not finished within 3.5s, show everything. */
(function () {
  var d = document.documentElement;
  d.classList.add("js");
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  if (!reduce) d.classList.add("motion");
  // build.py INTRO_DELAY (main.js defaults); the CSS plays half of it, like the build's --in-d
  var DELAY = { lines: .15, fade: .15, frame: .15, stagger: .15, status: .54 };
  function markFold() {
    // too late once main.js has set its reveals up (html.ready); nothing to do without motion
    if (!d.classList.contains("motion") || d.classList.contains("ready")) return;
    var vh = window.innerHeight, list = document.querySelectorAll("[data-reveal]:not([data-intro])"), hit = [], i, el, r;
    for (i = 0; i < list.length; i++) {  // reads first (one layout), then writes
      el = list[i];
      if (!DELAY.hasOwnProperty(el.getAttribute("data-reveal"))) continue;
      r = el.getBoundingClientRect();
      if (r.width > 0 && r.top < vh && r.bottom > 0) hit.push(el);
    }
    for (i = 0; i < hit.length; i++) {
      el = hit[i];
      var dl = parseFloat(el.getAttribute("data-delay")), st = parseFloat(el.getAttribute("data-stagger"));
      el.style.setProperty("--in-d", (isNaN(dl) ? DELAY[el.getAttribute("data-reveal")] : dl) / 2 + "s");
      if (!isNaN(st)) el.style.setProperty("--in-st", st + "s");
      el.setAttribute("data-intro", "");
    }
  }
  var shown = false;
  function fontsIn() {
    if (shown) return;
    shown = true;
    try {
      markFold();
      // the body is not fully parsed yet: mark the rest once it is (before main.js, a module, can run)
      if (document.readyState === "loading") {
        document.addEventListener("readystatechange", function once() {
          document.removeEventListener("readystatechange", once);
          markFold();
        });
      }
    } catch (e) {}
    d.classList.add("fonts-in");
  }
  try {
    var f = document.fonts;
    if (f && f.load) {
      Promise.all([f.load('700 1em "Inter"'), f.load('500 1em "Instrument Sans"')]).then(fontsIn, fontsIn);
    } else {
      fontsIn();
    }
  } catch (e) { fontsIn(); }
  window.setTimeout(fontsIn, 700);
  window.setTimeout(function () {
    if (!d.classList.contains("ready")) d.classList.remove("motion");
  }, 3500);
})();
