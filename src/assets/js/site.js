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

  // Bars are full width by default; they grow in once when the chart scrolls into view.
  var chart = document.querySelector(".chart");
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (chart && !calm && "IntersectionObserver" in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          chart.classList.add("is-animated");
          seen.disconnect();
        }
      });
    }, { threshold: 0.35 });
    seen.observe(chart);
  }

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
