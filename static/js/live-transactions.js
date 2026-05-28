const txnData = [
  {name:"Pierre D.", country:"France", model:"Tesla Model 3 2025", fee:"$249 fee paid"},
  {name:"Sarah M.", country:"USA", model:"Tesla Model Y 2025", fee:"$329 fee paid"},
  {name:"Nguyen L.", country:"Vietnam", model:"Tesla Model S 2025", fee:"$399 fee paid"},
  {name:"Carlos R.", country:"Brazil", model:"Tesla Model X 2025", fee:"$299 fee paid"}
];

function showTxn(){
  const wrap = document.getElementById("liveTransactions");
  if(!wrap) return;

  const t = txnData[Math.floor(Math.random() * txnData.length)];
  const el = document.createElement("div");
  el.className = "txn-toast";
  el.innerHTML = `
    <div class="txn-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 6L9 17l-5-5"></path>
      </svg>
    </div>
    <div style="flex:1;min-width:0">
      <div class="txn-topline">${t.name} <span class="country">${t.country}</span></div>
      <div class="txn-sub">Just paid delivery fee for <span class="txn-model">${t.model}</span></div>
      <div class="txn-success">🚗 Car confirmed & dispatched! (${t.fee})</div>
      <div class="txn-progress"><span></span></div>
    </div>
  `;

  wrap.prepend(el);
  setTimeout(() => el.classList.add("hide"), 5200);
  setTimeout(() => el.remove(), 5600);
}

showTxn();
setInterval(showTxn, 8000);