export const max_result_retrieve = 120;
// map from query length to num group filter
export const max_query_len_for_lookup = 7;
export const query_len_to_num_group_map = {
  1: 1,
  2: 1,
  3: 2,
  4: 2,
  5: 3,
  6: 3,
  7: 5
};
