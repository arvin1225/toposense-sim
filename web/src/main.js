import "./styles.css";

const familyMeta = {
  blur_crosstalk: { index: "01", label: "Blur × crosstalk", detail: "OTF / Mueller residual" },
  low_photon_bias: { index: "02", label: "Photon × bias", detail: "Poisson / carrier leakage" },
  high_mode_na: { index: "03", label: "High mode × NA", detail: "support truncation" },
  sector_dropout: { index: "04", label: "Sector dropout", detail: "unobserved angular arc" },
  compound_shift: { index: "05", label: "Compound shift", detail: "all receiver factors" },
};
const preferredMethods = ["polygon_unconditional", "margin_only", "global_certificate", "local_certificate", "uniform_support_certificate", "adaptive_support_certificate"];
const methodColors = { polygon_unconditional: "#8da5b1", margin_only: "#e8a53b", global_certificate: "#6287e8", local_certificate: "#8c74e8", uniform_support_certificate: "#48b8ce", adaptive_support_certificate: "#53e0b2" };
const state = { data: null, scenario: 0, method: "adaptive_support_certificate", yaw: -0.7, pitch: 0.28, zoom: 1, dragging: false, last: [0, 0] };
const $ = (query) => document.querySelector(query); const $$ = (query) => [...document.querySelectorAll(query)];
const current = () => state.data.representatives[state.scenario];
const signed = (value) => value > 0 ? `+${value}` : String(value);

function renderScenarioList() {
  $("#scenario-list").innerHTML = state.data.representatives.map((item, index) => { const meta = familyMeta[item.family]; return `<button class="scenario ${index === state.scenario ? "active" : ""}" data-index="${index}"><span>${meta.index}</span><div><b>${meta.label}</b><small>${meta.detail}</small></div><i>${item.seed}</i></button>`; }).join("");
  $$(".scenario").forEach((button) => button.addEventListener("click", () => { state.scenario = Number(button.dataset.index); renderAll(); }));
}

function renderMethodList() {
  $("#method-list").innerHTML = preferredMethods.map((method) => `<button class="method ${method === state.method ? "active" : ""}" data-method="${method}"><i style="--color:${methodColors[method]}"></i><span>${state.data.methodLabels[method]}</span><b>${method === "adaptive_support_certificate" ? "ADAPTIVE" : ""}</b></button>`).join("");
  $$(".method").forEach((button) => button.addEventListener("click", () => { state.method = button.dataset.method; renderMethodList(); renderDecision(); }));
}

function rotate([x, y, z]) {
  const cy = Math.cos(state.yaw), sy = Math.sin(state.yaw), cp = Math.cos(state.pitch), sp = Math.sin(state.pitch);
  const x1 = cy * x + sy * z; const z1 = -sy * x + cy * z;
  return [x1, cp * y - sp * z1, sp * y + cp * z1];
}

