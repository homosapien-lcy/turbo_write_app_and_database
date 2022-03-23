export const enw_key_map = {
  "%0": "type",
  "%T": "title",
  "%X": "abstract",
  "%A": "author",
  "%J": "journal",
  "%V": "volume",
  "%N": "issue",
  "%P": "page",
  "%D": "year",
  "%I": "publisher"
};

export const ris_key_map = {
  TY: "type",
  // full title, priority TI > T1
  TI: "title",
  // primary title
  T1: "title",
  AB: "abstract",
  // all author formats treat equally
  AU: "author",
  A1: "author",
  A2: "author",
  A3: "author",
  A4: "author",
  // JO > JF > J2
  JO: "journal",
  JF: "journal",
  J2: "journal",
  // JA > J1
  JA: "abbrev",
  J1: "abbrev",
  VL: "volume",
  IS: "issue",
  SP: "start_page",
  EP: "end_page",
  // Y1 > PY
  Y1: "year",
  PY: "year",
  PB: "publisher"
};

// priority of each ris term, for comparison
// if multiple term of the same field exist
export const ris_priority_map = {
  TY: 0,
  // full title, priority TI > T1
  TI: 1,
  // primary title
  T1: 0,
  AB: 0,
  // all author formats treat equally
  AU: 0,
  A1: 0,
  A2: 0,
  A3: 0,
  A4: 0,
  // JO > JF > J2
  JO: 2,
  JF: 1,
  J2: 0,
  // JA > J1
  JA: 1,
  J1: 0,
  VL: 0,
  IS: 0,
  SP: 0,
  EP: 0,
  // Y1 > PY
  Y1: 1,
  PY: 0,
  PB: 0
};
