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

// Colorazione minima dei blocchi <pre class="code" data-lang="py|sql">: parole chiave, stringhe, commenti, numeri.
// Il codice nell'HTML resta testo semplice; se lo script non gira si legge comunque.
(function () {
  var KW = {
    py: "def return import from as for in if else elif while with class None True False and or not lambda try except",
    sql: "SELECT FROM WHERE GROUP BY ORDER JOIN LEFT ON AS WITH CREATE OR REPLACE VIEW SUM AVG COUNT ROUND COALESCE NULLIF GREATEST CASE WHEN THEN ELSE END INSERT INTO VALUES AND"
  };
  var esc = function (s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); };

  document.querySelectorAll("pre.code[data-lang]").forEach(function (pre) {
    var lang = pre.getAttribute("data-lang");
    var words = KW[lang] || "";
    var comment = lang === "sql" ? "--[^\\n]*" : "#[^\\n]*";
    var re = new RegExp("(" + comment + ")|(\"\"\"[\\s\\S]*?\"\"\"|\"[^\"\\n]*\"|'[^'\\n]*')|\\b(" + words.split(" ").join("|") + ")\\b|\\b(\\d+(?:\\.\\d+)?)\\b", lang === "sql" ? "gi" : "g");
    var src = pre.textContent, out = "", last = 0, m;
    while ((m = re.exec(src))) {
      out += esc(src.slice(last, m.index));
      var cls = m[1] ? "c" : m[2] ? "s" : m[3] ? "k" : "n";
      out += '<span class="' + cls + '">' + esc(m[0]) + "</span>";
      last = re.lastIndex;
    }
    pre.innerHTML = out + esc(src.slice(last));
  });
})();
