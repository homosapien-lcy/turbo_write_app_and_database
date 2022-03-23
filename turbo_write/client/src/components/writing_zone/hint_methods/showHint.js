// this file is created by simply removing the function(mod) part of
// a hacked show-hint.js
import CodeMirror from 'codemirror/lib/codemirror';
import { flattenArr } from './hintUtils';

var HINT_ELEMENT_CLASS = 'CodeMirror-hint';
var ACTIVE_HINT_ELEMENT_CLASS = 'CodeMirror-hint-active';

const NUM_ITEMS_MARKED = 10;
const NUM_OFFSET = 9;

// This is the old interface, kept around for now to stay
// backwards-compatible.
CodeMirror.showHint = function(cm, getHints, options) {
  if (!getHints) return cm.showHint(options);
  if (options && options.async) getHints.async = true;
  var newOpts = { hint: getHints };
  if (options) for (var prop in options) newOpts[prop] = options[prop];
  return cm.showHint(newOpts);
};

CodeMirror.defineExtension('showHint', function(options, keywords) {
  options = parseOptions(this, this.getCursor('start'), options, keywords);
  var selections = this.listSelections();
  if (selections.length > 1) return;
  // By default, don't allow completion when something is selected.
  // A hint function can have a `supportsSelection` property to
  // indicate that it can handle selections.
  if (this.somethingSelected()) {
    // check whether selection is supported
    if (!options.hint.supportsSelection) return;
    // Don't try with cross-line selections
    // make sure that head and anchor are in the same line
    for (var i = 0; i < selections.length; i++) if (selections[i].head.line != selections[i].anchor.line) return;
  }

  // close the activity if it exist
  if (this.state.completionActive) this.state.completionActive.close();
  // set completion activity to a new Completion object
  var completion = (this.state.completionActive = new Completion(this, options));
  // return if no hint
  if (!completion.options.hint) return;

  // broadcast the startCompletion signal, for other handlers
  // to perform actions after "on("startCompletion")"
  CodeMirror.signal(this, 'startCompletion', this);
  completion.update(true);
});

// a new function for autocomplete after certain key press
CodeMirror.defineExtension('guessYouLike', function(options) {
  // add default option to the options, which contains closedCharacters
  // the absent of which will cause it to be null
  options = parseOptions(this, this.getCursor('start'), options);
  // construct the completion
  // this alone has already call widget.pick()
  var completion = (this.state.completionActive = new Completion(this, options));
  // check for null
  if (completion.widget) {
    // this part is actually not passed through!!!!!!
    completion.widget.pick();
  }
});

function Completion(cm, options) {
  this.cm = cm;
  this.options = options;
  this.widget = null;
  this.debounce = 0;
  this.tick = 0;
  this.startPos = this.cm.getCursor('start');
  this.startLen = this.cm.getLine(this.startPos.line).length - this.cm.getSelection().length;

  var self = this;
  cm.on(
    'cursorActivity',
    (this.activityFunc = function() {
      self.cursorActivity();
    })
  );
}

var requestAnimationFrame =
  window.requestAnimationFrame ||
  function(fn) {
    return setTimeout(fn, 1000 / 60);
  };
var cancelAnimationFrame = window.cancelAnimationFrame || clearTimeout;

