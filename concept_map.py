"""Offline SVG concept map: curated, conditional relationships and hover details."""
import json

# TERMS indices are stable within glossary_ui; relationships are editorial context.
LINKS=[
(0,1,'기조 확인','근원 CPI는 식품·에너지를 제외해 CPI의 지속성을 살핀다.'),
(2,0,'가격 전가','생산자 가격은 수요·기업 마진에 따라 소비자 가격으로 전가될 수 있다.'),
(0,6,'정책 판단','물가 흐름은 금리 판단의 재료다. 고용·전망도 함께 고려한다.'),
(3,4,'기조 확인','근원 PCE는 식품·에너지를 제외한 PCE 물가다.'),
(3,9,'물가 목표','연준은 PCE 물가를 물가 목표의 기준으로 사용한다.'),
(4,6,'정책 기대','기조적 물가 변화는 예상 정책 경로에 영향을 줄 수 있다.'),
(5,0,'측정','CPI는 소비 단계의 물가 변화를 측정하는 지표다.'),
(9,6,'금리 결정','FOMC는 미국 통화정책 방향과 정책금리 목표 범위를 결정한다.'),
(10,9,'정책 성향','매파·비둘기파는 중앙은행의 정책 우선순위를 설명한다.'),
(6,7,'금리 경로','국채 수익률은 정책 경로 기대와 기간 프리미엄 등의 영향을 받는다.'),
(7,8,'금리차 계산','10년물 수익률에서 2년물 수익률을 빼서 곡선의 기울기를 살핀다.'),
(6,21,'금리차','국가 간 금리차와 예상 경로는 환율의 여러 결정 요인 중 하나다.'),
(7,25,'할인율','금리는 주식의 할인율과 연결되지만 기업 실적도 함께 작용한다.'),
(11,12,'경기·고용','성장과 고용은 생산성·경제활동참가율 등에 따라 함께 변화할 수 있다.'),
(13,12,'고용 지표','NFP와 실업률은 다른 조사로 측정해 노동시장을 함께 살핀다.'),
(14,12,'고용 선행 단서','신규 청구 증가는 고용 악화의 단서일 수 있으나 주간 변동을 확인한다.'),
(15,13,'노동 수요','구인·채용·퇴직 흐름은 고용 변화와 임금 압력을 해석하는 자료다.'),
(13,6,'정책 판단','고용은 물가·경기 전망과 함께 정책 판단에 반영된다.'),
(16,11,'소비 흐름','소매판매는 소비 경기의 일부를 보여주며 서비스 소비 전체를 포함하지 않는다.'),
(17,11,'생산 흐름','산업생산은 생산 부문의 경기 방향을 보여준다.'),
(18,16,'소비 기대','소비 심리는 지출 의향의 단서지만 실제 지출 증가를 보장하지 않는다.'),
(20,19,'수지 범위','경상수지는 상품 무역뿐 아니라 서비스·소득 거래도 포함한다.'),
(20,11,'순수출','순수출은 GDP 구성 요소다. 수출만으로 전체 성장을 판단하지 않는다.'),
(21,20,'가격·채산성','환율은 계약 통화와 시차에 따라 수출입 가격·채산성에 영향을 준다.'),
(21,0,'수입물가','통화 약세가 수입 가격을 높일 수 있으나 소비자 가격 전가는 다르다.'),
(22,21,'달러 흐름','달러지수와 개별 환율은 구성 통화·국내 여건에 따라 다르게 움직인다.'),
(27,2,'생산 비용','유가 변화는 에너지·운송 비용을 통해 생산자 가격에 영향을 줄 수 있다.'),
(27,0,'에너지 물가','소비자물가 영향은 에너지 가중치·환율·정책에 따라 달라진다.'),
(28,25,'변동성 기대','VIX는 S&P 500 옵션의 예상 변동성을 나타내며 방향을 확정하지 않는다.'),
(24,25,'시장 비교','한국·미국 지수는 글로벌 위험 선호와 연결되나 업종 구성·환율이 다르다.'),
(26,21,'통화 환산','지역 주식의 해외 투자 수익은 주가와 환율 변화의 영향을 함께 받는다.'),
(29,6,'유동성 기대','디지털 자산은 유동성·위험 선호 외에도 규제 등 고유 요인에 반응한다.'),
(30,0,'비교 기간','전월비·전년비를 구분해야 물가 변화 속도를 해석할 수 있다.'),
(31,6,'단위 해석','금리 수준의 차이는 %p 또는 bp로 표시한다.'),
(32,13,'통계 해석','계절조정과 과거 수정치는 고용 추세 해석에 영향을 준다.'),
(33,0,'예상과 차이','시장 반응은 물가 수준 외에도 예상치와의 차이에 좌우된다.'),
(34,24,'가격 기준','종가 기준 극값은 장중 최고·최저와 다르다.'),
(35,0,'시점 구분','물가 대상 기간·발표일·조회 시각을 구분한다.'),
(23,11,'규모 대비 비율','투자·부채의 GDP 대비 비율은 경제 규모 대비 수준을 보여준다.'),
]

