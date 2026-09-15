// Ingresso dei blocchi quando entrano nella finestra, una volta sola.
(function () {
  var root = document.documentElement;
  if (!("IntersectionObserver" in window)) return;
  root.classList.add("js");

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add("is-in");
      io.unobserve(e.target);
    });
  }, { rootMargin: "0px 0px -40px 0px", threshold: 0.01 });

  document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
})();