Completion.prototype = {
  close: function() {
    if (!this.active()) return;
    this.cm.state.completionActive = null;
    this.tick = null;
    this.cm.off('cursorActivity', this.activityFunc);

    if (this.widget && this.data) CodeMirror.signal(this.data, 'close');
    // this will close the widget (hint drop down menu)
    if (this.widget) this.widget.close();
    CodeMirror.signal(this.cm, 'endCompletion', this.cm);
  },

  active: function() {
    return this.cm.state.completionActive == this;
  },

  pick: function(data, i) {
    if (i < data.list.length) {
      // normal pick
      var completion = data.list[i];
    } else if (data.list.length < NUM_ITEMS_MARKED) {
      // if pick longer than list and list shorter then 10,
      // pick the last one
      var completion = data.list[data.list.length - 1];
    } else {
      // cover the edge case at the end of the list
      var completion = data.list[i % data.list.length];
    }
    if (completion.hint) completion.hint(this.cm, data, completion);
    // replace text with the selected hint in the range
    else this.cm.replaceRange(getText(completion), completion.from || data.from, completion.to || data.to, 'complete');
    CodeMirror.signal(data, 'pick', completion);

    // not closing the completion keeps the completion going
    // which help users to select more bigrams and trigrams
    //this.close();
  },

  cursorActivity: function() {
    if (this.debounce) {
      cancelAnimationFrame(this.debounce);
      this.debounce = 0;
    }

    var pos = this.cm.getCursor(),
      line = this.cm.getLine(pos.line);
    if (
      pos.line != this.startPos.line ||
      line.length - pos.ch != this.startLen - this.startPos.ch ||
      pos.ch < this.startPos.ch ||
      this.cm.somethingSelected() ||
      (!pos.ch || this.options.closeCharacters.test(line.charAt(pos.ch - 1)))
    ) {
      this.close();
    } else {
      var self = this;
      this.debounce = requestAnimationFrame(function() {
        self.update();
      });
      if (this.widget) this.widget.disable();
    }
  },

  update: function(first) {
    if (this.tick == null) return;
    var self = this,
      myTick = ++this.tick;
    // this.options.hint is the function that generates hint
    // data contains a list of candidate words
    fetchHints(this.options.hint, this.options.keywords, this.cm, this.options, function(data) {
      if (self.tick == myTick) self.finishUpdate(data, first);
    });
  },

  finishUpdate: function(data, first) {
    if (this.data) CodeMirror.signal(this.data, 'update');

    var picked = (this.widget && this.widget.picked) || (first && this.options.completeSingle);
    if (this.widget) this.widget.close();

    this.data = data;

    if (data && data.list.length) {
      if (picked && data.list.length == 1) {
        //debugger;
        // this.pick command automatically
        // finish the word completion
        // which is annoying
        //this.pick(data, 0);
      } else {
        // create the widget (drop down menu)
        this.widget = new Widget(this, data);
        // give the shown signal of widget showing
        CodeMirror.signal(data, 'shown');
      }
    }
  }
};

function parseOptions(cm, pos, options, keywords) {
  var editor = cm.options.hintOptions;
  var out = {};
  for (var prop in defaultOptions) out[prop] = defaultOptions[prop];
  if (editor) for (var prop in editor) if (editor[prop] !== undefined) out[prop] = editor[prop];
  if (options) for (var prop in options) if (options[prop] !== undefined) out[prop] = options[prop];
  /*
      the original hint assignment only takes a special type of hint
      and not script hint, thus need to assign hint to options (hint)
      here
      */
  out.hint = options;
  out.keywords = keywords;

  if (out.hint.resolve) out.hint = out.hint.resolve(cm, pos);
  return out;
}

function getText(completion) {
  if (typeof completion == 'string') return completion;
  else return completion.text;
}

function buildKeyMap(completion, handle, cur_widget) {
  var baseMap = {
    Up: function() {
      handle.moveFocus(-1);
    },
    Down: function() {
      handle.moveFocus(1);
    },
    PageUp: function() {
      handle.moveFocus(-handle.menuSize() + 1, true);
    },
    PageDown: function() {
      handle.moveFocus(handle.menuSize() - 1, true);
    },
    Home: function() {
      handle.setFocus(0);
    },
    End: function() {
      handle.setFocus(handle.length - 1);
    },
    Enter: handle.pick_cur,
    // map Tab key to list shifting
    Tab: function() {
      handle.shiftList(cur_widget);
      // set the focus on the starting element
      handle.setFocus(0);
    },
    Esc: handle.close,
    // offset by the shift of the current widget
    '1': function() {
      handle.pick(0 + cur_widget.offset);
    },
    '2': function() {
      handle.pick(1 + cur_widget.offset);
    },
    '3': function() {
      handle.pick(2 + cur_widget.offset);
    },
    '4': function() {
      handle.pick(3 + cur_widget.offset);
    },
    '5': function() {
      handle.pick(4 + cur_widget.offset);
    },
    '6': function() {
      handle.pick(5 + cur_widget.offset);
    },
    '7': function() {
      handle.pick(6 + cur_widget.offset);
    },
    '8': function() {
      handle.pick(7 + cur_widget.offset);
    },
    '9': function() {
      handle.pick(8 + cur_widget.offset);
    },
    '0': function() {
      handle.pick(9 + cur_widget.offset);
    }
  };
  var custom = completion.options.customKeys;
  var ourMap = custom ? {} : baseMap;
  function addBinding(key, val) {
    var bound;
    if (typeof val != 'string')
      bound = function(cm) {
        return val(cm, handle);
      };
    // This mechanism is deprecated
    else if (baseMap.hasOwnProperty(val)) bound = baseMap[val];
    else bound = val;
    ourMap[key] = bound;
  }
  if (custom) for (var key in custom) if (custom.hasOwnProperty(key)) addBinding(key, custom[key]);
  var extra = completion.options.extraKeys;
  if (extra) for (var key in extra) if (extra.hasOwnProperty(key)) addBinding(key, extra[key]);
  return ourMap;
}

