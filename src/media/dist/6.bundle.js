(window.webpackJsonp=window.webpackJsonp||[]).push([[6],{283:function(e,n,t){"use strict";t.d(n,"g",(function(){return o})),t.d(n,"a",(function(){return a})),t.d(n,"e",(function(){return i})),t.d(n,"f",(function(){return c})),t.d(n,"b",(function(){return l})),t.d(n,"d",(function(){return u})),t.d(n,"c",(function(){return d}));var r=t(285);function o(){return"/"}function a(){return"/beta_code_converter"}function i(){for(var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,t="",o=arguments.length,a=new Array(o>2?o-2:0),i=2;i<o;i++)a[i-2]=arguments[i];var c=a.filter((function(e){return e}));return a.length>0&&e?(t=c.join("/"),"".concat("/work","/").concat(e,"/").concat(t).concat(Object(r.c)(n))):"".concat("/work","/").concat(e)}function c(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",n=arguments.length>1&&void 0!==arguments[1]&&arguments[1],t=arguments.length>2&&void 0!==arguments[2]&&arguments[2],o=arguments.length>3&&void 0!==arguments[3]?arguments[3]:"";return"".concat("/search").concat(Object(r.d)(e,n,t,o))}function l(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("https://www.google.com/search").concat(Object(r.a)(e))}function u(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("http://www.perseus.tufts.edu/hopper/morph").concat(Object(r.b)(e))}function d(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("https://logeion.uchicago.edu","/").concat(e)}},284:function(e,n,t){"use strict";t.d(n,"b",(function(){return a})),t.d(n,"k",(function(){return i})),t.d(n,"j",(function(){return c})),t.d(n,"i",(function(){return l})),t.d(n,"c",(function(){return u})),t.d(n,"g",(function(){return d})),t.d(n,"f",(function(){return s})),t.d(n,"h",(function(){return f})),t.d(n,"e",(function(){return p})),t.d(n,"d",(function(){return v})),t.d(n,"a",(function(){return m}));var r={};function o(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:window.location.hostname;return e in r?r[e]:""}function a(){for(var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",n="",t=arguments.length,r=new Array(t>1?t-1:0),a=1;a<t;a++)r[a-1]=arguments[a];return r.length>0&&e?(n=r.join("/"),"".concat(o(),"/api/work/").concat(e,"/").concat(n)):"".concat(o(),"/api/work/").concat(e)}function i(e){return"".concat(o(),"/api/work_info/").concat(e)}function c(e){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:100;return"".concat(o(),"/api/work_image/").concat(e,"?width=").concat(n)}function l(e){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"epub";return"".concat(o(),"/api/download/work/").concat(e,"?format=").concat(n)}function u(e,n){return"".concat(o(),"/api/resolve_reference/?work=").concat(e,"&ref=").concat(n)}function d(e){return"".concat(o(),"/api/word_parse/").concat(e)}function s(e){return"".concat(o(),"/api/word_forms/").concat(e)}function f(){return"".concat(o(),"/api/works")}function p(){return"".concat(o(),"/api/version_info")}function v(e){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:1,t=arguments.length>2&&void 0!==arguments[2]&&arguments[2],r=arguments.length>3&&void 0!==arguments[3]&&arguments[3],a=0;t&&(a=1);var i=0;return r&&(i=1),"".concat(o(),"/api/search/").concat(encodeURIComponent(e),"?page=").concat(n,"&related_forms=").concat(a,"&ignore_diacritics=").concat(i)}function m(e){return"".concat(o(),"/api/convert_query_beta_code/?q=").concat(e)}},285:function(e,n,t){"use strict";function r(e){return 0===e.length?e:"?".concat(e)}function o(e,n){return e.length>0?"&".concat(n):n}function a(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",n=arguments.length>1&&void 0!==arguments[1]&&arguments[1],t=arguments.length>2&&void 0!==arguments[2]&&arguments[2],a=arguments.length>3&&void 0!==arguments[3]?arguments[3]:"",i="";return e&&(i+=o(i,"q=".concat(e))),a&&(i+=o(i,"page=".concat(a))),n&&(i+=o(i,"ignore_diacritics=1")),t&&(i+=o(i,"include_related=1")),r(i)}function i(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:null,n="";return e&&(n+=o(n,"parallel=".concat(e))),r(n)}function c(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",n="";return e&&(n+="l=".concat(e,"&la=greek")),r(n)}function l(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",n="";return e&&(n="q=".concat(e)),r(n)}t.d(n,"d",(function(){return a})),t.d(n,"c",(function(){return i})),t.d(n,"b",(function(){return c})),t.d(n,"a",(function(){return l}))},286:function(e,n,t){"use strict";var r=t(0),o=t.n(r),a=t(6),i=t.n(a),c=t(274),l=t(281);function u(e){var n=e.title,t=e.description,r=e.message,a=e.inverted;return o.a.createElement(c.a,{color:"red",inverted:a},o.a.createElement(l.a,{as:"h3"},n),t&&t,r&&t&&o.a.createElement("div",{style:{marginBottom:12}}),r)}u.propTypes={title:i.a.string.isRequired,description:i.a.string,message:i.a.string.isRequired,inverted:i.a.bool},u.defaultProps={description:null,inverted:!1},n.a=u},289:function(e,n,t){"use strict";var r=t(0),o=t.n(r),a=t(277),i=t(274),c=t(35),l=t(281),u=t(302),d=t(6),s=t.n(d),f={display:"inline-block",fontSize:16,textAlign:"middle"},p={cursor:"pointer",marginBottom:0},v={display:"inline-block",fontSize:12,verticalAlign:"top",paddingLeft:12,color:"white"},m={marginTop:0},g=function(e){var n=e.children,t=e.onClickBack,r=e.inverted,d=e.backTitle;return o.a.createElement(a.a,null,o.a.createElement(i.a,{compact:!0,style:p,onClick:t,inverted:r},o.a.createElement("div",{style:f},o.a.createElement(c.a,{name:"arrow left",corner:"top left",fitted:!0})),o.a.createElement("div",{style:v},o.a.createElement(l.a,{inverted:r,as:"h4"},d))),o.a.createElement(u.a,{style:{marginTop:0}}),o.a.createElement(i.a,{compact:!0,style:m,inverted:r},n))};g.propTypes={children:s.a.object.isRequired,inverted:s.a.bool,onClickBack:s.a.func,backTitle:s.a.string},g.defaultProps={inverted:!1,onClickBack:function(){},backTitle:"Back"},n.a=g},290:function(e,n,t){"use strict";t.d(n,"b",(function(){return p}));var r=t(0),o=t.n(r),a=t(274),i=t(35),c=t(282),l=t(6),u=t.n(l);t(308);function d(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);n&&(r=r.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,r)}return t}function s(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?d(Object(t),!0).forEach((function(n){f(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):d(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function f(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}var p=function(e){return[e.clientX<window.innerWidth/2,e.clientY<window.innerHeight/2]},v=function(e){var n=e.children,t=e.onClose,r=e.x,l=e.y,u=e.positionBelow,d=e.positionRight,f=e.footer,p=e.inverted,v={float:"right",cursor:"pointer",marginRight:0},m={position:"absolute",width:500,maxHeight:300,overflowY:"auto",padding:0,zIndex:103},g=s(s({},m),{top:45,left:5,width:"calc(100% - 10px)",position:"fixed"}),b=s(s({},m),{bottom:5,left:5,width:"calc(100% - 10px)",position:"fixed"}),h=function(){return window.innerWidth<1024},w={position:"sticky",bottom:0,width:"100%"},y=function(){return o.a.createElement(a.a,{className:"popupDialog",inverted:p,style:h()?u?b:g:m},o.a.createElement("div",{style:{padding:15}},o.a.createElement(i.a,{style:v,onClick:t},"✕"),n),f&&o.a.createElement(a.a,{className:"popupDialogFooter",inverted:p,basic:!0,style:w},f))},x=m.height?m.height:300;return m.top=u?l:l-x-20,m.left=d?r:r-m.width-10,h()?o.a.createElement(c.a,{open:!0},y()):y()};v.propTypes={onClose:u.a.func.isRequired,x:u.a.number.isRequired,y:u.a.number.isRequired,positionBelow:u.a.bool,positionRight:u.a.bool,children:u.a.element.isRequired,footer:u.a.element,inverted:u.a.bool},v.defaultProps={positionBelow:!0,positionRight:!0,footer:null,inverted:!1},n.a=v},292:function(e,n,t){"use strict";t.d(n,"c",(function(){return r})),t.d(n,"b",(function(){return o})),t.d(n,"a",(function(){return a})),t.d(n,"d",(function(){return i}));var r=0,o=1,a=2,i=3},302:function(e,n,t){"use strict";var r=t(2),o=t.n(r),a=t(3),i=t.n(a),c=t(0),l=t.n(c),u=t(16),d=t(76),s=t(77),f=t(5);function p(e){var n=e.children,t=e.className,r=e.clearing,a=e.content,c=e.fitted,v=e.hidden,m=e.horizontal,g=e.inverted,b=e.section,h=e.vertical,w=i()("ui",Object(u.a)(r,"clearing"),Object(u.a)(c,"fitted"),Object(u.a)(v,"hidden"),Object(u.a)(m,"horizontal"),Object(u.a)(g,"inverted"),Object(u.a)(b,"section"),Object(u.a)(h,"vertical"),"divider",t),y=Object(d.a)(p,e),x=Object(s.a)(p,e);return l.a.createElement(x,o()({},y,{className:w}),f.a.isNil(n)?a:n)}p.handledProps=["as","children","className","clearing","content","fitted","hidden","horizontal","inverted","section","vertical"],p.propTypes={},n.a=p},306:function(e,n,t){var r=t(132),o=t(307);"string"==typeof(o=o.__esModule?o.default:o)&&(o=[[e.i,o,""]]);var a={insert:"head",singleton:!1};r(o,a);e.exports=o.locals||{}},307:function(e,n,t){(n=t(133)(!1)).push([e.i,'.view_lexicon .speaker {\n  font-weight: bold;\n  display: block;\n  margin-top: 12px;\n}\n.view_lexicon .milestone {\n  color: #999999;\n}\n.view_lexicon [data-rend="italics"] {\n  font-style: italic;\n}\n.view_lexicon .milestone[data-n].milestone[data-unit]:after {\n  font-size: smaller;\n  margin: 3px;\n  content: "[" attr(data-unit) " " attr(data-n) "]";\n}\n.view_lexicon .milestone[data-unit="para"] {\n  display: block;\n  padding-top: 12px;\n}\n.view_lexicon .l {\n  display: block;\n  margin-left: 24px;\n}\n.view_lexicon .gap {\n  content: "...";\n}\n.view_lexicon .quote,\n.view_lexicon .q {\n  font-style: italic;\n}\n.view_lexicon .bibl {\n  margin-left: 3px;\n  margin-right: 3px;\n  font-weight: bold;\n}\n.view_lexicon .bibl::before {\n  content: "[";\n}\n.view_lexicon .bibl::after {\n  content: "]";\n}\n.view_lexicon .docauthor {\n  display: block;\n  padding-bottom: 16px;\n}\n.view_lexicon .label:not(.block) .label {\n  margin-left: 8px;\n  margin-right: 4px;\n}\n.view_lexicon .note-tag {\n  margin-left: 4px;\n  margin-right: 2px;\n  cursor: hand;\n  cursor: pointer;\n}\n.view_lexicon .read-more {\n  margin-top: 16px;\n  display: block;\n}\n\n.view_lexicon .lb {\n  display: block;\n}\n\n.view_lexicon .div3 {\n  padding-top: 16px;\n  display: block;\n}\n\n.view_lexicon .quote > .title {\n  font-weight: bold;\n  display: block;\n}\n\n.view_lexicon .p {\n  margin-bottom: 16px;\n  display: block;\n}\n\n.view_lexicon .lemma {\n  text-decoration: underline;\n  font-weight: bold;\n}\n\n.view_lexicon .orth {\n  font-weight: bold;\n  display: block;\n}\n\n.view_lexicon .etym {\n  display: block;\n  margin-top: 12px;\n  font-weight: bold;\n}\n\n/**\n * Style the sense entries so that they are nested accordingly\n */\n.view_lexicon .sense {\n  display: block;\n  margin-left: 15px;\n  margin-top: 8px;\n}\n\n/**\n * Set the margins\n */\n.view_lexicon .sense[data-level="2"] {\n  margin-left: 30px;\n}\n\n.view_lexicon .sense[data-level="3"] {\n  margin-left: 45px;\n}\n\n.view_lexicon .sense[data-level="4"] {\n  margin-left: 60px;\n}\n\n.view_lexicon .sense[data-level="5"] {\n  margin-left: 75px;\n}\n\n.view_lexicon .sense[data-level="6"] {\n  margin-left: 90px;\n}\n\n/**\n * Show the N indicator ("1.", "2.", etc.)\n */\n.view_lexicon .sense[data-level]:before {\n  content: "" attr(data-n) ". ";\n}\n\n.view_lexicon .sense[data-level="0"]:before {\n  content: "";\n}\n\n/* -----------------------------------------\n     Read work\n     ----------------------------------------- */\n.verse.number {\n  font-weight: bold;\n  color: black;\n  /*\n  border: white solid 1px;\n  padding: 1px 4px 1px 4px;\n  background-color: white;\n  */\n}\n\n.verse-container {\n  display: inline;\n  line-height: 25px;\n}\n\n.block {\n  display: block;\n  margin-top: 12px;\n}\n\n.no_definition_entries {\n  font-style: italic;\n}\n\n.verse .word {\n  cursor: pointer;\n  cursor: hand;\n}\n.verse .word:hover {\n  text-decoration: underline;\n}\n\n.view_lexicon .tr {\n  font-style: italic;\n  font-weight: bold;\n}\n\n@media print {\n  .view_lexicon .note-tag {\n    display: none;\n  }\n}',""]),e.exports=n},308:function(e,n,t){var r=t(132),o=t(309);"string"==typeof(o=o.__esModule?o.default:o)&&(o=[[e.i,o,""]]);var a={insert:"head",singleton:!1};r(o,a);e.exports=o.locals||{}},309:function(e,n,t){(n=t(133)(!1)).push([e.i,".ui.inverted.segment.popupDialog{background-color:#2B2B2E;border:1px solid #444;-webkit-box-shadow:0 15px 20px rgba(0,0,0,0.5);box-shadow:0 15px 20px rgba(0,0,0,0.5)}.popupDialog{z-index:100}.ui.inverted.segment.popupDialogFooter{border-top:1px solid #202023;background-color:#202023}.ui.segment.popupDialogFooter{border-top:1px solid #DDD;background-color:#F6F6F6}\n",""]),e.exports=n},326:function(e,n,t){"use strict";var r=t(0),o=t.n(r),a=t(6),i=t.n(a),c=t(539),l=t(35),u=t(538),d=t(130),s=t(284),f=t(283),p=t(285),v=t(286),m=t(537),g=(t(306),function(e){var n=e.lexiconEntries,t="";return e.inverted&&(t="inverted"),o.a.createElement(o.a.Fragment,null,0===n.length&&o.a.createElement(m.a,{warning:!0,className:t},o.a.createElement(l.a,{name:"warning"}),"No definition available from Liddel and Scott."),n&&n.map((function(e){return o.a.createElement("div",{key:e.lemma_lexical_form,className:"view_lexicon",dangerouslySetInnerHTML:{__html:e.definition}})})))});g.propTypes={lexiconEntries:i.a.arrayOf(i.a.shape),inverted:i.a.bool},g.defaultProps={lexiconEntries:null,inverted:!1};var b=g,h=t(292);function w(e,n){return function(e){if(Array.isArray(e))return e}(e)||function(e,n){var t=null==e?null:"undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(null==t)return;var r,o,a=[],i=!0,c=!1;try{for(t=t.call(e);!(i=(r=t.next()).done)&&(a.push(r.value),!n||a.length!==n);i=!0);}catch(e){c=!0,o=e}finally{try{i||null==t.return||t.return()}finally{if(c)throw o}}return a}(e,n)||function(e,n){if(!e)return;if("string"==typeof e)return y(e,n);var t=Object.prototype.toString.call(e).slice(8,-1);"Object"===t&&e.constructor&&(t=e.constructor.name);if("Map"===t||"Set"===t)return Array.from(e);if("Arguments"===t||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t))return y(e,n)}(e,n)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function y(e,n){(null==n||n>e.length)&&(n=e.length);for(var t=0,r=new Array(n);t<n;t++)r[t]=e[t];return r}var x=function(e){var n=e.word,t=e.inverted,a=e.work,i=e.searchState,m=w(Object(r.useState)(!1),2),g=m[0],y=m[1],x=w(Object(r.useState)(null),2),E=x[0],k=x[1],j=w(Object(r.useState)(null),2),O=j[0],_=j[1],S=w(Object(r.useState)(null),2),R=S[0],T=S[1];Object(r.useEffect)((function(){y(!0),fetch(Object(s.g)(n)).then((function(e){return e.json()})).then((function(e){k(e),y(!1),_(null),T(null)})).catch((function(e){_(e.toString()),y(!1)}))}),[n]);var q=h.c;return!g&&E?q=h.a:!g&&O&&(q=h.b),o.a.createElement(o.a.Fragment,null,q===h.a&&o.a.createElement("div",null,"Found"," ",E.length," ",1!==E.length&&o.a.createElement(o.a.Fragment,null,"parses for"),1===E.length&&o.a.createElement(o.a.Fragment,null,"parse for")," ",n,".",E&&E.length>0&&E[0].ignoring_diacritics&&o.a.createElement(o.a.Fragment,null," ","An exact match could not be found, so similar words with different diacritical marks are being returned."),o.a.createElement(c.a,{inverted:t,style:{marginTop:18},fluid:!0},E.map((function(e,n){return o.a.createElement(o.a.Fragment,{key:"".concat(e.form,"::").concat(e.description)},o.a.createElement(c.a.Title,{active:R===n,index:n,onClick:function(e,n){return function(e,n){var t=n.index;T(R===t?-1:t)}(0,n)}},o.a.createElement(l.a,{name:"dropdown"}),e.lemma," ","(",e.description,"):"," ",e.meaning),o.a.createElement(c.a.Content,{active:R===n},o.a.createElement(b,{lexiconEntries:e.lexicon_entries,inverted:t})))}))),o.a.createElement("div",{style:{marginTop:12}},function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:null;return a?o.a.createElement(o.a.Fragment,null,"Search for"," ",n," ","in"," ",o.a.createElement(d.a,{to:{pathname:Object(f.f)(),search:Object(p.d)("work:".concat(a," ").concat(n)),state:e}},"this work")," ","or"," ",o.a.createElement(d.a,{to:Object(f.f)(n)},"all works")):o.a.createElement(o.a.Fragment,null,"Search for"," ",o.a.createElement(d.a,{to:Object(f.f)(n)},n))}(n,a,i))),q===h.b&&o.a.createElement("div",null,o.a.createElement(v.a,{inverted:t,title:"Unable to get word information",description:"Information for the given word could not be obtained.",message:O})),q===h.c&&o.a.createElement(u.a,{inverted:t,style:{marginTop:32}},o.a.createElement(u.a.Header,null,o.a.createElement(u.a.Line,null)),o.a.createElement(u.a.Paragraph,null,o.a.createElement(u.a.Line,null))))};x.propTypes={word:i.a.string.isRequired,work:i.a.string,inverted:i.a.bool,searchState:i.a.object},x.defaultProps={inverted:!1,work:null,searchState:null};var E=x,k=t(290);function j(e){var n=e.word;return o.a.createElement("div",null,"Look up at"," ",o.a.createElement("a",{target:"_blank",rel:"noopener noreferrer",href:Object(f.d)(n)},"Perseus"),","," ",o.a.createElement("a",{target:"_blank",rel:"noopener noreferrer",href:Object(f.c)(n)},"Logeion"),", or"," ",o.a.createElement("a",{target:"_blank",rel:"noopener noreferrer",href:Object(f.b)(n)},"Google"))}j.propTypes={word:i.a.string.isRequired};var O=j,_=function(e){var n=e.word,t=e.onClose,r=e.x,a=e.y,i=e.positionBelow,c=e.positionRight,l=e.inverted,u=e.work,d=e.searchState;return o.a.createElement(k.a,{onClose:t,inverted:l,x:r,y:a,positionBelow:i,positionRight:c,footer:o.a.createElement(O,{word:n})},o.a.createElement(E,{work:u,word:n,inverted:l,searchState:d}))};_.propTypes={word:i.a.string.isRequired,onClose:i.a.func.isRequired,x:i.a.number.isRequired,y:i.a.number.isRequired,positionBelow:i.a.bool,positionRight:i.a.bool,inverted:i.a.bool,work:i.a.string,searchState:i.a.object},_.defaultProps={positionBelow:!0,positionRight:!0,inverted:!0,work:null,searchState:null};n.a=_},522:function(e,n,t){"use strict";t.r(n);var r=t(0),o=t.n(r),a=t(6),i=t.n(a),c=t(277),l=t(274),u=t(281),d=t(532),s=t(524),f=t(280),p=t(525),v=t(270),m=t(300),g=t(284),b=t(283),h=t(289),w=t(326),y=t(286),x=t(290);function E(e,n){return function(e){if(Array.isArray(e))return e}(e)||function(e,n){var t=null==e?null:"undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(null==t)return;var r,o,a=[],i=!0,c=!1;try{for(t=t.call(e);!(i=(r=t.next()).done)&&(a.push(r.value),!n||a.length!==n);i=!0);}catch(e){c=!0,o=e}finally{try{i||null==t.return||t.return()}finally{if(c)throw o}}return a}(e,n)||function(e,n){if(!e)return;if("string"==typeof e)return k(e,n);var t=Object.prototype.toString.call(e).slice(8,-1);"Object"===t&&e.constructor&&(t=e.constructor.name);if("Map"===t||"Set"===t)return Array.from(e);if("Arguments"===t||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t))return k(e,n)}(e,n)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function k(e,n){(null==n||n>e.length)&&(n=e.length);for(var t=0,r=new Array(n);t<n;t++)r[t]=e[t];return r}var j={marginTop:"20px"},O=Object(m.a)((function(e){return fetch(Object(g.a)(e))}),500),_=function(e){var n=e.inverted,t=e.history,a=E(Object(r.useState)(""),2),i=a[0],v=a[1],m=E(Object(r.useState)(""),2),g=m[0],k=m[1],_=E(Object(r.useState)(!1),2),S=_[0],R=_[1],T=E(Object(r.useState)(null),2),q=T[0],C=T[1],P=E(Object(r.useState)(null),2),B=P[0],F=P[1],A=E(Object(r.useState)(null),2),D=A[0],N=A[1],I=E(Object(r.useState)(null),2),L=I[0],z=I[1],U=E(Object(r.useState)(null),2),M=U[0],G=U[1],H=E(Object(r.useState)(null),2),Y=H[0],J=H[1],W=E(Object(r.useState)(null),2),X=W[0],$=W[1],K=function(e){if(e.target.className.includes("word")){var n=e.target.textContent,t=E(Object(x.b)(e),2),r=t[0],o=t[1];J(r),$(o),z(e.layerX),G(e.layerY),F("word"),N(n)}};Object(r.useEffect)((function(){return window.addEventListener("click",K),function(){window.removeEventListener("click",K)}}),[K]);return o.a.createElement(h.a,{inverted:n,onClickBack:function(){t.push(Object(b.e)())},backTitle:"Back to the Library"},o.a.createElement(o.a.Fragment,null,"word"===B&&o.a.createElement(w.a,{inverted:n,positionBelow:X,positionRight:Y,x:L,y:M,word:D,onClose:function(){F(null)}})),o.a.createElement(c.a,null,q&&o.a.createElement(y.a,{title:"Unable to load word information",description:"Unable to get information about the text from the server",message:q}),o.a.createElement(l.a,{inverted:n},o.a.createElement(u.a,{as:"h1"},"Greek text analysis"),o.a.createElement(d.a,null,"Enter beta-code below and it will be converted to Greek Unicode automatically with the ability to look up individual words",o.a.createElement(s.a,{placeholder:"Enter Greek text or beta-code here",value:i,onChange:function(e,n){var t;v(n.value),t=n.value,R(!0),O(t).then((function(e){return e.json()})).then((function(e){k(e),R(!1),C(null)})).catch((function(e){C(e),R(!1)}))}}),o.a.createElement("div",{style:j}),g&&o.a.createElement(o.a.Fragment,null,"Results (click the word to do a morphological lookup):",o.a.createElement(l.a,{secondary:!0,inverted:n},S&&o.a.createElement(f.a,{active:!0},o.a.createElement(p.a,null)),g.split(" ").map((function(e){return o.a.createElement(o.a.Fragment,null,o.a.createElement("span",{className:"word"},e)," ")}))))))))};_.propTypes={inverted:i.a.bool,history:i.a.object.isRequired},_.defaultProps={inverted:!1},n.default=Object(v.h)(_)}}]);
//# sourceMappingURL=6.js.map