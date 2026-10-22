// Engine-neutral reference. Evaluate from timeline time, never accumulated dt.
export function springOffset(t, velocity, {
  amp=0.16, freq=2.5, decay=5.5, duration=1, fadeDuration=0.2,
  maxOffset=300
}={}) {
  if (t<=0 || t>=duration) return 0;
  const fade=Math.min(Math.max(fadeDuration,0),duration);
  let envelope=1;
  if (fade>0 && t>duration-fade) {
    const u=(t-(duration-fade))/fade;
    envelope=1-u*u*(3-2*u);
  }
  const a=Math.max(-maxOffset,Math.min(maxOffset,velocity*amp));
  return a*Math.sin(2*Math.PI*freq*t)*Math.exp(-decay*t)*envelope;
}
