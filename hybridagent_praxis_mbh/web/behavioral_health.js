/* Praxis Behavioral Health pack dashboard — the compliance surfaces.
 * Polls /api/behavioral_health every 20s; renders only when the
 * behavioral_health pack is active. Surfaces: psychotherapy-note gate,
 * duty-to-warn gate, mandated-reporter tracker, Part 2 SUD-record gate,
 * minor-consent-MH gate, treatment-plan attestation ledger.
 * Served from /web/behavioral_health.js.
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  async function api(url) {
    var r = await fetch(url);
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  }

  var mount = null, section = null, data = null;

  function renderSurface(title, bodyHtml) {
    var s = el("div", "bh-surface");
    s.appendChild(el("p", "bh-surface-title", title));
    s.appendChild(el("div", "bh-surface-body", null)).innerHTML = bodyHtml;
    return s;
  }
  function pill(kind, label) {
    return '<span class="bh-pill bh-pill-' + kind + '">' + esc(label) + "</span>";
  }

  function renderPsychotherapyGate(g) {
    if (!g) return renderSurface("Psychotherapy-note gate", '<p class="bh-empty">no drafts</p>');
    var rows = (g.drafts || []).map(function (d) {
      var p = d.blocked ? pill("blocked", "blocked") : pill("held", "attest");
      return '<li class="bh-row">' + esc(d.id) + " " + p + " " + esc(d.note_type) + "</li>";
    }).join("");
    var banner = '<div class="bh-gate-banner">Praxis drafts progress notes only — never psychotherapy notes (45 CFR §164.508).</div>';
    return renderSurface("Psychotherapy-note gate", banner + '<ul class="bh-list">' + rows + "</ul>");
  }

  function renderDutyToWarn(g) {
    if (!g) return renderSurface("Duty to warn / protect", '<p class="bh-empty">no active assessments</p>');
    var p = g.duty_triggered ? pill("held", "clinician action") : pill("ok", "clear");
    var body = '<div class="bh-stat-line"><span class="bh-stat">standard:</span> ' + esc(g.standard || "—") + "</div>"
      + '<div class="bh-stat-line"><span class="bh-stat">status:</span> ' + p + "</div>"
      + '<p class="bh-muted">' + esc(g.citation || "") + "</p>";
    return renderSurface("Duty to warn / protect", body);
  }

  function renderMandatedReporter(g) {
    if (!g) return renderSurface("Mandated-reporter tracker", '<p class="bh-empty">no open reports</p>');
    var rows = (g.reports || []).map(function (r) {
      var p = r.status === "filed" ? pill("filed", "filed") : pill("held", "sign-off");
      return '<li class="bh-row">' + esc(r.id) + " " + p + " " + esc(r.reason) + " · SCR " + esc(r.scr_window_h + "h") + "</li>";
    }).join("");
    return renderSurface("Mandated-reporter tracker", '<ul class="bh-list">' + rows + "</ul>");
  }

  function renderPart2(g) {
    if (!g) return renderSurface("42 CFR Part 2 (SUD records)", '<p class="bh-empty">no disclosure requests</p>');
    var body = '<div class="bh-gate-banner">General HIPAA TPO consent does NOT authorize Part 2 disclosures.</div>';
    var rows = (g.requests || []).map(function (r) {
      var p = r.blocked ? pill("blocked", "blocked") : pill("ok", "permitted");
      return '<li class="bh-row">' + esc(r.id) + " " + p + " → " + esc(r.recipient) + "</li>";
    }).join("");
    return renderSurface("42 CFR Part 2 (SUD records)", body + '<ul class="bh-list">' + rows + "</ul>");
  }

  function renderMinorConsent(g) {
    if (!g) return renderSurface("Minor consent for MH", '<p class="bh-empty">no access requests</p>');
    var rows = (g.requests || []).map(function (r) {
      var p = r.blocked ? pill("blocked", "denied") : pill("ok", "allowed");
      return '<li class="bh-row">' + esc(r.id) + " " + p + " " + esc(r.requester_role) + "</li>";
    }).join("");
    return renderSurface("Minor consent for MH", '<ul class="bh-list">' + rows + "</ul>");
  }

  function renderTreatmentPlan(g) {
    if (!g) return renderSurface("Treatment-plan attestation", '<p class="bh-empty">no plan drafts</p>');
    var rows = (g.drafts || []).map(function (d) {
      var p = d.attested ? pill("filed", "attested") : pill("held", "attest");
      return '<li class="bh-row">' + esc(d.id) + " " + p + " " + esc(d.plan_type) + "</li>";
    }).join("");
    return renderSurface("Treatment-plan attestation", '<ul class="bh-list">' + rows + "</ul>");
  }

  function render() {
    if (!mount) return;
    mount.innerHTML = "";
    if (!data || !data.active) {
      mount.appendChild(el("p", "bh-empty", "behavioral_health pack not active"));
      return;
    }
    mount.appendChild(renderPsychotherapyGate(data.psychotherapy));
    mount.appendChild(renderDutyToWarn(data.duty_to_warn));
    mount.appendChild(renderMandatedReporter(data.mandated_reporter));
    mount.appendChild(renderPart2(data.part2));
    mount.appendChild(renderMinorConsent(data.minor_consent));
    mount.appendChild(renderTreatmentPlan(data.treatment_plan));
  }

  async function tick() {
    try { data = await api("/api/behavioral_health"); render(); }
    catch (e) { /* pack not active or daemon down — leave prior render */ }
  }

  function init() {
    section = document.getElementById("behavioral-health-section");
    if (!section) return;
    mount = document.getElementById("behavioral-health-mount");
    if (!mount) { mount = el("div", ""); mount.id = "behavioral-health-mount"; section.appendChild(mount); }
    tick();
    setInterval(tick, 20000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();