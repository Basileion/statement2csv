import sys, json, shutil, os; sys.path.insert(0, '/workspace/basileion-sites')
from common import Site, e
C = '2026-11-20'
INTUIT = 'https://quickbooks.intuit.com/learn-support/en-us/help-article/import-transactions/manually-upload-transactions-quickbooks-online/L0rE9OXBz_US_en_US'
INTUIT2 = 'https://quickbooks.intuit.com/learn-support/en-us/help-article/bank-transactions/format-csv-files-excel-bank-transactions-quickbooks/L4BjLWckq_US_en_US'
s = Site('statement2csv', 'Statement<span>2CSV</span>', 'Statement2CSV',
         [('Converter', '/'), ('QuickBooks CSV', '/quickbooks-csv/'), ('PDF to Excel', '/pdf-to-excel/'), ('Privacy', '/privacy/')],
         '<b>Statement2CSV</b> converts text-based bank and card statement PDFs to CSV in your browser using Mozilla pdf.js. Files never leave your device. Scanned (image) PDFs are not supported. Always check totals against the statement.', acc='#0f6b4f', acc2='#e6f3ee')
os.makedirs(s.D + '/vendor', exist_ok=True)
for f in ('pdf.min.mjs', 'pdf.worker.min.mjs'): shutil.copy(f'/workspace/statement2csv/node_modules/pdfjs-dist/build/{f}', s.D + '/vendor/' + f)
shutil.copy('/workspace/statement2csv/node_modules/pdfjs-dist/LICENSE', s.D + '/vendor/PDFJS-LICENSE')
P = open('/workspace/statement2csv/scripts/parse.js').read()
TOOL = f"""<div class="card"><label style="display:flex">Statement PDF (text-based)<input type="file" id="f" accept="application/pdf" multiple></label>
<p><label>Year for dates without one<input id="yr" placeholder="e.g. 2026" style="width:110px"></label> <label>Format<select id="fmt"><option value="g">Date, Description, Amount, Balance</option><option value="q">QuickBooks 3-column (Date, Description, Amount)</option></select></label> <label style="flex-direction:row;gap:6px;align-items:center"><input type="checkbox" id="flip" style="min-width:0">Flip signs (card statements)</label></p>
<p id="st" class="mut">Choose a PDF. Nothing is uploaded: parsing runs on this page.</p>
<p><button class="btn" id="dl" disabled>Download CSV</button> <button class="btn" id="cp" disabled style="background:var(--mut)">Copy for Excel / Sheets</button></p></div>
<div id="sum"></div><div class="tw" id="out"></div>
<script>{P}</script><script type="module">
import * as pdfjs from '{s.BASE}/vendor/pdf.min.mjs';pdfjs.GlobalWorkerOptions.workerSrc='{s.BASE}/vendor/pdf.worker.min.mjs';
let rows=[];const $=id=>document.getElementById(id);
async function load(files){{rows=[];let pages=0;for(const file of files){{const doc=await pdfjs.getDocument({{data:new Uint8Array(await file.arrayBuffer())}}).promise;const items=[];pages+=doc.numPages;
for(let p=1;p<=doc.numPages;p++){{const tc=await (await doc.getPage(p)).getTextContent();for(const i of tc.items)items.push({{str:i.str,x:i.transform[4],y:i.transform[5],page:p}})}}
if(!items.length){{$('st').textContent=file.name+': no text layer found. This looks like a scanned PDF, which is not supported.';continue}}
rows=rows.concat(parseLines(linesFromItems(items)))}}
$('st').textContent=rows.length+' transactions found across '+pages+' page(s). Review before importing.';render()}}
function d(x){{const y=$('yr').value.trim();return (/^\\d{{1,2}}[/.-]\\d{{1,2}}$/.test(x)&&y)?x+'/'+y:x}}
function cur(){{const f=$('flip').checked?-1:1;return rows.map(r=>({{date:d(r.date),desc:r.desc,amount:Math.round(r.amount*f*100)/100,balance:r.balance}}))}}
function table(){{const q=$('fmt').value==='q';const h=q?['Date','Description','Amount']:['Date','Description','Amount','Balance'];return [h].concat(cur().map(r=>q?[r.date,r.desc.replace(/\\d/g,'').replace(/\\s+/g,' ').trim(),r.amount.toFixed(2)]:[r.date,r.desc,r.amount.toFixed(2),r.balance==null?'':r.balance.toFixed(2)]))}}
function render(){{const t=table(),c=cur();const inn=c.filter(r=>r.amount>0).reduce((a,r)=>a+r.amount,0),out=c.filter(r=>r.amount<0).reduce((a,r)=>a+r.amount,0);
$('sum').innerHTML=c.length?'<div class="grid"><div class="card"><div class="mut">Rows</div><div class="big">'+c.length+'</div></div><div class="card"><div class="mut">Money in</div><div class="big">'+inn.toFixed(2)+'</div></div><div class="card"><div class="mut">Money out</div><div class="big">'+out.toFixed(2)+'</div><div>Compare with the statement summary</div></div></div>':'';
$('out').innerHTML='<table><thead><tr>'+t[0].map(h=>'<th style="text-align:left">'+h+'</th>').join('')+'</tr></thead><tbody>'+t.slice(1).map(r=>'<tr>'+r.map(v=>'<td style="text-align:left">'+String(v).replace(/</g,'&lt;')+'</td>').join('')+'</tr>').join('')+'</tbody></table>';$('dl').disabled=$('cp').disabled=!c.length}}
const csv=()=>table().map(r=>r.map(v=>/[",\\n]/.test(v)?'"'+String(v).replace(/"/g,'""')+'"':v).join(',')).join('\\r\\n');
$('f').onchange=ev=>load([...ev.target.files]).catch(err=>$('st').textContent='Could not read PDF: '+err.message);
['yr','fmt','flip'].forEach(i=>$(i).addEventListener('input',render));
$('dl').onclick=()=>{{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv()],{{type:'text/csv'}}));a.download='statement.csv';a.click()}};
$('cp').onclick=()=>navigator.clipboard.writeText(table().map(r=>r.join('\\t')).join('\\n')).then(()=>$('st').textContent='Copied. Paste into Excel or Google Sheets.');
</script>"""
HOW = """<h2>How it works</h2><ol><li>pdf.js reads the PDF's text layer in your browser.</li><li>Text is regrouped into lines by position. A line that starts with a date and ends with money amounts becomes a transaction; short lines below it are joined to its description.</li><li>When a running balance is printed, each amount's sign is set from the change in balance, so withdrawals come out negative.</li><li>Opening and previous-balance lines are dropped.</li></ol>
<h2>Limits</h2><ul><li>Scanned or photographed statements have no text layer and are not supported (no OCR).</li><li>Layouts vary by bank. Check the row count and the money-in / money-out totals against your statement before importing.</li><li>Without a balance column, unsigned amounts stay positive; use Flip signs or fix in your spreadsheet.</li></ul>"""
s.page('/', 'Bank Statement PDF to CSV / Excel Converter (Free, Private, No Upload) | Statement2CSV',
       'Convert a text-based bank or credit card statement PDF to CSV or Excel in your browser. No upload, no sign-up. QuickBooks 3-column export.',
       '<p class="eb" style="margin-top:34px">Free · runs in your browser · no upload</p><h1>Bank statement PDF to CSV, in your browser</h1><p class="lede">Drop a text-based statement PDF. Get Date, Description, Amount and Balance as CSV, ready for Excel, Google Sheets or a QuickBooks upload. The file never leaves your device.</p>' + TOOL + HOW,
       schema={'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'Statement2CSV', 'applicationCategory': 'FinanceApplication', 'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': 0, 'priceCurrency': 'USD'}, 'url': s.SITE + '/'})
s.page('/quickbooks-csv/', 'QuickBooks Online Bank CSV Format (3-Column) from a PDF Statement | Statement2CSV',
       'The CSV layouts QuickBooks Online accepts for bank uploads, per Intuit, and a free in-browser converter from PDF statements to the 3-column format.',
       f"""<p class="eb" style="margin-top:34px">Guide · Intuit docs checked {C}</p><h1>QuickBooks Online bank CSV format</h1>
<p>Per Intuit's help articles:</p><ul><li>Each upload file needs either 3 columns (Date, Description, Amount) or 4 columns (Date, Description, Credit, Debit).</li><li>In the 3-column layout, payments are negative and deposits positive.</li><li>The upload file must be 350 KB or less.</li><li>Leave zero-only amount cells blank, remove numbers from the Description column, and keep every date in one format (Intuit recommends dd/mm/yyyy).</li></ul>
<p class="note">Sources: <a href="{INTUIT}" rel="nofollow noopener">Manually upload transactions into QuickBooks Online</a>; <a href="{INTUIT2}" rel="nofollow noopener">Format CSV files in Excel</a>.</p>
<h2>Convert a PDF statement to that format</h2><p>Choose "QuickBooks 3-column" in the converter. It writes signed amounts with no currency symbols or thousands separators and strips digits from descriptions.</p>{TOOL}""")
for path, t, kw in [('/pdf-to-excel/', 'Bank Statement PDF to Excel (Free, No Upload)', 'Excel'), ('/pdf-to-csv/', 'Bank Statement PDF to CSV (Free, No Upload)', 'CSV'), ('/credit-card-statement-to-csv/', 'Credit Card Statement PDF to CSV (Free, No Upload)', 'CSV')]:
    s.page(path, t + ' | Statement2CSV', f'Turn a text-based statement PDF into {kw} in your browser. Nothing is uploaded.',
           f'<p class="eb" style="margin-top:34px">Free · runs in your browser</p><h1>{e(t)}</h1><p class="lede">Open the CSV in {kw if kw=="Excel" else "any spreadsheet"}, or use Copy for Excel / Sheets to paste rows directly.' + (' Card statements often print purchases as positive amounts; tick Flip signs if you want money out negative.' if 'Credit' in t else '') + '</p>' + TOOL + HOW)
s.page('/privacy/', 'Privacy: Statements Never Leave Your Browser | Statement2CSV', 'How Statement2CSV processes statements locally with pdf.js.',
       '<h1>Privacy</h1><ul><li>The converter is a static page. Your PDF is read with <a href="https://mozilla.github.io/pdf.js/" rel="nofollow noopener">Mozilla pdf.js</a> (Apache-2.0, served from this site) inside your browser tab.</li><li>No file, row or amount is sent to any server. There is no account and no analytics script on this site.</li><li>You can verify this by opening your browser\'s network tab while converting, or by loading the page and then going offline.</li></ul>')
s.page('/about/', 'Methodology | Statement2CSV', 'How Statement2CSV parses statements.', '<h1>Methodology</h1>' + HOW)
s.changes([{'date': C, 'title': 'Launch', 'text': 'Converter, QuickBooks 3-column export, copy-to-spreadsheet.'}], C)
s.finish(C, f'# Statement2CSV\n> Free in-browser converter from text-based bank statement PDFs to CSV / Excel / QuickBooks 3-column. No upload.\n\n- Converter: {s.SITE}/\n- QuickBooks format guide: {s.SITE}/quickbooks-csv/ (source: {INTUIT})\n')