def html(terms):
    nodes=[dict(id=i,category=t[0],name=t[1],meaning=t[3],impact=t[4],reading=t[5]) for i,t in enumerate(terms)]
    payload=json.dumps({'nodes':nodes,'edges':LINKS},ensure_ascii=False).replace('<','\\u003c')
    return '''<!doctype html><html lang="ko"><meta charset="utf-8"><style>
body{margin:0;color:#243445;font:14px Pretendard,'Malgun Gothic',sans-serif}button,select{font:inherit;padding:8px 12px;border:1px solid #d6dce0;border-radius:6px;background:white;color:#243445}header{display:flex;gap:10px;align-items:center;margin:4px 0 12px;flex-wrap:wrap}#map{border:1px solid #e1e4e7;border-radius:10px;overflow:auto;background:radial-gradient(ellipse at 50% 45%,#fff2ec 0%,#fafbfc 65%)}svg{display:block;min-width:680px;width:100%}.edge{stroke:#9baab7;stroke-width:1.4;fill:none;stroke-dasharray:5 4}.edge:hover{stroke:#e14d00;stroke-width:3}.hit{stroke:transparent;stroke-width:18;fill:none;cursor:help}.node{cursor:pointer}.node:hover .shape,.node:focus .shape{stroke:#e14d00;stroke-width:2.5}.tip{display:none;position:fixed;z-index:5;background:#fff;border:1px solid #b9c3cb;border-radius:8px;padding:14px;max-width:340px;box-shadow:0 6px 24px #152d4320;pointer-events:none;line-height:1.65;font-size:13px}.tip b{display:block;color:#152d43;margin-bottom:5px}#detail{margin-top:12px;line-height:1.7;padding:12px 16px;background:#fff2ec;border-radius:6px}small{color:#657383}text{font-family:inherit}
@keyframes map-enter{from{opacity:0}to{opacity:1}}@media(prefers-reduced-motion:no-preference){.node{animation:map-enter 180ms ease-out}.node rect{transition:stroke 140ms ease-out,fill 140ms ease-out}}@media(prefers-reduced-motion:reduce){.node{animation:none}.node rect{transition:none}}</style><header><label for="focus">중심 개념</label><select id="focus"></select><button id="all">전체 지도</button><button id="reset">CPI 중심으로</button><small>개념: 마우스·클릭 / 선: 마우스로 관계 확인</small></header><div id="map"><svg id="svg" viewBox="0 0 1000 530" role="img" aria-label="경제 개념 연결 지도"></svg></div><div id="detail" aria-live="polite">연결선 위에 마우스를 올리면 관계와 조건을 확인할 수 있습니다.</div><div class="tip" id="tip"></div><script>
const data=PAYLOAD, ns='http://www.w3.org/2000/svg', svg=document.getElementById('svg'), tip=document.getElementById('tip'),detail=document.getElementById('detail'),select=document.getElementById('focus');
data.nodes.forEach(n=>{let o=document.createElement('option');o.value=n.id;o.textContent=n.name;select.append(o)});
function el(tag,attrs,parent=svg){let e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));parent.append(e);return e}
function show(ev,title,body){tip.replaceChildren();let b=document.createElement('b');b.textContent=title;tip.append(b,document.createTextNode(body));tip.style.display='block';tip.style.left=Math.max(8,Math.min(ev.clientX+12,innerWidth-370))+'px';tip.style.top=Math.max(8,Math.min(ev.clientY+12,innerHeight-190))+'px'}
function hide(){tip.style.display='none'}
function draw(all=false){hide();svg.replaceChildren();let defs=el('defs',{});let filter=el('filter',{id:'shadow',x:'-30%',y:'-50%',width:'160%',height:'200%'},defs);el('feDropShadow',{dx:0,dy:4,stdDeviation:5,'flood-color':'#203050','flood-opacity':'.10'},filter);let focus=Number(select.value),edges=all?data.edges:data.edges.filter(e=>e[0]===focus||e[1]===focus),ids=all?data.nodes.map(n=>n.id):[focus,...new Set(edges.flatMap(e=>[e[0],e[1]]).filter(i=>i!==focus))],pos={};
let h=all?Math.ceil(ids.length/4)*92+50:Math.max(530,Math.ceil((ids.length-1)/2)*100+60);svg.setAttribute('viewBox',`0 0 1000 ${h}`);
ids.forEach((id,i)=>{pos[id]=all?[130+(i%4)*245,50+Math.floor(i/4)*92]:(i===0?[500,h/2]:[i%2?155:845,60+Math.floor((i-1)/2)*100])});
edges.forEach(e=>{let [a,b,label,note]=e,[x,y]=pos[a],[xx,yy]=pos[b],path=`M${x},${y} C${(x+xx)/2},${y} ${(x+xx)/2},${yy} ${xx},${yy}`;el('path',{d:path,class:'edge'});let hit=el('path',{d:path,class:'hit',tabindex:0,role:'button','aria-label':label+'。'+note});hit.addEventListener('mousemove',v=>show(v,label,note));hit.addEventListener('mouseleave',hide);hit.addEventListener('focus',()=>{detail.textContent=data.nodes[a].name+' → '+data.nodes[b].name+' / '+label+'：'+note});hit.addEventListener('click',()=>{detail.textContent=data.nodes[a].name+' → '+data.nodes[b].name+' / '+label+'：'+note});if(!all){let t=el('text',{x:(x+xx)/2,y:(y+yy)/2-6,'text-anchor':'middle',fill:'#536575','font-size':12,'paint-order':'stroke',stroke:'#fafbfc','stroke-width':5});t.textContent=label}});
ids.forEach(id=>{let n=data.nodes[id],[x,y]=pos[id],g=el('g',{class:'node',tabindex:0,role:'button','aria-label':n.name,transform:`translate(${x},${y})`});let theme={'물가':['#fff0e6','#ed8a4d','pill'],'금리·채권':['#eeeaff','#9c88e5','hex'],'경기·고용':['#e5f6ed','#72bd96','round'],'무역·통화':['#e5f2ff','#79acda','hex'],'시장':['#fde9f1','#d58caa','round'],'읽는 법':['#fff6d6','#cfb65f','pill']}[n.category]||['white','#cbd4db','round'];let attrs={class:'shape',fill:id===focus?'#ffe1cc':theme[0],stroke:id===focus?'#ff6600':theme[1],'stroke-width':id===focus?2.5:1.3,filter:'url(#shadow)'};if(theme[2]==='hex'){el('polygon',{...attrs,points:'-112,0 -94,-31 94,-31 112,0 94,31 -94,31'},g)}else{el('rect',{...attrs,x:-112,y:-31,width:224,height:62,rx:theme[2]==='pill'?31:16},g)};let t=el('text',{'text-anchor':'middle',y:-3,fill:'#152d43','font-size':n.name.length>24?11:13,'font-weight':600},g);t.textContent=n.name;let c=el('text',{'text-anchor':'middle',y:16,fill:'#657383','font-size':11},g);c.textContent=n.category;g.addEventListener('mousemove',e=>show(e,n.name,n.meaning));g.addEventListener('mouseleave',hide);function choose(){select.value=id;detail.textContent=n.name+'：'+n.meaning+' 市場 영향：'+n.impact+' 읽는 법：'+n.reading;draw()}g.addEventListener('click',choose);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose()}});g.addEventListener('focus',()=>{detail.textContent=n.name+'：'+n.meaning})});}
select.onchange=()=>draw();document.getElementById('all').onclick=()=>draw(true);document.getElementById('reset').onclick=()=>{select.value=0;draw()};draw();
</script></html>'''.replace('PAYLOAD',payload).replace('市場 영향','시장 영향')
