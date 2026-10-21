// Paste on First Margin in After Effects. Text is attached to a smooth mask path.
// Use two base keys; do not add a second elastic ease on this same property.
var amp=.1, freq=2, decay=6, duration=1, fadeDuration=.2;
var n=0;
if(numKeys>0){n=nearestKey(time).index;if(key(n).time>time)n--;}
var result=value;
if(n>0){
  var t=time-key(n).time;
  if(t>0 && t<duration){
    var v=velocityAtTime(key(n).time-thisComp.frameDuration/10);
    var envelope=1;
    if(t>duration-fadeDuration){
      var u=(t-(duration-fadeDuration))/fadeDuration;
      envelope=1-u*u*(3-2*u);
    }
    result=value+v*amp*Math.sin(2*Math.PI*freq*t)*Math.exp(-decay*t)*envelope;
  }
}
result;