function renderSphere() {
  const canvas = $("#sphere-canvas"), ctx = canvas.getContext("2d"); const w = canvas.width, h = canvas.height; const cx = w * .52, cy = h * .5, radius = Math.min(w, h) * .39 * state.zoom;
  ctx.clearRect(0, 0, w, h);
  const gradient = ctx.createRadialGradient(cx - radius * .34, cy - radius * .42, radius * .05, cx, cy, radius); gradient.addColorStop(0, "rgba(119,175,205,.22)"); gradient.addColorStop(.65, "rgba(43,91,112,.09)"); gradient.addColorStop(1, "rgba(7,19,31,.2)");
  ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = "rgba(134,190,203,.30)"; ctx.lineWidth = 1.2; ctx.stroke();
  const project = (point) => { const [x, y, z] = rotate(point); return [cx + x * radius, cy - y * radius, z]; };
  const gridCircle = (axis, offset = 0) => { const points=[]; for(let i=0;i<=90;i++){const a=i/90*Math.PI*2; const p=axis===0?[offset,Math.cos(a)*Math.sqrt(1-offset*offset),Math.sin(a)*Math.sqrt(1-offset*offset)]:axis===1?[Math.cos(a)*Math.sqrt(1-offset*offset),offset,Math.sin(a)*Math.sqrt(1-offset*offset)]:[Math.cos(a)*Math.sqrt(1-offset*offset),Math.sin(a)*Math.sqrt(1-offset*offset),offset]; points.push(project(p));} ctx.beginPath(); points.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1])); ctx.stroke(); };
  ctx.strokeStyle="rgba(129,181,194,.10)"; ctx.lineWidth=.8; [0,1,2].forEach(axis=>[-.5,0,.5].forEach(offset=>gridCircle(axis,offset)));
  const sample = current(); const na = Number($("#na-control").value); const bias = Number($("#bias-control").value); const budget = Number($("#budget-control").value);
  const transformed = sample.received.map(([x,y,z]) => { const scale = Math.max(.25, na); const v=[x*scale+bias,y*scale-.3*bias,z]; const n=Math.hypot(...v)||1; return v.map(q=>q/n); });
  const drawLoop = (points, color, width, alpha=1) => { const projected=points.map(project); ctx.strokeStyle=color; ctx.globalAlpha=alpha; ctx.lineWidth=width; ctx.lineJoin="round"; ctx.beginPath(); projected.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1])); if(projected.length)ctx.lineTo(projected[0][0],projected[0][1]); ctx.stroke(); ctx.globalAlpha=1; };
  if($("#show-ideal").checked) drawLoop(sample.ideal,"#7d9cff",3,0.9);
  if($("#show-received").checked) drawLoop(transformed,"#efad55",3,0.92);
  if($("#show-samples").checked){ const points=sample.adaptive.stokes.slice(0,budget); points.map((p,i)=>({p:project(p),i})).sort((a,b)=>a.p[2]-b.p[2]).forEach(({p,i})=>{ctx.beginPath();ctx.arc(p[0],p[1],i<12?5:4,0,Math.PI*2);ctx.fillStyle=i<12?"#a9bdc8":"#58e0b3";ctx.globalAlpha=p[2]<0?.45:1;ctx.fill();ctx.globalAlpha=1;}); }
  ctx.fillStyle="rgba(175,214,218,.75)";ctx.font="500 12px 'IBM Plex Mono'";ctx.fillText("S² / normalized Stokes",cx-radius+14,cy+radius-17);
}

function renderAngleTrack() {
  const item=current(); const budget=Number($("#budget-control").value); const angles=item.adaptive.angles.slice(0,budget);
  $("#angle-track").innerHTML=angles.map((angle,index)=>`<i class="${index<12?"initial":"added"}" style="left:${angle/(Math.PI*2)*100}%"></i>`).join("");
}

function renderDecision() {
  const item=current(); const result=item.methods[state.method]; const badge=$("#decision-badge"); const released=result.released;
  badge.className=`decision-badge ${released?"release":"erasure"}`; badge.innerHTML=`<span>DECISION</span><strong>${released?"RELEASE":"ERASURE"}</strong>`;
  $("#released-symbol").textContent=released?signed(result.releasedWinding):"—";
  $("#observed-winding").textContent=signed(result.observedWinding); $("#true-winding").textContent=signed(item.trueWinding);
  $("#decision-explanation").textContent=released?(result.correct?"The selected policy releases a winding consistent with the dense ideal topology.":"The released integer differs from the ideal field in this recorded trial."):"The receiver returned an erasure because at least one required check failed.";
  const cert=item.certificate; $("#margin-metric").textContent=Number(result.margin).toFixed(3); $("#radius-metric").textContent=cert.minimum_projected_radius.toFixed(3); $("#gap-metric").textContent=cert.maximum_gap_rad.toFixed(2); $("#transfer-metric").textContent=cert.transfer_headroom.toFixed(2);
}

