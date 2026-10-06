// Damico Health site behavior: mobile menu, programs dropdown, chart reveal, email signup.
(function () {
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    var item = btn.closest(".has-sub");
    btn.addEventListener("click", function () {
      var open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && item.classList.contains("is-open")) {
        item.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
        btn.focus();
      }
    });
  });

  // Marks are drawn at full size by default; each chart grows in once when it scrolls into view.
  var charts = document.querySelectorAll(".chart, .viz");
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (charts.length && !calm && "IntersectionObserver" in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-animated");
          seen.unobserve(entry.target);
        }
      });
    }, { threshold: 0.35 });
    charts.forEach(function (c) { seen.observe(c); });
  }

  // Smooth mouse-wheel scrolling on computers. Phones and tablets keep their native scrolling,
  // and so does anyone who has asked their system for reduced motion.
  var desktopPointer = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (window.Lenis && desktopPointer && !calm) {
    // Section links land below the sticky bars via scroll-padding-top in the stylesheet.
    new window.Lenis({ autoRaf: true, lerp: 0.14, anchors: true });
  }

  // Our work: mark the section being read in the on-page menu.
  var pageNav = document.querySelector(".work-nav");
  if (pageNav && "IntersectionObserver" in window) {
    var links = {};
    pageNav.querySelectorAll("a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        Object.keys(links).forEach(function (id) { links[id].classList.toggle("is-current", id === entry.target.id); });
        var cur = links[entry.target.id];
        if (cur && cur.scrollIntoView) {
          var list = cur.closest("ul");
          list.scrollLeft = cur.offsetLeft - list.clientWidth / 2 + cur.clientWidth / 2;
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(links).forEach(function (id) { var el = document.getElementById(id); if (el) spy.observe(el); });
  }

  // Copy-to-clipboard buttons (contact page).
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    var status = btn.parentNode.querySelector(".copy-status");
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      function done(ok) { if (status) status.textContent = ok ? "Copied" : "Select the address above to copy it"; }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
      } else { done(false); }
    });
  });

  // Email signup. Set data-endpoint on the form to the mailing-list provider's form address.
  document.querySelectorAll("form.signup").forEach(function (form) {
    var status = form.querySelector(".signup-status");
    var input = form.querySelector("input[type=email]");
    function say(text) { status.textContent = text; status.hidden = false; }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!input.value || !input.checkValidity()) { say("Enter a valid email address."); input.focus(); return; }
      var endpoint = form.getAttribute("data-endpoint");
      if (!endpoint) { say("Signup is not connected yet. For now, email md@damicohealth.org to join the list."); return; }
      say("Signing you up.");
      fetch(endpoint, { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(form) })
        .then(function (r) {
          if (!r.ok) throw new Error("failed");
          form.reset();
          say("You are signed up. Thank you.");
        })
        .catch(function () { say("Signup did not go through. Try again, or email md@damicohealth.org."); });
    });
  });
})();
