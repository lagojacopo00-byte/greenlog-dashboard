// Pagine della pipeline lette come slide verticali: ogni sezione occupa una schermata
// e si aggancia allo scorrimento; a destra i puntini dicono a che sezione sei.
// Senza JS la pagina resta un normale documento a scorrimento libero.
(function () {
  var root = document.documentElement;
  var header = document.querySelector(".site-header");
  var stepsNav = document.querySelector(".steps-nav");
  var pager = document.querySelector(".pager");
  var footer = document.querySelector(".site-footer");
  var hero = document.querySelector(".p-hero");
  if (!header || !hero) return;

  root.classList.add("p-slides");

  // la prima slide è header + passaggi + apertura; l'ultima è il passaggio successivo + footer
  function measure() {
    root.style.setProperty("--top-h", header.offsetHeight + (stepsNav ? stepsNav.offsetHeight : 0) + "px");
    root.style.setProperty("--foot-h", (footer ? footer.offsetHeight : 0) + "px");
  }
  measure();
  window.addEventListener("resize", measure);

  var slides = [{ el: header, label: (hero.querySelector("h1") || {}).textContent || "Apertura" }];
  document.querySelectorAll("main .p-section").forEach(function (s) {
    var h = s.querySelector("h2");
    slides.push({ el: s, label: h ? h.textContent.trim() : "Sezione" });
  });
  if (pager) slides.push({ el: pager, label: "Passaggio successivo" });

  var nav = document.createElement("nav");
  nav.className = "slide-dots";
  nav.setAttribute("aria-label", "Sezioni della pagina");
  var ol = document.createElement("ol");
  var links = slides.map(function (s, i) {
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = s.el.id ? "#" + s.el.id : "#";
    a.innerHTML = '<span class="lbl"></span><i aria-hidden="true"></i>';
    a.querySelector(".lbl").textContent = s.label;
    a.addEventListener("click", function (e) {
      e.preventDefault();
      go(i);
    });
    li.appendChild(a);
    ol.appendChild(li);
    return a;
  });
  nav.appendChild(ol);
  document.body.appendChild(nav);

  function topOf(i) {
    if (i === 0) return 0;
    if (slides[i].el === pager) return document.documentElement.scrollHeight - window.innerHeight;
    return slides[i].el.getBoundingClientRect().top + window.scrollY;
  }

  function go(i) {
    window.scrollTo({ top: topOf(i), behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }

  var current = -1;
  function update() {
    var y = window.scrollY + window.innerHeight * 0.4;
    var idx = 0;
    for (var i = 0; i < slides.length; i++) if (topOf(i) <= y) idx = i;
    // in fondo alla pagina l'ultima slide è attiva anche se è più bassa di una schermata
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) idx = slides.length - 1;
    if (idx === current) return;
    current = idx;
    links.forEach(function (a, k) {
      if (k === idx) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
    });
  }

  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; update(); });
  }, { passive: true });
  window.addEventListener("resize", update);
  update();
})();
