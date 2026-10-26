/* Runs in <head> before paint (after the stylesheets): marks JS and motion support so CSS can hide reveal targets.
   html.fonts-in: the two web fonts are loaded (or 700 ms passed). The first screen's reveals ([data-intro], marked by
   the build) are CSS animations that start on it, so they never wait for the JS bundle.
   Failsafe: if main.js has not finished within 3.5s, show everything. */
(function () {
  var d = document.documentElement;
  d.classList.add("js");
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  if (!reduce) d.classList.add("motion");
  var shown = false;
  function fontsIn() {
    if (shown) return;
    shown = true;
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
