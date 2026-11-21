// Statement line parser: works on text lines [{text, items}] rebuilt from PDF text positions
const MON='(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\\.?';
const DATE_RE=new RegExp('^(\\d{1,2}[/.-]\\d{1,2}(?:[/.-]\\d{2,4})?|\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\\s'+MON+'(?:\\s\\d{2,4})?|'+MON+'\\s\\d{1,2}(?:,?\\s\\d{4})?)(?=\\s|$)','i');
const AMT_RE=/^(?:\(?-?[$£€]?\d{1,3}(?:,\d{3})*\.\d{2}\)?-?|\(?-?[$£€]?\d+\.\d{2}\)?-?)(?:\s?(?:CR|DR))?$/i;
function num(t){let s=t.trim(),neg=false;if(/\(.*\)/.test(s))neg=true;if(/-$/.test(s)||/^-|^\(?-/.test(s))neg=true;if(/DR$/i.test(s))neg=true;const v=parseFloat(s.replace(/CR|DR/ig,'').replace(/[^0-9.]/g,''));return{v:neg?-v:v,explicit:neg||/CR$/i.test(s)}}
function linesFromItems(items){ // items: {str,x,y,page}
 const rows=[];const sorted=items.filter(i=>i.str.trim()).sort((a,b)=>a.page-b.page||b.y-a.y||a.x-b.x);
 for(const it of sorted){let r=rows.length?rows[rows.length-1]:null;if(!r||r.page!==it.page||Math.abs(r.y-it.y)>2.5){r={page:it.page,y:it.y,items:[]};rows.push(r)}r.items.push(it)}
 return rows.map(r=>{r.items.sort((a,b)=>a.x-b.x);return r.items.map(i=>i.str.trim()).filter(Boolean)})}
function parseLines(lines){ // lines: array of token arrays
 const out=[];let last=null;
 for(const toks of lines){const line=toks.join(' ').replace(/\s+/g,' ').trim();const m=line.match(DATE_RE);
  const amts=[];let rest=toks.slice();while(rest.length&&AMT_RE.test(rest[rest.length-1].replace(/\s+/g,' '))){amts.unshift(rest.pop())}
  if(m&&amts.length){let desc=rest.join(' ').replace(/\s+/g,' ').trim().slice(m[1].length).trim();
   // drop a second leading date (posting vs transaction date)
   const m2=desc.match(DATE_RE);let date2=null;if(m2){date2=m2[1];desc=desc.slice(m2[1].length).trim()}
   const n=amts.map(num);const row={date:m[1],desc,amount:n[0].v,explicit:n[0].explicit,balance:n.length>1?n[n.length-1].v:null};
   if(n.length===1&&/(opening|beginning|previous|starting)\s+balance|balance\s+(forward|brought)/i.test(desc)){row.balance=n[0].v;row.isBal=true}
   out.push(row);last=row}
  else if(last&&!m&&!amts.length&&line.length<80&&!/balance|total|page \d|statement|continued/i.test(line)){last.desc=(last.desc+' '+line).trim()}
  else last=null}
 // sign inference from running balance
 for(let i=1;i<out.length;i++){const p=out[i-1],r=out[i];if(r.balance!=null&&p.balance!=null){const d=Math.round((r.balance-p.balance)*100)/100;if(Math.abs(Math.abs(d)-Math.abs(r.amount))<0.005)r.amount=d;}}
 return out.filter(r=>!r.isBal)}
if(typeof module!=='undefined')module.exports={parseLines,linesFromItems,DATE_RE,AMT_RE};
