// Shared by the error screens. <body data-loop="..." data-once="ms"> names the
// looping GIF to switch to once the play-once GIF has finished.
(function(){
  var b=document.body,d=document.getElementById("dialog");
  // Not when reduced motion swapped in the still PNG
  if(d&&b.dataset.loop)setTimeout(function(){if(/\.gif$/.test(d.currentSrc))d.src=b.dataset.loop},+b.dataset.once||3000);
  // Seattle time in the tray, like the home page
  var c=document.getElementById("clock");
  if(c&&window.Intl){var f=new Intl.DateTimeFormat("en-US",{hour:"numeric",minute:"2-digit",timeZone:"America/Los_Angeles"});
    var tick=function(){c.textContent=f.format(new Date())};tick();setInterval(tick,15000)}
  // Esc goes home too
  addEventListener("keydown",function(e){if(e.key==="Escape")location.href="/"});
})();
