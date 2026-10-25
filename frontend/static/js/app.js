let allProducts=[], filteredProducts=[], currentPage=1;
const pageSize=12;

function showPage(id){
 document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
 document.getElementById(id).classList.add('active');
 if(id==='products') renderProducts();
 if(id==='decisionLab') runDecisionLab();
 if(id==='wishlist') loadWishlist();
 if(id==='alerts') loadAlerts();
 window.scrollTo({top:0,behavior:'smooth'});
}

async function loadProducts(q=''){
 const r=await fetch('/api/products?search='+encodeURIComponent(q));
 filteredProducts=await r.json();
 allProducts=filteredProducts;
 currentPage=1;
 document.getElementById('productTotal').textContent=allProducts.length;
 renderProducts(); renderCategories();
}
function searchProducts(inputId){
 const q=document.getElementById(inputId).value.trim();
 loadProducts(q); showPage('products');
}
function productEnter(e){
 if(e.key==='Enter'){
   e.preventDefault();
   if(document.getElementById('products').classList.contains('active')) nextPage();
   else searchProducts('productSearch');
 }
}
function homeEnter(e){if(e.key==='Enter'){e.preventDefault();searchProducts('homeSearch');}}
document.addEventListener('DOMContentLoaded',()=>{
 document.getElementById('homeSearch').addEventListener('keydown',homeEnter);
 loadProducts(); updateCounts();
});

