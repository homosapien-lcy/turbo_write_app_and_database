mkdir fastText-0.9.2/result
mkdir fastText-0.9.2/result/fasttext_model_dim_150_min_df_100
fasttext skipgram -input ../title_abstract_processor/pubmed_title_abstract_fasttext -output fastText-0.9.2/result/fasttext_model_dim_150_min_df_100/pubmed_title_abstract_fasttext_model -minCount 100 -dim 150 -thread 8