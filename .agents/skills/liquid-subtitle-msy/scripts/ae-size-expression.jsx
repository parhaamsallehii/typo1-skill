// Rectangle Path > Size. Key pairs: anticipation start, arrival at caption cut.
// Use linear base keys; set each anticipation key to evaluated incoming width.
// Bounce only from each arrival key (2,4,6...), never anticipation keys.
var amp=.1, freq=2, decay=6;
var n=0;
if(numKeys>0){n=nearestKey(time).index;if(key(n).time>time)n--;}
var result=value;
if(n>0 && n%2===0){
  var t=time-key(n).time;
  if(t>0 && t<1){
    var v=velocityAtTime(key(n).time-thisComp.frameDuration/10);
    result=[value[0]+v[0]*amp*Math.sin(freq*t*2*Math.PI)/Math.exp(decay*t),value[1]];
  }
}
result;