function getHintElement(hintsElement, el) {
  while (el && el != hintsElement) {
    if (el.nodeName.toUpperCase() === 'LI' && el.parentNode == hintsElement) return el;
    el = el.parentNode;
  }
}

function Widget(completion, data) {
  this.completion = completion;
  this.data = data;
  this.picked = false;
  var widget = this,
    cm = completion.cm;

  this.offset = 0;

  // function to construct the list of hint (in elements)
  function renderHint(hints, completions, widget) {
    const upper = completions.slice(0, widget.offset);
    const lower = completions.slice(widget.offset, completions.length);
    const offset_completions = flattenArr([lower, upper]);

    // reset the list elements
    hints.innerHTML = '';
    for (var i = 0; i < offset_completions.length; ++i) {
      var elt = hints.appendChild(document.createElement('li')),
        cur = offset_completions[i];
      // add the number indicator to the hints, if number <= 9
      if (i >= 0 && i <= NUM_ITEMS_MARKED - 1) {
        // case of 1 -> 9 -> 0
        cur = ((i + 1) % NUM_ITEMS_MARKED) + ' ' + cur;
      }
      var className = HINT_ELEMENT_CLASS + (i != widget.selectedHint ? '' : ' ' + ACTIVE_HINT_ELEMENT_CLASS);
      if (cur.className != null) className = cur.className + ' ' + className;
      elt.className = className;
      if (cur.render) cur.render(elt, data, cur);
      else elt.appendChild(document.createTextNode(cur.displayText || getText(cur)));
      elt.hintId = i;
    }
  }

  // ul is the html element that shows a list
  var hints = (this.hints = document.createElement('ul'));
  var theme = completion.cm.options.theme;
  hints.className = 'CodeMirror-hints ' + theme;
  this.selectedHint = data.selectedHint || 0;

  // completions contains the list of suggested words
  var completions = data.list;
  // append the list element by element to the drop down menu
  renderHint(hints, completions, this);

  var pos = cm.cursorCoords(completion.options.alignWithWord ? data.from : null);
  var left = pos.left,
    top = pos.bottom,
    below = true;
  hints.style.left = left + 'px';
  hints.style.top = top + 'px';
  // If we're at the edge of the screen, then we want the menu to appear on the left of the cursor.
  var winW = window.innerWidth || Math.max(document.body.offsetWidth, document.documentElement.offsetWidth);
  var winH = window.innerHeight || Math.max(document.body.offsetHeight, document.documentElement.offsetHeight);
  (completion.options.container || document.body).appendChild(hints);
  var box = hints.getBoundingClientRect(),
    overlapY = box.bottom - winH;
  var scrolls = hints.scrollHeight > hints.clientHeight + 1;
  var startScroll = cm.getScrollInfo();

  if (overlapY > 0) {
    var height = box.bottom - box.top,
      curTop = pos.top - (pos.bottom - box.top);
    if (curTop - height > 0) {
      // Fits above cursor
      hints.style.top = (top = pos.top - height) + 'px';
      below = false;
    } else if (height > winH) {
      hints.style.height = winH - 5 + 'px';
      hints.style.top = (top = pos.bottom - box.top) + 'px';
      var cursor = cm.getCursor();
      if (data.from.ch != cursor.ch) {
        pos = cm.cursorCoords(cursor);
        hints.style.left = (left = pos.left) + 'px';
        box = hints.getBoundingClientRect();
      }
    }
  }
  var overlapX = box.right - winW;
  if (overlapX > 0) {
    if (box.right - box.left > winW) {
      hints.style.width = winW - 5 + 'px';
      overlapX -= box.right - box.left - winW;
    }
    hints.style.left = (left = pos.left - overlapX) + 'px';
  }
  if (scrolls)
    for (var node = hints.firstChild; node; node = node.nextSibling)
      node.style.paddingRight = cm.display.nativeBarWidth + 'px';

  // here, the handles are the mapped to functions that will be
  // executed after key press
  cm.addKeyMap(
    (this.keyMap = buildKeyMap(
      completion,
      {
        moveFocus: function(n, avoidWrap) {
          widget.changeActive(widget.selectedHint + n, avoidWrap);
        },
        // set the focus on location n
        setFocus: function(n) {
          widget.changeActive(n);
        },
        menuSize: function() {
          return widget.screenAmount();
        },
        length: completions.length,
        close: function() {
          completion.close();
        },
        // function that pick at the current cursor
        pick_cur: function() {
          widget.pick();
        },
        // function that pick at the # location
        pick: function(n) {
          widget.pick(n);
        },
        // shifting the list
        shiftList: function(cur_widget) {
          // if offset will not exceeding the list
          if (cur_widget.offset + NUM_OFFSET < completions.length) {
            cur_widget.offset += NUM_OFFSET;
          }
          renderHint(hints, completions, cur_widget);
        },
        data: data
      },
      this
    ))
  );

  if (completion.options.closeOnUnfocus) {
    var closingOnBlur;
    cm.on(
      'blur',
      (this.onBlur = function() {
        closingOnBlur = setTimeout(function() {
          completion.close();
        }, 100);
      })
    );
    cm.on(
      'focus',
      (this.onFocus = function() {
        clearTimeout(closingOnBlur);
      })
    );
  }

  cm.on(
    'scroll',
    (this.onScroll = function() {
      var curScroll = cm.getScrollInfo(),
        editor = cm.getWrapperElement().getBoundingClientRect();
      var newTop = top + startScroll.top - curScroll.top;
      var point = newTop - (window.pageYOffset || (document.documentElement || document.body).scrollTop);
      if (!below) point += hints.offsetHeight;
      if (point <= editor.top || point >= editor.bottom) return completion.close();
      hints.style.top = newTop + 'px';
      hints.style.left = left + startScroll.left - curScroll.left + 'px';
    })
  );

  CodeMirror.on(hints, 'dblclick', function(e) {
    var t = getHintElement(hints, e.target || e.srcElement);
    if (t && t.hintId != null) {
      widget.changeActive(t.hintId);
      widget.pick();
    }
  });

  CodeMirror.on(hints, 'click', function(e) {
    var t = getHintElement(hints, e.target || e.srcElement);
    if (t && t.hintId != null) {
      widget.changeActive(t.hintId);
      if (completion.options.completeOnSingleClick) widget.pick();
    }
  });

  CodeMirror.on(hints, 'mousedown', function() {
    setTimeout(function() {
      cm.focus();
    }, 20);
  });

  CodeMirror.signal(data, 'select', completions[this.selectedHint], hints.childNodes[this.selectedHint]);
  return true;
}

