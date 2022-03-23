import React, { Component } from "react";
import _ from "lodash";
import axios from "axios";

import {
  keysInclude,
  dictionarySum,
  updateReferencesAndIndex
} from "./utils/dictionaryUtils";

import { popImage } from "./utils/webpageUtils";

import { SERVER_ADDRESS } from "./constants/networkConstants";
import { databaseOpt } from "./constants/optionConstants";
import { hints } from "./constants/guidelineConstants";

import ImagePanel from "./right_panel/image_view_panel/imagePanel";
import SearchBar from "./right_panel/reference_panel/searchBar";
import AddFromText from "./right_panel/text_citation_panel/addFromText";
import SearchResultBox from "./right_panel/reference_panel/searchResultBox";
import TextContentsBox from "./right_panel/text_view_panel/textContentsBox";
import SymbolColumn from "./right_panel/symbol_panel/symbolColumn";
import EndNotePanel from "./right_panel/endnote_panel/endnotePanel";
import ExamplePanel from "./right_panel/example_panel/examplePanel";
import EvidencePanel from "./right_panel/evidence_panel/evidencePanel";
import GuidelinePanel from "./right_panel/guideline_panel/guidelinePanel";
import OverlayDropdown from "./right_panel/common_components/overlayDropdown";

import { searchCitation } from "./utils/citationUtils";
import saveToServer from "./utils/save_and_load/saveToServer";
import loadFromServer from "./utils/save_and_load/loadFromServer";
import UploadBox from "./image_upload_element/uploadBox";

import Textbar from "./writing_zone/textbar";
import WritingZone from "./writing_zone/writingZone";
import GuidelineBox from "./guideline_page/guidelineBox";

import PDFPreview from "./preview_and_download/pdfPreview";

import { HotKeys } from "react-hotkeys";

import "./App.css";

import page_0 from "../assets/page_0.jpeg";
import page_1 from "../assets/page_1.jpeg";
import page_2 from "../assets/page_2.jpeg";
import page_3 from "../assets/page_3.jpeg";
import page_4 from "../assets/page_4.jpeg";
import page_5 from "../assets/page_5.jpeg";
import page_6 from "../assets/page_6.jpeg";

import {
  Layout,
  Menu,
  Switch,
  Dropdown,
  Breadcrumb,
  Icon,
  Input,
  Select,
  Button,
  notification
} from "antd";
import { FILE } from "dns";
import MenuItem from "antd/lib/menu/MenuItem";

