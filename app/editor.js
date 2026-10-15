const canvas=document.getElementById('canvas');
const ctx=canvas.getContext('2d');
const maskCanvas=document.createElement('canvas');
const maskCtx=maskCanvas.getContext('2d');
let img=new Image(), maskMode=false, dirty=false;

function status(t){document.getElementById('status').textContent=t}
function fit(){
  if(!img.width)return;
  const s=Math.min(900/img.width,600/img.height,1);
  canvas.width=Math.round(img.width*s);
  canvas.height=Math.round(img.height*s);
  maskCanvas.width=canvas.width;
  maskCanvas.height=canvas.height;
  maskCtx.clearRect(0,0,maskCanvas.width,maskCanvas.height);
  ctx.drawImage(img,0,0,canvas.width,canvas.height);
}
function drawMaskStroke(x,y){
  maskCtx.fillStyle='rgba(255,255,255,1)';
  maskCtx.beginPath();
  maskCtx.arc(x,y,24,0,Math.PI*2);
  maskCtx.fill();
  ctx.drawImage(img,0,0,canvas.width,canvas.height);
  ctx.fillStyle='rgba(255,0,0,.35)';
  ctx.drawImage(maskCanvas,0,0);
}
function canvasBlob(c){return new Promise(r=>c.toBlob(r,'image/png'))}

document.getElementById('file').onchange=e=>{
  const f=e.target.files[0]; if(!f)return;
  img.onload=()=>{fit();status('تم تحميل الصورة.')};
  img.src=URL.createObjectURL(f);
};

document.querySelectorAll('[data-cmd]').forEach(b=>b.onclick=()=>{
  if(!img.width)return;
  const c=b.dataset.cmd;
  const old=document.createElement('canvas');
  old.width=canvas.width; old.height=canvas.height;
  old.getContext('2d').drawImage(canvas,0,0);

  if(c==='rotate'){
    canvas.width=old.height; canvas.height=old.width;
    maskCanvas.width=canvas.width; maskCanvas.height=canvas.height;
    ctx.save();ctx.translate(canvas.width/2,canvas.height/2);ctx.rotate(Math.PI/2);
    ctx.drawImage(old,-old.width/2,-old.height/2);ctx.restore();
  }else if(c==='flip'){
    ctx.save();ctx.translate(canvas.width,0);ctx.scale(-1,1);ctx.drawImage(old,0,0);ctx.restore();
  }else{
    const data=ctx.getImageData(0,0,canvas.width,canvas.height),d=data.data;
    const amt=c==='bright'?18:1.15;
    for(let i=0;i<d.length;i+=4){
      if(c==='bright'){
        d[i]=Math.min(255,d[i]+amt);d[i+1]=Math.min(255,d[i+1]+amt);d[i+2]=Math.min(255,d[i+2]+amt);
      }else{
        d[i]=Math.min(255,d[i]*amt);d[i+1]=Math.min(255,d[i+1]*amt);d[i+2]=Math.min(255,d[i+2]*amt);
      }
    }
    ctx.putImageData(data,0,0);
  }
  dirty=true;
  status('تم تطبيق التعديل السريع.');
});

document.getElementById('mask').onclick=()=>{
  maskMode=!maskMode;
  status(maskMode?'ارسم بالماوس على المنطقة التي تريد أن يضيف/يعدل فيها AI.':'تم إيقاف وضع القناع.');
};
canvas.onpointerdown=e=>{if(!maskMode)return;canvas.setPointerCapture(e.pointerId);paint(e)};
canvas.onpointermove=e=>{if(maskMode&&e.buttons===1)paint(e)};
function paint(e){
  const r=canvas.getBoundingClientRect();
  const x=e.clientX-r.left,y=e.clientY-r.top;
  drawMaskStroke(x,y);
}
document.getElementById('clearMask').onclick=()=>{
  maskCtx.clearRect(0,0,maskCanvas.width,maskCanvas.height);
  ctx.drawImage(img,0,0,canvas.width,canvas.height);
  status('تم مسح القناع.');
};

document.getElementById('check').onclick=async()=>{
  try{
    const r=await fetch('/api/comfy/status'); const j=await r.json();
    status(j.ok?'ComfyUI متصل — النموذج: '+j.model:'ComfyUI غير متصل: '+(j.message||''));
  }catch(e){status('تعذر الاتصال بالخادم المحلي. شغّل start-v5.bat.')}
};

document.getElementById('ai').onclick=async()=>{
  if(!img.width)return status('حمّل صورة أولًا.');
  const maskData=maskCtx.getImageData(0,0,maskCanvas.width,maskCanvas.height).data;
  let hasMask=false;
  for(let i=0;i<maskData.length;i+=4){if(maskData[i]>0){hasMask=true;break}}
  if(!hasMask)return status('ارسم منطقة القناع أولًا.');
  const imageBlob=await canvasBlob(canvas);

  const cleanMask=document.createElement('canvas');
  cleanMask.width=maskCanvas.width;cleanMask.height=maskCanvas.height;
  const mc=cleanMask.getContext('2d');
  mc.fillStyle='#000';mc.fillRect(0,0,cleanMask.width,cleanMask.height);
  mc.drawImage(maskCanvas,0,0);

  const maskBlob=await canvasBlob(cleanMask);
  const fd=new FormData();
  fd.append('image',imageBlob,'input.png');
  fd.append('mask',maskBlob,'mask.png');
  fd.append('prompt',document.getElementById('prompt').value);
  status('جاري تنفيذ التعديل محليًا... قد يستغرق وقتًا على هذا الجهاز.');
  try{
    const r=await fetch('/api/edit',{method:'POST',body:fd});
    const j=await r.json();
    if(j.image){
      img.onload=()=>{fit();status('تم تنفيذ التعديل بنجاح.')};
      img.src=j.image;
    }else status(j.message||'لم يتم الحصول على نتيجة.');
  }catch(e){status('تعذر تنفيذ AI: '+e.message)}
};