function renderGates() {
  const labels={projected_clearance:"Projected clearance",unambiguous_phase:"Branch uniqueness",integer_closure:"Integer closure",nontrivial_sampling:"Sample support",measurement_model_registered:"Measurement envelope",support_observability:"Optical observability",zero_mode_separation:"Zero-mode separation"};
  $("#gate-list").innerHTML=Object.entries(current().certificate.gates).map(([key,value])=>`<div class="gate ${value?"pass":"fail"}"><i>${value?"✓":"×"}</i><span><b>${labels[key]||key}</b><small>${value?"contract satisfied":"erasure trigger"}</small></span><em>${value?"PASS":"FAIL"}</em></div>`).join("");
}

function renderMetadata() {
  const item=current(); $("#seed-label").textContent=item.seed; $("#na-value").textContent=item.receiver.naCutoff.toFixed(2); $("#cross-value").textContent=item.receiver.crosstalk.toFixed(3); $("#bias-value").textContent=item.receiver.projectedBias.toFixed(3); $("#dropped-value").textContent=item.adaptive.dropped; $("#added-value").textContent=Math.max(0,item.adaptive.angles.length-12);
}

function renderGoodputChart() {
  const overall=state.data.summary.overall; const methods=["margin_only","global_certificate","uniform_support_certificate","adaptive_support_certificate"]; const max=Math.max(...methods.map(m=>overall[m].certified_goodput));
  $("#goodput-chart").innerHTML=methods.map(method=>`<div><span>${state.data.methodLabels[method]}</span><p><i style="width:${overall[method].certified_goodput/max*100}%;--color:${methodColors[method]}"></i></p><b>${overall[method].certified_goodput.toFixed(3)}</b></div>`).join("");
}

function renderFamilyChart() {
  const summary=state.data.summary.by_family; const max=Math.max(...Object.values(summary).map(v=>v.adaptive_support_certificate.certified_goodput));
  $("#family-chart").innerHTML=Object.entries(summary).map(([family,values])=>`<div><span>${familyMeta[family].label}</span><p><i class="global" style="height:${values.global_certificate.certified_goodput/max*100}%"></i><i class="adaptive" style="height:${values.adaptive_support_certificate.certified_goodput/max*100}%"></i></p><small>${values.adaptive_support_certificate.certified_goodput.toFixed(2)}</small></div>`).join("");
}

function renderAll(){renderScenarioList();renderMethodList();renderMetadata();renderDecision();renderGates();renderSphere();renderAngleTrack();}

function bind() {
  ["show-ideal","show-received","show-samples"].forEach(id=>$("#"+id).addEventListener("change",renderSphere));
  const controls=[["na-control","na-out",v=>`${Number(v).toFixed(2)}×`],["bias-control","bias-out",v=>Number(v).toFixed(2)],["budget-control","budget-out",v=>v]];
  controls.forEach(([id,out,format])=>$("#"+id).addEventListener("input",e=>{$("#"+out).textContent=format(e.target.value);renderSphere();renderAngleTrack();}));
  $("#reset-lens").addEventListener("click",()=>{controls.forEach(([id,out,format])=>{const v=id==="na-control"?1:id==="budget-control"?32:0;$("#"+id).value=v;$("#"+out).textContent=format(v);});renderSphere();renderAngleTrack();});
  const canvas=$("#sphere-canvas"); canvas.addEventListener("pointerdown",e=>{state.dragging=true;state.last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);}); canvas.addEventListener("pointermove",e=>{if(!state.dragging)return;state.yaw+=(e.clientX-state.last[0])*.008;state.pitch=Math.max(-1.1,Math.min(1.1,state.pitch+(e.clientY-state.last[1])*.008));state.last=[e.clientX,e.clientY];renderSphere();}); canvas.addEventListener("pointerup",()=>state.dragging=false); canvas.addEventListener("wheel",e=>{e.preventDefault();state.zoom=Math.max(.7,Math.min(1.35,state.zoom-e.deltaY*.0007));renderSphere();},{passive:false});
}

async function init(){const response=await fetch(`${import.meta.env.BASE_URL}data/receiver.json`);if(!response.ok)throw new Error("receiver artifact unavailable");state.data=await response.json();bind();renderGoodputChart();renderFamilyChart();renderAll();}
init().catch(error=>document.body.innerHTML=`<pre class="fatal">TopoSense receiver failed to load\n${error.message}</pre>`);
