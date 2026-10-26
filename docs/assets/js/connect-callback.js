/* /connect/microsoft/callback/ (src/pages/connect/microsoft/callback.html): Microsoft admin consent lands here
   with query params only.
     success: ?admin_consent=True&tenant=<tenant GUID>&state=...
     failure: ?error=<code>&error_description=<text>&state=...   (admin_consent missing or not True)
   Shows one of the page's three blocks (none | ok | error). Every value from the URL is validated and written with
   textContent only: no HTML parsing, no request, no storage, no logging. state is never shown. In a frame the URL is
   ignored (generic block). Then the query string is dropped from the address bar. The page's referrer policy is
   no-referrer and phone/email auto-linking is off (front matter), so text from the URL never becomes a link. */
(function () {
  "use strict";

  var GUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  var CODE = /^[A-Za-z0-9_.-]{1,64}$/;
  var DESC_MAX = 200;   // characters (code points) shown
  var DESC_LINES = 6;   // Microsoft's descriptions run 1 to 5 lines (message, Trace ID, Correlation ID, Timestamp)
  var RAW_MAX = 4096;   // read at most this much of the param before cleaning it
  // control characters, lone surrogates, invisible or bidi formatting marks, fillers, variation selectors and
  // tag characters (they can hide, reorder or smuggle text)
  var STRIP = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F\u00AD\u034F\u061C\u115F\u1160\u17B4\u17B5\u180B-\u180F\u200B-\u200F\u2028\u2029\u202A-\u202E\u2060-\u206F\u3164\uD800-\uDFFF\uFE00-\uFE0F\uFEFF\uFFA0\uFFF9-\uFFFB\u{E0000}-\u{E007F}\u{E0100}-\u{E01EF}]/gu;
  // stacked combining marks ("zalgo") paint far above and below the line, over the rest of the card: keep 2 per letter
  var MARKS = /(\p{M}{2})\p{M}+/gu;
  var TITLES = {
    ok: "Microsoft connected | YellowForce",
    error: "Microsoft connection not completed | YellowForce"
  };

  var card = document.querySelector("[data-cb]");
  if (!card) return;

  function cleanText(s) {
    s = String(s).slice(0, RAW_MAX).replace(/\r\n?/g, "\n").replace(STRIP, "").replace(MARKS, "$1")
      .replace(/[ \t]+/g, " ").replace(/ ?\n ?/g, "\n").replace(/\n{2,}/g, "\n").trim();
    var cut = false;
    var lines = s.split("\n");
    if (lines.length > DESC_LINES) { s = lines.slice(0, DESC_LINES).join("\n"); cut = true; }
    var chars = Array.from(s); // code points, so a cut never splits a surrogate pair
    if (chars.length > DESC_MAX) { s = chars.slice(0, DESC_MAX).join(""); cut = true; }
    return cut ? s.replace(/\s+$/, "") + "\u2026" : s;
  }

  function setText(sel, text) {
    var el = card.querySelector(sel);
    if (el) el.textContent = text;
  }

  function showRow(name, on) {
    var row = card.querySelector('[data-cb-row="' + name + '"]');
    if (row) row.hidden = !on;
  }

  function render(q) {
    var attempt = q.has("admin_consent") || q.has("tenant") || q.has("error") || q.has("error_description");
    if (!attempt) return "none";

    var err = q.get("error");
    var consent = (q.get("admin_consent") || "").trim().toLowerCase() === "true";
    var tenant = (q.get("tenant") || "").trim();
    if (err === null && consent && GUID.test(tenant)) { // any error param, even empty, is not a success
      setText("[data-cb-tenant]", tenant.toLowerCase());
      return "ok";
    }

    var code = err !== null && CODE.test(err) ? err : "";
    var desc = q.has("error_description") ? cleanText(q.get("error_description")) : "";
    // only show text shaped like a real Microsoft identity error ("AADSTS65004: ..."); anything else could be
    // an attacker's message under our domain (vishing), so it is dropped
    if (desc && !/^AADSTS\d{4,6}:/.test(desc)) desc = "";
    if (!code && !desc) {
      // nothing from Microsoft we can show: say what was wrong with the link instead (fixed strings)
      if (err !== null) desc = "Microsoft sent back an error code this page can\u2019t display.";
      else if (consent) desc = "The link back from Microsoft has no valid tenant ID.";
      else if (q.has("admin_consent")) desc = "Admin consent was not granted.";
      else desc = "The link back from Microsoft is incomplete.";
    }
    setText("[data-cb-code]", code);
    setText("[data-cb-desc]", desc);
    showRow("code", !!code);
    showRow("desc", !!desc);
    return "error";
  }

  // Microsoft always lands here as the top-level page. In a frame (another site showing this page with its own
  // params, GitHub Pages cannot send frame-ancestors) nothing from the URL is shown: generic block only.
  var framed = true;
  try { framed = window.self !== window.top; } catch (e) {}

  var state = "none";
  try {
    if (!framed) state = render(new URLSearchParams(window.location.search));
  } catch (e) {
    state = "none";
  }

  var blocks = card.querySelectorAll("[data-cb-state]");
  for (var i = 0; i < blocks.length; i++) blocks[i].hidden = blocks[i].getAttribute("data-cb-state") !== state;
  var badges = card.querySelectorAll("[data-cb-show]");
  for (var j = 0; j < badges.length; j++) badges[j].hidden = badges[j].getAttribute("data-cb-show") !== state;
  if (TITLES[state]) document.title = TITLES[state];
  card.setAttribute("data-cb-ready", "");

  // rendered: drop the query string from the address bar (screenshots, bookmarks, shared links)
  // (a full same-origin URL, so an odd path such as //x/ can never resolve to another host)
  if (window.location.search && window.history && typeof window.history.replaceState === "function") {
    try {
      var clean = new URL(window.location.href);
      clean.search = "";
      window.history.replaceState(window.history.state, "", clean.href);
    } catch (e) {}
  }
})();
