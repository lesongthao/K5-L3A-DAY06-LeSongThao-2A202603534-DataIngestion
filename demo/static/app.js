"use strict";
const $ = (id) => document.getElementById(id);
const state = { data: null, split: "all", strategy: "all", metricSplit: "dev", liveResult: null, live: false };
const labels = { a: ["Cửa sổ cố định", "500 ký tự · overlap 50"], b: ["Theo đoạn văn", "Tối đa 800 ký tự · không lọc"], c: ["Đoạn văn + metadata", "Cùng chunk B · lọc section"] };
const sections = { quy_che_dao_tao: "Quy chế đào tạo", hoc_bong_hoc_phi: "Học phí & học bổng", cong_tac_sinh_vien: "Công tác sinh viên", tot_nghiep_khen_thuong: "Tốt nghiệp & khen thưởng" };
function el(tag, cls, text) { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; }
function notice(message) { $("notice").textContent = message; $("notice").hidden = !message; }
function sourceLink(page, text = "Mở trang ↗") {
  const a = el("a", "text-link", text); const p = Number(page);
  a.href = "/api/document#page=" + (Number.isInteger(p) && p > 0 && p <= 35 ? p : 3);
  a.target = "_blank"; a.rel = "noopener noreferrer"; return a;
}
function showView(view) {
  document.querySelectorAll(".view").forEach((node) => { node.hidden = node.id !== "view-" + view; });
  document.querySelectorAll("[data-view]").forEach((button) => {
    const selected = button.dataset.view === view; button.classList.toggle("active", selected);
    if (selected) button.setAttribute("aria-current", "page"); else button.removeAttribute("aria-current");
  });
  notice("");
}
function setSelected(selector, key, value) { document.querySelectorAll(selector).forEach((b) => b.classList.toggle("selected", b.dataset[key] === value)); }
function highlight(text, quotes) {
  const node = el("p", "chunk-text");
  const clean = String(text || "").normalize("NFC").replace(/\s+/g, " ");
  const lower = clean.toLocaleLowerCase("vi"); const ranges = [];
  for (const quote of quotes || []) {
    if (!quote) continue;
    const q = quote.normalize("NFC").replace(/\s+/g, " ").toLocaleLowerCase("vi");
    const index = lower.indexOf(q); if (index >= 0 && q.length) ranges.push([index, index + q.length]);
  }
  ranges.sort((a, b) => a[0] - b[0]);
  let offset = 0;
  for (const [start, end] of ranges) {
    if (start < offset) continue;
    node.append(document.createTextNode(clean.slice(offset, start)), el("mark", "", clean.slice(start, end)));
    offset = end;
  }
  node.append(document.createTextNode(clean.slice(offset))); return node;
}
function currentQuestion() { return state.data.questions.find((q) => q.id === $("questionSelect").value); }
function populateQuestions() {
  const prev = $("questionSelect").value || "q08"; const search = $("questionFilter").value.toLocaleLowerCase("vi").trim();
  const questions = state.data.questions.filter((q) => (state.split === "all" || q.split === state.split) && (q.id + " " + q.question).toLocaleLowerCase("vi").includes(search));
  $("questionSelect").replaceChildren();
  questions.forEach((q) => { const o = el("option", "", q.id.toUpperCase() + " · " + q.question); o.value = q.id; $("questionSelect").append(o); });
  if (questions.some((q) => q.id === prev)) $("questionSelect").value = prev;
  $("questionSelect").disabled = !questions.length;
  $("questionCounter").textContent = questions.length + " câu phù hợp";
  renderRecorded();
}
function renderRecorded() {
  if (state.live) return;
  const q = currentQuestion(); $("goldPanel").hidden = !q; $("questionMeta").replaceChildren();
  if (!q) { $("results").replaceChildren(el("p", "empty", "Không có câu hỏi phù hợp. Thử từ khóa hoặc tập khác.")); return; }
  $("questionMeta").append(el("span", "mini-tag", q.id.toUpperCase()), el("span", "mini-tag", q.split.toUpperCase()), el("span", "mini-tag", "Gold · trang " + q.gold_page));
  if (q.filter) $("questionMeta").append(el("span", "mini-tag", "Filter C: " + (sections[q.filter.section] || q.filter.section)));
  else $("questionMeta").append(el("span", "mini-tag", "Không có filter"));
  $("goldQuote").textContent = (q.evidence_quotes?.length ? q.evidence_quotes : [q.evidence_quote]).join("\n\n");
  $("goldAnswer").textContent = q.expected_answer; $("goldSource").href = "/api/document#page=" + q.gold_page;
  $("goldSource").textContent = "PDF · Trang " + q.gold_page + " ↗";
  renderResults(Object.fromEntries("abc".split("").map((s) => [s, state.data.traces[s].find((t) => t.id === q.id).hits])), q);
}
function renderResults(hitsByStrategy, q = null) {
  $("results").replaceChildren(); $("results").classList.toggle("single", state.strategy !== "all");
  $("resultsTitle").textContent = q ? "Top-3 · " + q.id.toUpperCase() + " / " + q.split : "Top-3 · Truy vấn trực tiếp";
  for (const s of "abc") {
    if (state.strategy !== "all" && state.strategy !== s) continue;
    const hits = hitsByStrategy[s] || []; const card = el("article", "strategy-card strategy-" + s);
    const head = el("div", "strategy-head"); head.append(el("span", "strategy-letter", s.toUpperCase()));
    const title = el("div"); title.append(el("strong", "", labels[s][0]), el("small", "", labels[s][1])); head.append(title);
    const hit = hits.some((h) => h.is_evidence_hit);
    head.append(el("span", "result-badge" + (q && !hit ? " miss" : ""), q ? (hit ? "HIT@3 ✓" : "MISS@3") : "LIVE")); card.append(head);
    hits.forEach((h, index) => {
      const item = el("section", "hit"); const top = el(index ? "summary" : "div", "hit-top");
      top.append(el("span", "rank", String(index + 1)), el("span", "hit-page", "Trang " + h.page), el("span", "similarity", "cosine " + Number(h.score).toFixed(3)));
      const container = index ? el("details") : item;
      container.append(top);
      const quotes = q ? (q.evidence_quotes?.length ? q.evidence_quotes : [q.evidence_quote]) : [];
      container.append(highlight(h.text, quotes));
      const bottom = el("div", "hit-bottom"); bottom.append(el("span", "mini-tag", sections[h.section] || h.section || "Chưa có section"), sourceLink(h.page));
      container.append(bottom, el("div", "hit-id", h.chunk_id));
      if (index) item.append(container); card.append(item);
    });
    if (!hits.length) card.append(el("p", "empty", "Không có kết quả trong phạm vi này."));
    $("results").append(card);
  }
}
function setMode(live) {
  state.live = live; $("recordedControls").hidden = live; $("liveForm").hidden = !live; $("goldPanel").hidden = live;
  for (const [id, chosen] of [["liveTab", live], ["recordedTab", !live]]) { $(id).classList.toggle("selected", chosen); $(id).setAttribute("aria-selected", String(chosen)); }
  $("modeBadge").textContent = live ? "TRUY VẤN MỚI" : "TRACE ĐÃ LƯU"; notice("");
  if (!live) renderRecorded();
  else if (state.liveResult) renderResults(state.liveResult.hits);
  else { $("results").replaceChildren(el("p", "empty", state.data.live_enabled ? "Nhập câu hỏi và phạm vi, sau đó chọn Tra cứu top-3." : "Chạy python -m demo --live để bật truy vấn mới qua Gemini.")); $("resultsTitle").textContent = "Kết quả truy vấn mới"; }
}
function renderMetrics() {
  $("benchmarkBars").replaceChildren(); $("metricsBody").replaceChildren();
  for (const s of "abc") {
    const summary = state.data.summary["strategy_" + s], m = summary.metrics[state.metricSplit];
    const bar = el("div", "bar-row"), label = el("div", "bar-label");
    label.append(el("span", "", s.toUpperCase() + " · " + labels[s][0]), el("small", "", m.hit_at_3 + " · " + Math.round(m.hit_at_3_rate * 100) + "%"));
    const progress = el("progress"); progress.max = 1; progress.value = m.hit_at_3_rate; progress.setAttribute("aria-label", s.toUpperCase() + " Evidence Hit@3"); bar.append(label, progress); $("benchmarkBars").append(bar);
    const row = el("tr"); const seconds = state.data.summary.timing_breakdown["strategy_" + s].embed_time;
    [s.toUpperCase() + " · " + labels[s][0], m.hit_at_1, m.hit_at_3, m.filter_compliance, summary.chunk_count, s === "c" ? "Dùng lại B" : seconds + "s"].forEach((v) => row.append(el("td", "", String(v)))); $("metricsBody").append(row);
  }
}
function renderAudit() {
  const audit = state.data.audit; $("auditMethod").textContent = audit.methodology;
  for (const s of "abc") {
    const article = el("article"); const coh = audit.coherence[s === "a" ? "strategy_a_avg" : "strategy_b_avg"];
    article.append(el("small", "", s.toUpperCase() + " · COHERENCE / 2"), el("strong", "", Number(coh).toFixed(2)), el("small", "", "Metadata: " + audit.metadata_usefulness["strategy_" + s].accuracy_ratio + " · Grounding: " + audit.grounding_quality.averages["strategy_" + s].toFixed(2) + "/2")); $("auditSummary").append(article);
  }
  for (const sample of state.data.audit_samples) {
    const details = el("details", "audit-sample"), summary = el("summary");
    summary.append(el("span", "", "Trang " + sample.page + " · " + (sections[sample.section] || sample.section)), el("span", "", "A " + sample.strategy_a.score + "/2 · B/C " + sample.strategy_b.score + "/2")); details.append(summary);
    const columns = el("div", "audit-columns");
    for (const s of ["a", "b"]) { const d = sample["strategy_" + s], col = el("div"); col.append(el("h4", "", "Chiến lược " + s.toUpperCase() + " · " + d.score + "/2"), highlight(d.text, []), el("p", "", d.reason), sourceLink(sample.page)); columns.append(col); }
    details.append(columns); $("coherenceSamples").append(details);
  }
  for (const sample of audit.grounding_quality.eval_list) {
    const details = el("details", "audit-sample"), summary = el("summary"); summary.append(el("span", "", sample.query_id.toUpperCase() + " · " + sample.question), el("span", "", "A " + sample.strategy_a.score + "/2 · B " + sample.strategy_b.score + "/2 · C " + sample.strategy_c.score + "/2")); details.append(summary);
    for (const s of "abc") details.append(el("p", "fine-print", s.toUpperCase() + ": " + sample["strategy_" + s].reason));
    const button = el("button", "text-button", "Mở top-3 của câu này →"); button.addEventListener("click", () => selectCase(sample.query_id)); details.append(button); $("groundingSamples").append(details);
  }
}
function selectCase(id) { state.split = "all"; $("questionFilter").value = ""; setSelected("[data-split]", "split", "all"); setMode(false); populateQuestions(); $("questionSelect").value = id; renderRecorded(); showView("explorer"); }
async function liveSearch(event) {
  event.preventDefault(); if (!state.data.live_enabled) return;
  $("liveSubmit").disabled = true; $("liveSubmit").textContent = "Đang truy xuất…"; notice("");
  try {
    const response = await fetch("/api/search", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: $("liveQuestion").value, section: $("liveSection").value || null }), signal: AbortSignal.timeout(65000) });
    const result = await response.json(); if (!response.ok) throw new Error(result.error || "Truy vấn chưa thực hiện được.");
    state.liveResult = result; renderResults(result.hits); notice("Kết quả truy vấn mới. Chưa có gold để tính Hit@1/Hit@3; phạm vi chỉ được áp dụng cho C.");
  } catch (error) { notice(error.name === "TimeoutError" ? "Hết thời gian chờ. Kiểm tra kết nối ở máy chủ." : error.message); }
  finally { $("liveSubmit").disabled = false; $("liveSubmit").textContent = "Tra cứu top-3 →"; }
}
async function initialize() {
  try {
    const response = await fetch("/api/data"); if (!response.ok) throw new Error("Không tải được dữ liệu. Kiểm tra các file results và khởi động lại demo.");
    state.data = await response.json(); const d = state.data, summary = d.summary;
    $("studentName").textContent = d.student.name; $("pageCount").textContent = d.manifest.total_content_pages;
    $("pageDetail").textContent = d.manifest.total_physical_pages + " trang PDF · bỏ bìa, mục lục, phụ lục";
    $("queryCount").textContent = d.questions.length; $("splitDetail").textContent = d.questions.filter((q) => q.split === "dev").length + " dev / " + d.questions.filter((q) => q.split === "test").length + " test";
    $("chunkCounts").textContent = "abc".split("").map((s) => summary["strategy_" + s].chunk_count).join(" / ");
    $("bestHit").textContent = summary.strategy_c.metrics.test.hit_at_3;
    $("liveSubmit").disabled = !d.live_enabled; $("liveHint").textContent = d.live_enabled ? "Dùng Gemini API và database trên máy chủ; có thể tiêu thụ quota. Phạm vi là input của bạn, chỉ áp dụng cho C." : "Chế độ hiện tại không gọi API. Để tra cứu mới, chạy python -m demo --live với GEMINI_API_KEY ở .env phía máy chủ.";
    populateQuestions(); renderMetrics(); renderAudit(); document.body.classList.add("ready");
    document.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => showView(b.dataset.view)));
    document.querySelectorAll("[data-split]").forEach((b) => b.addEventListener("click", () => { state.split = b.dataset.split; setSelected("[data-split]", "split", state.split); populateQuestions(); }));
    document.querySelectorAll("[data-strategy]").forEach((b) => b.addEventListener("click", () => { state.strategy = b.dataset.strategy; setSelected("[data-strategy]", "strategy", state.strategy); if (state.live && state.liveResult) renderResults(state.liveResult.hits); else if (!state.live) renderRecorded(); }));
    document.querySelectorAll("[data-metric-split]").forEach((b) => b.addEventListener("click", () => { state.metricSplit = b.dataset.metricSplit; setSelected("[data-metric-split]", "metricSplit", state.metricSplit); renderMetrics(); }));
    $("questionFilter").addEventListener("input", populateQuestions); $("questionSelect").addEventListener("change", renderRecorded);
    $("recordedTab").addEventListener("click", () => setMode(false)); $("liveTab").addEventListener("click", () => setMode(true)); $("liveForm").addEventListener("submit", liveSearch);
    $("showFilterCase").addEventListener("click", () => selectCase("q08"));
    $("exportAudit").addEventListener("click", () => { const blob = new Blob([JSON.stringify(d.audit, null, 2)], { type: "application/json" }); const url = URL.createObjectURL(blob); const a = el("a"); a.href = url; a.download = "day06-audit-labels.json"; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); });
  } catch (error) { notice(error.message); $("results").replaceChildren(el("p", "empty", "Chưa có dữ liệu để hiển thị.")); }
}
initialize();