Widget.prototype = {
  close: function() {
    if (this.completion.widget != this) return;
    this.completion.widget = null;
    this.hints.parentNode.removeChild(this.hints);
    this.completion.cm.removeKeyMap(this.keyMap);

    var cm = this.completion.cm;
    if (this.completion.options.closeOnUnfocus) {
      cm.off('blur', this.onBlur);
      cm.off('focus', this.onFocus);
    }
    cm.off('scroll', this.onScroll);
  },

  disable: function() {
    this.completion.cm.removeKeyMap(this.keyMap);
    var widget = this;
    this.keyMap = {
      Enter: function() {
        widget.picked = true;
      }
    };
    this.completion.cm.addKeyMap(this.keyMap);
  },

  // add the offset to take care of the shift by user
  pick: function(index = this.selectedHint + this.offset) {
    this.completion.pick(this.data, index);
  },

  changeActive: function(i, avoidWrap) {
    if (i >= this.data.list.length) i = avoidWrap ? this.data.list.length - 1 : 0;
    else if (i < 0) i = avoidWrap ? 0 : this.data.list.length - 1;
    if (this.selectedHint == i) return;
    var node = this.hints.childNodes[this.selectedHint];
    if (node) node.className = node.className.replace(' ' + ACTIVE_HINT_ELEMENT_CLASS, '');
    node = this.hints.childNodes[(this.selectedHint = i)];
    node.className += ' ' + ACTIVE_HINT_ELEMENT_CLASS;
    if (node.offsetTop < this.hints.scrollTop) this.hints.scrollTop = node.offsetTop - 3;
    else if (node.offsetTop + node.offsetHeight > this.hints.scrollTop + this.hints.clientHeight)
      this.hints.scrollTop = node.offsetTop + node.offsetHeight - this.hints.clientHeight + 3;
    CodeMirror.signal(this.data, 'select', this.data.list[this.selectedHint], node);
  },

  screenAmount: function() {
    return Math.floor(this.hints.clientHeight / this.hints.firstChild.offsetHeight) || 1;
  }
};