function nextPage(){
 const pages=Math.max(1,Math.ceil(filteredProducts.length/pageSize));
 if(currentPage<pages){currentPage++;renderProducts();}
}
function prevPage(){if(currentPage>1){currentPage--;renderProducts();}}
function renderProducts(){
 const pages=Math.max(1,Math.ceil(filteredProducts.length/pageSize));
 if(currentPage>pages) currentPage=pages;
 const rows=filteredProducts.slice((currentPage-1)*pageSize,currentPage*pageSize);
 document.getElementById('pageInfo').textContent=`Page ${currentPage} of ${pages} • ${filteredProducts.length} products`;
 document.getElementById('productGrid').innerHTML=rows.map(card).join('') || '<div class="empty">No products found.</div>';
}
function card(p){
 return `<article class="card">
  <div class="product-icon">${icon(p.category)}</div>
  <div class="tag">${esc(p.category)}</div>
  <h3>${esc(p.name)}</h3><p>${esc(p.brand)} · ${esc(p.description||'Compare prices across stores')}</p>
  <div class="card-actions">
   <button class="primary" onclick="showProduct(${p.id})">Compare Prices</button>
   <button class="secondary" onclick="addWish(${p.id})">♡ Wishlist</button>
  </div>
  <button class="online" onclick="searchOnlineFor('${escAttr(p.name)}')">🌐 Search Online</button>
 </article>`;
}
function icon(c){return ({Laptop:'💻',Mobile:'📱',Headphones:'🎧',Smartwatch:'⌚',Monitor:'🖥️',Keyboard:'⌨️',Mouse:'🖱️',Camera:'📷',Speaker:'🔊','Tablet & Reader':'📚',Storage:'💾',Networking:'📡',Gaming:'🎮','PC Components':'🧩',Webcam:'📹',Printer:'🖨️','Smart Home':'🏠','Home Appliances':'🧺',Fitness:'🏃',Accessories:'🔌',Projector:'📽️','Audio Equipment':'🎙️'})[c]||'🛍️'}
function esc(s){return String(s||'').replace(/[&<>"]/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[x]));}
function escAttr(s){return String(s||'').replace(/\\/g,'\\\\').replace(/'/g,"\\'");}

async function showProduct(id){
 const d=await fetch('/api/products/'+id).then(r=>r.json());
 const t=await fetch('/api/products/'+id+'/trend').then(r=>r.json());
 document.getElementById('modalBody').innerHTML=`
  <div class="eyebrow">PRICE COMPARISON</div><h2>${esc(d.product.name)}</h2>
  <p class="muted">${esc(d.product.description)}</p>
  <div class="modal-actions">
   <button class="primary" onclick="addWish(${id})">♡ Add to Wishlist</button>
   <button class="secondary" onclick="searchOnlineFor('${escAttr(d.product.name)}')">🌐 Search Online</button>
   <button class="secondary" onclick="createAlert(${id},'${escAttr(d.product.name)}')">🔔 Set Price Alert</button>
  </div>
  ${d.best_offer?`<div class="deal-hero"><div><span class="eyebrow">BEST EFFECTIVE OFFER</span><h3>₹${Number(d.best_offer.effective_price).toLocaleString('en-IN')}</h3><p>${esc(d.best_offer.store)} · saves ₹${Number(d.best_offer.discount_saving).toLocaleString('en-IN')} before delivery</p></div><div class="dna-score"><strong>${d.best_offer.deal_dna}</strong><span>Deal DNA / 100</span></div></div>`:''}
  <h3>Compare ${d.offers.length} sample-store offers</h3>
  <div class="buy-style-grid">
   ${buyStyleSummary(d.offers)}
  </div>
  <div class="offers">${d.offers.map(o=>`
   <div class="offer"><div><b>${esc(o.store)}</b><br><small>⭐ ${o.rating} · ${o.discount}% discount · Delivery ₹${o.delivery}<br>Sticker ₹${Number(o.price).toLocaleString('en-IN')} · Deal DNA ${o.deal_dna}/100</small></div>
   <strong>₹${Number(o.effective_price).toLocaleString('en-IN')}</strong></div>`).join('')}</div>
  <div class="trend"><b>Hidden Cost Radar:</b> Discount savings ₹${Number(d.best_offer?.discount_saving||0).toLocaleString('en-IN')} + delivery ₹${Number(d.best_offer?.delivery||0).toLocaleString('en-IN')} are included in the effective offer ranking.<br><b>Price trend:</b> ${esc(t.trend||'N/A')} &nbsp; <b>Estimated next:</b> ${t.estimated_next_price?'₹'+Number(t.estimated_next_price).toLocaleString('en-IN'):'Not enough data'}<br><small>Demo-store offers and estimated trends are sample data, not live retailer quotes.</small></div>`;
 document.getElementById('modal').classList.remove('hidden');
}
function buyStyleSummary(offers){
 if(!offers || !offers.length) return '';
 const lowest=[...offers].sort((a,b)=>a.effective_price-b.effective_price)[0];
 const free=[...offers].filter(o=>Number(o.delivery)===0).sort((a,b)=>a.effective_price-b.effective_price)[0];
 const discount=[...offers].sort((a,b)=>b.discount-a.discount)[0];
 const rating=[...offers].sort((a,b)=>b.rating-a.rating)[0];
 const tile=(label,o,detail)=>`<div class="buy-style"><span>${label}</span><b>${esc(o.store)}</b><small>${detail}</small></div>`;
 return tile('Lowest final cost',lowest,'₹'+Number(lowest.effective_price).toLocaleString('en-IN'))+
  tile('Free delivery',free||lowest,free?'₹'+Number(free.effective_price).toLocaleString('en-IN'):'No free-delivery offer')+
  tile('Biggest discount',discount,discount.discount+'% off')+
  tile('Highest rating',rating,'⭐ '+rating.rating+'/5');
}
function closeModal(){document.getElementById('modal').classList.add('hidden');}

async function addWish(id){
 const r=await fetch('/api/wishlist/'+id,{method:'POST'});
 if(r.ok){updateCounts(); loadWishlist();}
}
async function updateCounts(){
 const [w,a]=await Promise.all([fetch('/api/wishlist').then(r=>r.json()),fetch('/api/alerts').then(r=>r.json())]);
 document.getElementById('wishCount').textContent=w.length;
 document.getElementById('alertCount').textContent=a.length;
}
async function openWishlist(){showPage('wishlist');}
async function loadWishlist(){
 const data=await fetch('/api/wishlist').then(r=>r.json());
 document.getElementById('wishlistGrid').innerHTML=data.map(p=>`
  <article class="card"><div class="product-icon">♡</div><h3>${esc(p.name)}</h3>
  <div class="card-actions"><button class="primary" onclick="showProduct(${p.id})">Compare</button>
  <button class="online" onclick="searchOnlineFor('${escAttr(p.name)}')">🌐 Search Online</button></div></article>`
 ).join('') || '<div class="empty">Your wishlist is empty.</div>';
 updateCounts();
}
function renderCategories(){
 const cats=[...new Set(allProducts.map(p=>p.category))];
 document.getElementById('categoryGrid').innerHTML=cats.map(c=>`
  <button onclick="filterCategory('${escAttr(c)}')"><span>${icon(c)}</span><b>${esc(c)}</b><small>Browse products</small></button>`).join('');
}
function filterCategory(c){
 filteredProducts=allProducts.filter(p=>p.category===c); currentPage=1; showPage('products'); renderProducts();
}
function createAlert(id,name){
 closeModal(); showPage('alerts');
 document.getElementById('alertCreate').innerHTML=`<div><h3>${esc(name)}</h3><p>Enter the price at which you want to be notified.</p>
 <div class="search-row compact"><input id="targetPrice" type="number" min="1" placeholder="Target price in ₹"><button class="primary" onclick="saveAlert(${id})">Create Alert</button></div></div>`;
}
async function saveAlert(id){
 const target=Number(document.getElementById('targetPrice').value);
 if(!target)return alert('Please enter a target price.');
 const r=await fetch('/api/alerts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:id,target_price:target})});
 if(r.ok){document.getElementById('alertCreate').innerHTML='<div class="success">✓ Price alert created.</div>';loadAlerts();updateCounts();}
 else alert('Could not create alert.');
}
async function openAlerts(){showPage('alerts');}
async function loadAlerts(){
 const data=await fetch('/api/alerts').then(r=>r.json());
 document.getElementById('alertList').innerHTML=data.map(a=>`
  <div class="alert-item"><div><b>${esc(a.product_name)}</b><small>Target price: ₹${Number(a.target_price).toLocaleString('en-IN')} · ${a.active?'Active':'Inactive'}</small></div>
  <button class="danger" onclick="deleteAlert(${a.id})">Remove</button></div>`
 ).join('') || '<div class="empty">No price alerts yet.</div>';
 updateCounts();
}
async function deleteAlert(id){
 await fetch('/api/alerts/'+id,{method:'DELETE'}); loadAlerts(); updateCounts();
}
async function runDecisionLab(){
 const input=document.getElementById('labBudget');
 if(!input)return;
 const budget=Number(input.value||50000);
 const results=document.getElementById('labResults');
 const summary=document.getElementById('labSummary');
 if(budget<=0){summary.textContent='Enter a budget greater than zero.';results.innerHTML='';return;}
 results.innerHTML='<div class="empty">Finding best-fit buys…</div>';
 try{
  const data=await fetch('/api/decision-lab?budget='+encodeURIComponent(budget)).then(r=>r.json());
  summary.textContent=`${data.length} products fit within ₹${budget.toLocaleString('en-IN')}. Ranked by the demo Deal DNA score, then price.`;
  results.innerHTML=data.map(p=>`<article class="card lab-card"><div class="product-icon">${icon(p.category)}</div><div class="tag">${esc(p.category)}</div><h3>${esc(p.name)}</h3><p>${esc(p.brand)} · Best offer at ${esc(p.store)}</p><div class="lab-price">₹${Number(p.best_price).toLocaleString('en-IN')}</div><div class="lab-metrics"><span><b>${p.deal_dna}</b><small>Deal DNA</small></span><span><b>₹${Number(p.budget_left).toLocaleString('en-IN')}</b><small>Budget left</small></span><span><b>⭐ ${p.rating}</b><small>Offer rating</small></span></div><div class="card-actions"><button class="primary" onclick="showProduct(${p.id})">Inspect deal</button><button class="secondary" onclick="addWish(${p.id})">♡ Wishlist</button></div></article>`).join('')||'<div class="empty">No matching products under this budget. Try increasing it.</div>';
 }catch(e){summary.textContent='Could not load recommendations. Check that the backend is running.';results.innerHTML='';}
}

function searchOnlineFor(name){
 const q=encodeURIComponent(name);
 window.open('https://www.google.com/search?tbm=shop&q='+q,'_blank');
}