const { Header, Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;
const { TextArea } = Input;
const { Option } = Select;

class App extends React.Component {
  state = {
    vocabulary_source: databaseOpt[0],
    vocab: null,
    // the current entry of login
    paper_id_login_entry: "",
    // paper id for save and load
    paper_id: "",
    tutorial_images: [page_0, page_1, page_2, page_3, page_4, page_5, page_6],
    current_tutorial_image_id: 0,
    tutorial_finished: false,
    // states for show settings
    collapsed_left: false,
    collapsed_right: false,
    expand_right: false,
    isShowHint: "hidden",
    part: "Guideline",
    // the current step of hint that the writer is on
    current_hints: {
      Abstract: 0,
      Introduction: 0,
      Methods: 0,
      Results: 0,
      Discussion: 0,
      Acknowledgement: 0
    },
    first_time_loading_image: true,
    first_time_viewing_uploaded_image: true,
    first_time_using_example: true,
    first_time_using_evidence: true,
    first_time_rendering_writing_page: true,
    currentRefImage: "",
    currentRefText: "",
    // states for figures
    listOfFigureContents: {
      "1": {
        inputMode: true,
        description: "",
        fileList: []
      }
    },
    // states for texts
    guideline_answers: ["", "", "", "", ""],
    title: "",
    text: {
      Abstract: "",
      Introduction: "",
      Methods: "",
      Results: "",
      Discussion: "",
      Acknowledgement:
        "We would like to thank Dr. XX and Dr. XX for their helpful discussions and comments. This research is funded by XX grant. This paper is written with the help of TurboWrite professional academic paper writing tool."
    },
    // state for tracking the position of cursor
    cursor_loc: {
      line_num: 0,
      pos_in_line: 0
    },
    references: {
      count: 0,
      // the reference list is designed to be indexed
      // by number, since when the user is trying to
      // remove reference, they remove the numbers
      // BUT NEED TO BE CAUTIOUS! SINCE JS CONVERT ALL KEYS TO STRINGS!
      reference_list: {}
    },
    // index of references for checking whether already cited
    references_index: {},
    // reference abbrev -> reference look up
    references_lookup: {},
    // citation counts for counting the number of citations in each section
    citation_counts: {
      Abstract: {},
      Introduction: {},
      Methods: {},
      Results: {},
      Discussion: {},
      Acknowledgement: {}
    },
    // states for search term of reference
    ref_search_term: "",
    // states for searches of reference
    ref_search_results: [],
    // states for search term of example
    example_search_term: "",
    // states for searches of example
    example_search_results: [],
    // states for searches of evidence
    evidence_search_term: "",
    // states for searches of evidence
    evidence_search_results: [],
    // right bar states
    right_bar: "figures"
  };

  /* login page */
  /* ---------------------------------------------------------------------------------------------------------- */
  enterID = e => {
    this.setState({ paper_id_login_entry: e.target.value });
  };

  login = e => {
    // if empty, alert
    if (this.state.paper_id_login_entry == "") {
      alert("请输入论文编码，不可为空");
    } else {
      this.setState({ paper_id: this.state.paper_id_login_entry });

      loadFromServer(this.state.paper_id_login_entry, this.loadData, () => {
        alert("已从服务器导入数据");
      });
    }
  };

  renderLoginPage() {
    return (
      <Layout style={{ minHeight: "100vh" }}>
        <Content style={{ padding: "70px 70px" }}>
          <div style={{ margin: "25px 0px" }}>
            <div style={{ margin: "10px 0px" }}>
              开始新的写作: 请输入一串字符作为您的论文编码
            </div>
            <div style={{ margin: "10px 0px" }}>
              载入之前的档案: 请输入该篇论文的编码
            </div>
            <div style={{ margin: "10px 0px" }}>按回车登录</div>
          </div>
          <Input onChange={this.enterID} onPressEnter={this.login} />
        </Content>
      </Layout>
    );
  }
  /* ---------------------------------------------------------------------------------------------------------- */

  /* tutorial page */
  /* ---------------------------------------------------------------------------------------------------------- */

  // load previous tutorial screen
  prevTutorial = e => {
    var current_tutorial_image_id = this.state.current_tutorial_image_id;
    if (current_tutorial_image_id > 0) {
      current_tutorial_image_id = current_tutorial_image_id - 1;
      this.setState({ current_tutorial_image_id: current_tutorial_image_id });
    }
  };

  // load next tutorial screen
  nextTutorial = e => {
    var current_tutorial_image_id = this.state.current_tutorial_image_id;
    if (current_tutorial_image_id < this.state.tutorial_images.length - 1) {
      current_tutorial_image_id = current_tutorial_image_id + 1;
      this.setState({ current_tutorial_image_id: current_tutorial_image_id });
    } else {
      this.setState({ tutorial_finished: true });
    }
  };

  // skip tutorial
  skipTutorial = e => {
    this.setState({ tutorial_finished: true });
  };

  // return to tutorial page
  returnToTutorial = e => {
    // reset current tutorial image
    this.setState({ current_tutorial_image_id: 0 });
    this.setState({ tutorial_finished: false });
  };

  renderTutorialPage() {
    return (
      <div style={{ margin: "10px 0px" }}>
        <img
          style={{
            display: "block",
            margin: "auto auto",
            height: 500,
            width: 900
          }}
          src={this.state.tutorial_images[this.state.current_tutorial_image_id]}
        />
        <div align="center">
          <Button
            style={{ margin: "0px 100px" }}
            title="上一张"
            icon="caret-left"
            onClick={this.prevTutorial}
          />
          <Button title="跳过教程" onClick={this.skipTutorial}>
            跳过教程
          </Button>
          <Button
            style={{ margin: "0px 100px" }}
            title="下一张"
            icon="caret-right"
            onClick={this.nextTutorial}
          />
        </div>
      </div>
    );
  }
  /* ---------------------------------------------------------------------------------------------------------- */

  /* main page */
  /* ---------------------------------------------------------------------------------------------------------- */
  // small sub components
  renderSearchDropDown() {
    const submenu_components = [
      ["搜索例句", this.rightExampleMode],
      ["搜索论据", this.rightEvidenceMode]
    ];

    return (
      <OverlayDropdown
        submenu_components={submenu_components}
        icon_name="file-search"
      />
    );
  }

  renderReferenceDropDown() {
    const submenu_components = [
      ["从搜索引擎导入引用", this.rightSearchMode],
      ["从EndNote合集文件批量导入引用", this.rightEndNoteMode],
      ["从bibTex, ris, enw文件添加单个引用", this.rightFromTextMode]
    ];

    return (
      <OverlayDropdown
        submenu_components={submenu_components}
        icon_name="pushpin"
      />
    );
  }

  renderOverviewDropDown() {
    const submenu_components = [
      ["回顾思路", this.rightGuidelineMode],
      ["回顾上传图片", this.rightFigureMode],
      ["回顾全文内容", this.rightContentMode],
      ["使用ESODA查询英语表达", this.openEsoda]
    ];

    return (
      <OverlayDropdown
        submenu_components={submenu_components}
        icon_name="compass"
      />
    );
  }

  // render the middle section based on the section name
  renderMiddleSection() {
    if (this.state.part == "Guideline") {
      return (
        <div>
          <Button style={{ margin: "5px 0px" }} onClick={this.returnToTutorial}>
            回到教程页面
          </Button>
          <GuidelineBox
            answers={this.state.guideline_answers}
            setAnswers={this.setAnswers}
          />
        </div>
      );
    } else if (this.state.part == "图片") {
      // suffix for input box
      const suffix = this.state.title ? (
        <Icon type="close-circle" onClick={this.emitEmpty} />
      ) : (
        <span />
      );

      return (
        <div>
          <Select
            placeholder="选择学科专用输入法"
            style={{ width: 200, margin: "15px 0px" }}
            onChange={this.handleVocabSourceSelect}
          >
            {databaseOpt.map(DB => (
              <Option key={DB}>{DB}</Option>
            ))}
          </Select>
          <Button style={{ margin: "0px 5px" }} onClick={this.loadVocab}>
            加载输入法
          </Button>
          <Textbar text="Title" />
          <Input
            value={this.state.title}
            suffix={suffix}
            onChange={this.enterTitle}
            ref={node => (this.titleInput = node)}
          />
          <UploadBox
            listOfFigureContents={this.state.listOfFigureContents}
            addFigure={this.addFigure}
            changeFigure={this.changeFigure}
            changeDescription={this.changeDescription}
            changeToShowMode={this.changeToShowMode}
          />
        </div>
      );
    } else if (this.state.part == "回顾并下载全文") {
      return (
        <div>
          <Textbar text={this.state.part} />
          <PDFPreview
            title={this.state.title}
            text={this.state.text}
            referencesLookup={this.state.references_lookup}
            listOfFigureContents={this.state.listOfFigureContents}
          />
        </div>
      );
    } else {
      return (
        <WritingZone
          text={this.state.text}
          part={this.state.part}
          isShowHint={this.state.isShowHint}
          vocabularies={this.state.vocab}
          currentRefImage={this.state.currentRefImage}
          currentRefText={this.state.currentRefText}
          current_hints={this.state.current_hints}
          setText={this.setText}
          setCursorLoc={this.setCursorLoc}
          popImage={popImage}
          hints={hints}
          hintAddOne={this.hintAddOne}
          hintSubOne={this.hintSubOne}
          suggestTemplate={this.suggestTemplate}
        />
      );
    }
  }

  /* saving and loading data */
  /* ---------------------------------------------------------------------------------------------------------- */
  // update data by loading from server response
  loadData = (
    guideline_answers,
    title,
    text,
    listOfFigureContents,
    references,
    references_index,
    references_lookup,
    citation_counts
  ) => {
    this.setState({
      guideline_answers: guideline_answers,
      title: title,
      text: text,
      listOfFigureContents: listOfFigureContents,
      references: references,
      references_index: references_index,
      references_lookup: references_lookup,
      citation_counts: citation_counts
    });
  };

  onClickSave = e => {
    saveToServer(
      this.state.paper_id,
      this.state.guideline_answers,
      this.state.title,
      this.state.text,
      this.state.listOfFigureContents,
      this.state.references,
      this.state.references_index,
      this.state.references_lookup,
      this.state.citation_counts,
      alert("数据已保存至服务器")
    );
  };

  onClickLoad = e => {
    loadFromServer(this.state.paper_id, this.loadData, () => {
      alert("已从服务器导入数据");
    });
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // bar collapsing and section switching
  /* ---------------------------------------------------------------------------------------------------------- */
  onCollapse_left = collapsed => {
    this.setState({ collapsed_left: collapsed });
  };

  onCollapse_right = collapsed => {
    this.setState({ collapsed_right: collapsed });
  };

  // e is the menu item get clicked
  switchSection = e => {
    this.setState({ part: e.key });
    if (e.key == "图片" || e.key == "回顾并下载全文" || e.key == "Guideline") {
      this.setState({ isShowHint: "hidden" });
    } else {
      // if first time loading writing page
      // alert for full view
      if (this.state.first_time_rendering_writing_page) {
        notification["info"]({
          message: "大纲使用提示",
          description:
            "写作中，您可以点击'写作提示'下方的'查看本小结大纲'来获得该部分大纲总结。",
          duration: 3
        });
        this.setState({ first_time_rendering_writing_page: false });
      }
      this.setState({ isShowHint: "visible" });
    }
  };

  // function for guideline answers
  /* ---------------------------------------------------------------------------------------------------------- */
  setAnswers = (i, answer_text) => {
    const guideline_answers = this.state.guideline_answers;
    guideline_answers[i] = answer_text;
    this.setState({ guideline_answers: guideline_answers });
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // title handling
  /* ---------------------------------------------------------------------------------------------------------- */
  emitEmpty = () => {
    this.titleInput.focus();
    this.setState({ title: "" });
  };

  enterTitle = e => {
    this.setState({ title: e.target.value });
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // vocabulary functions
  /* ---------------------------------------------------------------------------------------------------------- */
  handleVocabSourceSelect = value => {
    this.setState({
      vocabulary_source: value
    });
  };

  loadVocab = e => {
    axios
      .get(`${SERVER_ADDRESS}/api/loadDocGrams`, {
        params: {
          subject: this.state.vocabulary_source
        }
      })
      .then(res => {
        const vocab_data = res.data;
        const vocab = [
          vocab_data.unigram_freq,
          vocab_data.bigram_freq,
          vocab_data.trigram_freq,
          vocab_data.bigram_dict,
          vocab_data.trigram_dict,
          vocab_data.interpolation_model
        ];

        console.log(vocab);

        this.setState({ vocab: vocab });

        // reminder for vocab usage
        alert("输入法加载完毕，在正文写作部分将显示输入自动补全提示");
        alert("使用输入法中，按tab进行翻页");
      });
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // function for figures
  /* ---------------------------------------------------------------------------------------------------------- */
  // method to modify the figure based on id
  changeFigure = (id, fig) => {
    const listOfFigureContents = this.state.listOfFigureContents;
    listOfFigureContents[id].fileList = fig;
    this.setState({ listOfFigureContents: listOfFigureContents });

    // reminder for reviewing image
    if (this.state.first_time_loading_image) {
      alert("图片上传后，您可以在右侧的回顾按钮->回顾上传图片中查看已上传图片");
      this.setState({ first_time_loading_image: false });
    }
  };

  // method to modify the description of figure based on id
  changeDescription = (id, description) => {
    const listOfFigureContents = this.state.listOfFigureContents;
    listOfFigureContents[id].description = description;
    this.setState({ listOfFigureContents: listOfFigureContents });
  };

  // change an image to show mode
  changeToShowMode = id => {
    const listOfFigureContents = this.state.listOfFigureContents;
    listOfFigureContents[id].inputMode = false;
    this.setState({ listOfFigureContents: listOfFigureContents });
  };

  addFigure = () => {
    const listOfFigureContents = this.state.listOfFigureContents;
    const num_ele = Object.keys(listOfFigureContents).length;
    // get id for the new figure
    const id = (num_ele + 1).toString();
    // add new empty figure
    listOfFigureContents[id] = {
      inputMode: true,
      description: "",
      fileList: []
    };
    // cannot push figure to the list directly, need
    // to call setState to start rerender
    this.setState({ listOfFigureContents: listOfFigureContents });
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // right bar switching
  /* ---------------------------------------------------------------------------------------------------------- */
  // set right bar to figure mode
  rightExpand = checked => {
    this.setState({ expand_right: !checked });
  };

  rightFigureMode = e => {
    this.setState({ right_bar: "figures" });
    // reminder for image usage
    if (this.state.first_time_viewing_uploaded_image) {
      alert(
        "在写作中点击图片可以将图片显示在中央方便边读边写，再次点击右侧图片隐藏"
      );
      this.setState({ first_time_viewing_uploaded_image: false });
    }
  };

  // set right bar to search mode
  rightSearchMode = e => {
    this.setState({ right_bar: "search" });
  };

  // set right bar to from_text mode
  rightFromTextMode = e => {
    this.setState({ right_bar: "from_text" });
  };

  // set right bar to content mode
  rightContentMode = e => {
    this.setState({ right_bar: "contents" });
  };

  // set right bar to symbol mode
  rightSymbolMode = e => {
    this.setState({ right_bar: "symbols" });
  };

  // set right bar to guideline mode
  rightGuidelineMode = e => {
    this.setState({ right_bar: "guideline" });
  };

  // set right bar to EndNote mode
  rightEndNoteMode = e => {
    this.setState({ right_bar: "endnote" });
  };

  // set right bar to example sentence search mode
  rightExampleMode = e => {
    this.setState({ right_bar: "example" });
    // reminder for 1 click search
    if (this.state.first_time_using_example) {
      alert("搜索后可使用一键搜文按钮查找到论文原文");
      alert(
        "点击展开上下文后，再次点击可以将原文呈现到写作框上方用于参考，再次点此收起"
      );
      this.setState({ first_time_using_example: false });
    }
  };

  // set right bar to example sentence search mode
  rightEvidenceMode = e => {
    this.setState({ right_bar: "evidence" });
    // reminder for 1 click search
    if (this.state.first_time_using_evidence) {
      alert("搜索后可使用一键搜文按钮查找到论文原文");
      this.setState({ first_time_using_evidence: false });
    }
  };

  openEsoda = e => {
    window.open("http://www.esoda.org/", "popup", "width=800,height=800");
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // functions for hints, answers and writing
  /* ---------------------------------------------------------------------------------------------------------- */
  // add 1 to the hint number
  hintAddOne = part => {
    const current_hints = this.state.current_hints;

    if (current_hints[part] + 1 < hints[part].length) {
      current_hints[part] += 1;
    }
    this.setState({ current_hints: current_hints });
  };

  // substract 1 to the hint number
  hintSubOne = part => {
    const current_hints = this.state.current_hints;

    if (current_hints[part] > 0) {
      current_hints[part] -= 1;
    }
    this.setState({ current_hints: current_hints });
  };

  suggestTemplate = (part, template) => {
    const text = this.state.text;
    text[part] = text[part] + " " + template;
    this.setState({ text: text });
  };

  assignImage = key => {
    if (this.state.currentRefImage == "") {
      // first click to set the current image to the clicked image on the image panel
      this.setState({
        currentRefImage: this.state.listOfFigureContents[key].fileList[0]
          .thumbUrl
      });
    } else {
      // second click to hide it
      this.setState({
        currentRefImage: ""
      });
    }
  };

  assignText = text => {
    if (this.state.currentRefText == "") {
      // first click to set the current image to the clicked image on the image panel
      this.setState({
        currentRefText: text
      });
    } else {
      // second click to hide it
      this.setState({
        currentRefText: ""
      });
    }
  };

  // orginal method for text_area
  //setText = (key, e) => {
  setText = (key, text_value) => {
    var references = this.state.references;
    var references_index = this.state.references_index;
    const references_lookup = this.state.references_lookup;

    // orginal method for text_area
    //const section_text = e.target.value;
    const section_text = text_value;

    // [0-9]{1,3} matches 1-3 digit numbers
    // \s* zero or more spaces
    //var citations = section_text.match(/\[\s*&[0-9]{1,3}&\s*\]/g);
    // also replace spaces longer than 2
    var citations = section_text
      .replace(/\s\s+/g, " ")
      .match(/\[\s*&\s*(.*?)\s*&\s*\]/g);

    var page_citation_counts = {};
    // if any citation found, do the following
    // else keep page_citation_counts as empty
    if (citations != null) {
      citations = citations.map(c => {
        // remove [ and ], remove space
        const clean_c = c
          .replace(/\[\s*&\s*/g, "")
          .replace(/\s*&\s*\]/g, "")
          .trim();

        // look up full reference
        const full_c = references_lookup[clean_c];

        // and convert to index
        return references_index[full_c].index;
      });
      page_citation_counts = _.countBy(citations);
    }

    const citation_counts = this.state.citation_counts;
    citation_counts[key] = page_citation_counts;

    // set the text to the entries
    const text = this.state.text;
    text[key] = section_text;

    this.setState({
      text: text,
      citation_counts: citation_counts
    });

    // calculate the total sum of citations
    const citation_indeces = Object.keys(this.state.references.reference_list);
    const citation_count_sum = dictionarySum(
      citation_indeces,
      this.state.citation_counts
    );

    // update the counts in references and the index dictonary
    [references, references_index] = updateReferencesAndIndex(
      references,
      references_index,
      citation_count_sum
    );

    this.setState({
      references: references,
      references_index: references_index
    });

    // reference deleting mechanism is removed to fix
    // the citation copy and pasting bug
    // since at the end of the day the citations
    // are resorted by order of appearance, thus
    // should not affect the citation function
    /*
    Object.keys(citation_count_sum).forEach(index => {
      // if an index has count 0
      if (citation_count_sum[index] == 0) {
        // remove this reference
        this.deleteReference(index);
      }
    });
    */

    /*
    console.log("references", this.state.references);
    console.log("references_index", this.state.references_index);
    console.log("references_lookup", this.state.references_lookup);
    console.log("citation_counts", this.state.citation_counts);
    console.log("citation_count_sum", citation_count_sum);
    */
  };

  // method for saving the current cursor location
  setCursorLoc = (line_num, pos_in_line) => {
    this.setState({
      cursor_loc: {
        line_num: line_num,
        pos_in_line: pos_in_line
      }
    });
  };

  // method for insert content at specific location
  insertContentAtLoc = (section, content_to_insert) => {
    // set the text to the entries
    var text = this.state.text;
    const cur_section_text = text[section];

    // get cursor location
    const line_num = this.state.cursor_loc.line_num;
    const pos_in_line = this.state.cursor_loc.pos_in_line;

    // divide into lines
    var lines = cur_section_text.split("\n");

    // replace the line with new line that have content inserted
    const cur_line = lines[line_num];
    const first_half = cur_line.slice(0, pos_in_line);
    const second_half = cur_line.slice(pos_in_line);
    const new_line = first_half + content_to_insert + second_half;
    lines[line_num] = new_line;

    // join and put back into text
    const new_section_text = lines.join("\n");
    text[section] = new_section_text;

    this.setState({ text: text });
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  // searches (references and examples)
  /* ---------------------------------------------------------------------------------------------------------- */
  setRefSearchTerm = e => {
    this.setState({ ref_search_term: e.target.value });
  };

  setRefSearchTermWithInput = value => {
    this.setState({ ref_search_term: value });
  };

  setRefSearchResults = results => {
    this.setState({ ref_search_results: results });
  };

  setExampleSearchTerm = e => {
    this.setState({ example_search_term: e.target.value });
  };

  setExampleSearchResults = results => {
    this.setState({ example_search_results: results });
  };

  onCitationSearchSubmit = async () => {
    const paper_info = await searchCitation(this.state.ref_search_term);
    this.setRefSearchResults(paper_info);
  };

  setEvidenceSearchTerm = e => {
    this.setState({ evidence_search_term: e.target.value });
  };

  setEvidenceSearchResults = results => {
    this.setState({ evidence_search_results: results });
  };

  // add a reference
  addReference = citation_info => {
    const references = this.state.references;
    const references_index = this.state.references_index;
    const references_lookup = this.state.references_lookup;

    // get the citation
    const citation_text = citation_info.citation;
    const short_citation_text = citation_info.citation_short;

    // if currently working on one of the text parts
    // add the reference
    if (keysInclude(this.state.text, this.state.part)) {
      // if haven't cited previously
      // create new citation
      if (!keysInclude(references_index, citation_text)) {
        // add to the count of references
        references.count = references.count + 1;

        // add to the reference list
        references.reference_list[references.count] = {
          citation: citation_text,
          citation_info: citation_info
        };

        // initialize citation indexing
        references_index[citation_text] = {
          index: references.count,
          // initiate to 0 count, since there is add 1 below
          num: 0
        };

        // add to reference lookup
        references_lookup[short_citation_text] = citation_text;
      }

      // add citation to text
      // increase count
      references_index[citation_text].num =
        references_index[citation_text].num + 1;

      // get index
      const index = references_index[citation_text].index;

      // set num in reference list
      references.reference_list[index].num =
        references_index[citation_text].num;

      // add citation to the text
      const text_to_insert = "[&" + short_citation_text + "&]";
      this.insertContentAtLoc(this.state.part, text_to_insert);

      // update the count number of this citation index
      const citation_counts = this.state.citation_counts;
      // check for undefined, if undefined (not found in page) initiate as 1
      // else add 1
      citation_counts[this.state.part][index] =
        citation_counts[this.state.part][index] == undefined
          ? 1
          : citation_counts[this.state.part][index] + 1;

      // update text, reference and index
      this.setState({
        references: references,
        references_index: references_index,
        references_lookup: references_lookup,
        citation_counts: citation_counts
      });
    }
  };

  // delete a reference
  // use after the count reach 0
  deleteReference = index => {
    // this index is a string not a number! Since it comes from Object.keys()!
    // convert to number
    const number_index = Number(index);

    const references = this.state.references;
    const references_index = this.state.references_index;
    const references_lookup = this.state.references_lookup;
    const citation_counts = this.state.citation_counts;

    // if index out of bound
    if (number_index > references.count) {
      return;
    }

    // get the info of citation to delete
    const del_citation_info = references.reference_list[index];
    const del_citation_text = del_citation_info.citation;
    const del_short_citation_text =
      del_citation_info.citation_info.citation_short;

    // delete from three dictionaries
    delete references.reference_list[index];
    delete references_index[del_citation_text];
    delete references_lookup[del_short_citation_text];
    delete citation_counts[index];

    // change the index of the citations whose indeces are greater
    // use <= since this index starts from 1
    for (var i = number_index + 1; i <= references.count; i++) {
      const change_citation_info = references.reference_list[i];
      const change_citation_text = change_citation_info.citation;

      // change the reference
      // shift the index backward by delete and then insert with new id
      delete references.reference_list[i];
      references.reference_list[i - 1] = change_citation_info;

      // change indexing
      references_index[change_citation_text].index =
        references_index[change_citation_text].index - 1;

      // change count
      Object.keys(citation_counts).forEach(part => {
        // check whether the part has citation i originally
        if (keysInclude(citation_counts[part], i)) {
          // change the reference
          // shift the index backward by delete and then insert with new id
          const count_i = citation_counts[part][i];
          delete citation_counts[part][i];
          citation_counts[part][i - 1] = count_i;
        }
      });
    }

    // decrease count at the end, since still need count in prev step
    if (references.count > 0) {
      references.count = references.count - 1;
    }

    // update text and index
    this.setState({
      references: references,
      references_index: references_index,
      references_lookup: references_lookup,
      citation_counts: citation_counts
    });
  };

  // method for adding examples to text
  addExample = example_text => {
    // add example to the text
    this.insertContentAtLoc(this.state.part, example_text);
  };
  /* ---------------------------------------------------------------------------------------------------------- */

  renderRightBar(resultFontSize) {
    if (this.state.right_bar == "search") {
      return (
        // contains a search bar and a list of potential search results
        <div className="reference-region" style={{ margin: "10px 0px" }}>
          <SearchBar
            search_term={this.state.ref_search_term}
            setSearchTerm={this.setRefSearchTerm}
            onCitationSearchSubmit={this.onCitationSearchSubmit}
          />
          <SearchResultBox
            search_result_list={this.state.ref_search_results}
            addReference={this.addReference}
            resultFontSize={resultFontSize}
          />
        </div>
      );
    } else if (this.state.right_bar == "from_text") {
      return (
        <div className="add-text-region" style={{ margin: "10px 0px" }}>
          <AddFromText
            part={this.state.part}
            addReference={this.addReference}
          />
        </div>
      );
    } else if (this.state.right_bar == "figures") {
      return (
        <ImagePanel
          listOfFigureContents={this.state.listOfFigureContents}
          imageClick={this.assignImage}
          resultFontSize={resultFontSize}
        />
      );
    } else if (this.state.right_bar == "contents") {
      return (
        <TextContentsBox
          text={this.state.text}
          resultFontSize={resultFontSize}
        />
      );
    } else if (this.state.right_bar == "symbols") {
      return <SymbolColumn />;
    } else if (this.state.right_bar == "guideline") {
      return <GuidelinePanel answers={this.state.guideline_answers} />;
    } else if (this.state.right_bar == "endnote") {
      return (
        <div className="endnote-region" style={{ margin: "10px 0px" }}>
          <EndNotePanel setSearchResults={this.setRefSearchResults} />
          <SearchResultBox
            search_result_list={this.state.ref_search_results}
            addReference={this.addReference}
            resultFontSize={resultFontSize}
          />
        </div>
      );
    } else if (this.state.right_bar == "example") {
      return (
        <ExamplePanel
          search_term={this.state.example_search_term}
          search_results={this.state.example_search_results}
          setSearchTerm={this.setExampleSearchTerm}
          setSearchResults={this.setExampleSearchResults}
          setReferenceSearchTerm={this.setRefSearchTermWithInput}
          switchToRefSearch={this.rightSearchMode}
          part={this.state.part}
          addExample={this.addExample}
          onCitationSearchSubmit={this.onCitationSearchSubmit}
          textClick={this.assignText}
          resultFontSize={resultFontSize}
        />
      );
    } else if (this.state.right_bar == "evidence") {
      return (
        <EvidencePanel
          search_term={this.state.evidence_search_term}
          search_results={this.state.evidence_search_results}
          setSearchTerm={this.setEvidenceSearchTerm}
          setSearchResults={this.setEvidenceSearchResults}
          setReferenceSearchTerm={this.setRefSearchTermWithInput}
          onCitationSearchSubmit={this.onCitationSearchSubmit}
          switchToRefSearch={this.rightSearchMode}
          resultFontSize={resultFontSize}
        />
      );
    }
  }

  renderWritingPage() {
    // elements for hotkey
    const keyMap = {
      ctrl_S: "ctrl+shift+s"
    };

    const handlers = {
      ctrl_S: e => this.onClickSave(e)
    };

    var rightSiderSize = "310";
    var resultFontSize = 8;

    // when expand sider, increase sider and font size
    if (this.state.expand_right) {
      rightSiderSize = "1300";
      resultFontSize = 13;
    }

    return (
      <HotKeys keyMap={keyMap} handlers={handlers}>
        <Layout style={{ minHeight: "100vh" }}>
          <Sider
            collapsible
            collapsed={this.state.collapsed_left}
            onCollapse={this.onCollapse_left}
          >
            <Menu
              theme="dark"
              defaultSelectedKeys={["1"]}
              mode="inline"
              onClick={this.switchSection}
            >
              <Menu.Item key="Guideline">
                <Icon type="question-circle" />
                <span>Guideline</span>
              </Menu.Item>
              <Menu.Item key="图片">
                <Icon type="pie-chart" />
                <span>图片</span>
              </Menu.Item>
              <Menu.Item key="Abstract">
                <Icon type="pic-center" />
                <span>Abstract</span>
              </Menu.Item>
              <Menu.Item key="Introduction">
                <Icon type="book" />
                <span>Introduction</span>
              </Menu.Item>
              <Menu.Item key="Methods">
                <Icon type="experiment" />
                <span>Methods</span>
              </Menu.Item>
              <Menu.Item key="Results">
                <Icon type="laptop" />
                <span>Results</span>
              </Menu.Item>
              <Menu.Item key="Discussion">
                <Icon type="bulb" />
                <span>Discussion</span>
              </Menu.Item>
              <Menu.Item key="Acknowledgement">
                <Icon type="usergroup-add" />
                <span>Acknowledgement</span>
              </Menu.Item>
              <Menu.Item key="回顾并下载全文">
                <Icon type="file" />
                <span>回顾并下载全文</span>
              </Menu.Item>
            </Menu>
          </Sider>
          <Content className="content-region">
            <Button
              title="保存数据"
              type="primary"
              shape="circle"
              icon="save"
              size="large"
              style={{ margin: "5px 0px" }}
              onClick={this.onClickSave}
            />
            <Button
              title="加载数据"
              type="primary"
              shape="circle"
              icon="download"
              size="large"
              style={{ margin: "5px 25px" }}
              onClick={this.onClickLoad}
            />
            {this.renderMiddleSection()}
          </Content>
          <Sider
            className="search_result-col"
            collapsible
            collapsed={this.state.collapsed_right}
            onCollapse={this.onCollapse_right}
            reverseArrow
            width={rightSiderSize}
          >
            <div style={{ margin: "15px 10px" }}>
              <Switch
                checkedChildren="展开菜单"
                unCheckedChildren="收缩菜单"
                defaultChecked
                onChange={this.rightExpand}
              />
            </div>
            {this.renderSearchDropDown()}
            {this.renderReferenceDropDown()}
            {this.renderOverviewDropDown()}
            <Button
              title="特殊符号"
              style={{ margin: "0px 20px" }}
              shape="circle"
              icon="strikethrough"
              onClick={this.rightSymbolMode}
            />
            {this.renderRightBar(resultFontSize)}
          </Sider>
        </Layout>
      </HotKeys>
    );
  }
  /* ---------------------------------------------------------------------------------------------------------- */

  render() {
    // if haven't login
    if (this.state.paper_id == "") {
      return <div>{this.renderLoginPage()}</div>;
    } else if (this.state.tutorial_finished) {
      return <div>{this.renderWritingPage()}</div>;
    } else {
      return <div>{this.renderTutorialPage()}</div>;
    }
  }
}

export default App;
