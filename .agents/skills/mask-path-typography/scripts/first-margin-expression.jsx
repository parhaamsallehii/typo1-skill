// Paste on First Margin in After Effects. Text is attached to a smooth mask path.
// Four First Margin base keys: entry frames 1/5, then exit frames 1/5.
// Bounce only after the entry-arrival key, never from the start of exit.
var amp=.16, freq=2.5, decay=5.5, duration=1, fadeDuration=.2, maxOffset=300;
var n=0;
if(numKeys>0){n=nearestKey(time).index;if(key(n).time>time)n--;}
var result=value;
if(n===2){
  var t=time-key(n).time;
  if(t>0 && t<duration){
    var v=velocityAtTime(key(n).time-thisComp.frameDuration/10);
    var envelope=1;
    if(t>duration-fadeDuration){
      var u=(t-(duration-fadeDuration))/fadeDuration;
      envelope=1-u*u*(3-2*u);
    }
    var amplitude=Math.max(-maxOffset,Math.min(maxOffset,v*amp));
    result=value+amplitude*Math.sin(2*Math.PI*freq*t)*Math.exp(-decay*t)*envelope;
  }
}
result;
