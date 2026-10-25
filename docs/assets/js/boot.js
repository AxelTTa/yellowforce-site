/* Runs in <head> before paint: marks JS and motion support so CSS can hide reveal targets.
   Failsafe: if main.js has not finished within 3.5s, show everything. */
(function () {
  var d = document.documentElement;
  d.classList.add("js");
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  if (!reduce) d.classList.add("motion");
  window.setTimeout(function () {
    if (!d.classList.contains("ready")) d.classList.remove("motion");
  }, 3500);
})();
