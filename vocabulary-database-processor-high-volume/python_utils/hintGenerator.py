from .IOHelper import *
from .counterHelper import *
from shutil import copyfile

hint_path = "hint_generation_files/"
target_path = "node_modules/codemirror/addon/hint/"

hint_upper_half_fn = hint_path + "hint_upper_half"
hint_lower_half_fn = hint_path + "hint_lower_half"


def toJSCommand(word):
    return 'javascriptKeywords.push("' + word + '"); \n'


def generateHint(wordTable):
    # copy the new show hint file into the node_module
    copyfile("hint_generation_files/show-hint.js",
             target_path + "show-hint.js")

    hint_file = open(target_path + "javascript-hint.js", 'w')
    upper_content = fileAllIn(hint_upper_half_fn)
    lower_content = fileAllIn(hint_lower_half_fn)

    word_list = counterToList(wordTable)
    hint_content = ' '.join([toJSCommand(x) for x in word_list])
    hint_contents = upper_content + hint_content + lower_content

    hint_file.write(hint_contents)
    hint_file.close()