function applicableHelpers(cm, helpers) {
  if (!cm.somethingSelected()) return helpers;
  var result = [];
  for (var i = 0; i < helpers.length; i++) if (helpers[i].supportsSelection) result.push(helpers[i]);
  return result;
}

function fetchHints(hint, keywords, cm, options, callback) {
  if (hint.async) {
    hint(cm, callback, options, keywords);
  } else {
    var result = hint(cm, options, keywords);
    if (result && result.then) result.then(callback);
    else callback(result);
  }
}

function resolveAutoHints(cm, pos) {
  var helpers = cm.getHelpers(pos, 'hint'),
    words;
  if (helpers.length) {
    var resolved = function(cm, callback, options) {
      var app = applicableHelpers(cm, helpers);
      function run(i) {
        if (i == app.length) return callback(null);
        fetchHints(app[i], cm, options, function(result) {
          if (result && result.list.length > 0) callback(result);
          else run(i + 1);
        });
      }
      run(0);
    };
    resolved.async = true;
    resolved.supportsSelection = true;
    return resolved;
  } else if ((words = cm.getHelper(cm.getCursor(), 'hintWords'))) {
    return function(cm) {
      return CodeMirror.hint.fromList(cm, { words: words });
    };
  } else if (CodeMirror.hint.anyword) {
    return function(cm, options) {
      return CodeMirror.hint.anyword(cm, options);
    };
  } else {
    return function() {};
  }
}

CodeMirror.registerHelper('hint', 'auto', {
  resolve: resolveAutoHints
});

CodeMirror.registerHelper('hint', 'fromList', function(cm, options) {
  var cur = cm.getCursor(),
    token = cm.getTokenAt(cur);
  var term,
    from = CodeMirror.Pos(cur.line, token.start),
    to = cur;
  if (token.start < cur.ch && /\w/.test(token.string.charAt(cur.ch - token.start - 1))) {
    term = token.string.substr(0, cur.ch - token.start);
  } else {
    term = '';
    from = cur;
  }
  var found = [];
  for (var i = 0; i < options.words.length; i++) {
    var word = options.words[i];
    if (word.slice(0, term.length) == term) found.push(word);
  }

  if (found.length) return { list: found, from: from, to: to };
});

CodeMirror.commands.autocomplete = CodeMirror.showHint;

var defaultOptions = {
  hint: CodeMirror.hint.auto,
  completeSingle: true,
  alignWithWord: true,
  closeCharacters: /[\s()\[\]{};:>,]/,
  closeOnUnfocus: true,
  completeOnSingleClick: true,
  container: null,
  customKeys: null,
  extraKeys: null
};

CodeMirror.defineOption('hintOptions', null);
