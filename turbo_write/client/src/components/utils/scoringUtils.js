// w_es * es_score + w_ct * decay_fun_ct(cited_times)
export function ESScoreDecayRefNum(
  w_es,
  es_score,
  w_ct,
  decay_fun_ct,
  cited_times
) {
  return w_es * es_score + w_ct * decay_fun_ct(cited_times);
}

// (w_es * es_score + w_ct * decay_fun_ct(cited_times)) * decay_fun_ph(percent_hit)
export function ESScoreDecayRefNumMultDecayHit(
  w_es,
  es_score,
  w_ct,
  decay_fun_ct,
  cited_times,
  decay_fun_ph,
  percent_hit
) {
  return (
    ESScoreDecayRefNum(w_es, es_score, w_ct, decay_fun_ct, cited_times) *
    decay_fun_ph(percent_hit)
  );
}
