import time

from python_utils.sentenceEmbeddingUtils import *

from RDRPOSTagger import *
RDRPOSTagger = RDRPOSTagger()
RDRPOSTagger.englishSetup()


def runGenerateRDRTag(sentence):
    return generateRDRTags(RDRPOSTagger, sentence)


processing_batch_size = 1000000

sentence_DB_fn = sys.argv[1]
collection_name = sys.argv[2]

collection_folder = collection_name + '/'
checkAndCreateFolder(collection_folder)

sentence_DB_file = open(sentence_DB_fn, 'r')
batch_start = 0
for segment_batch in chunked(sentence_DB_file, processing_batch_size):
    start = time.time()
    # this step only takes 4.5s for 1000000 data, not a concern
    sentence_batch = list(flatten([segment.split('. ')
                              for segment in segment_batch]))
    VP_batch = list(extractPatternArrMP(sentence_batch, relation_VP_pattern,
                                        tag_operator=runGenerateRDRTag))

    print("This batch contains", len(VP_batch), "sentences")
    batch_end = batch_start + processing_batch_size - 1
    savePythonObject(VP_batch, collection_folder + collection_name +
                     "_" + str(batch_start) + "_" + str(batch_end) + ".pkl")
    batch_start += processing_batch_size

    end = time.time()
    print("This batch takes", end - start, "seconds")

sentence_DB_file.close()
