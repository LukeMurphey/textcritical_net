(window.webpackJsonp=window.webpackJsonp||[]).push([[4],{280:function(e,t,r){"use strict";function n(){return"/"}function a(){for(var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:"",t="",r=arguments.length,n=new Array(1<r?r-1:0),a=1;a<r;a++)n[a-1]=arguments[a];var o=n.filter((function(e){return e}));return 0<n.length&&e?(t=o.join("/"),"/work/".concat(e,"/").concat(t)):"/work/".concat(e)}function o(){var e=1<arguments.length&&void 0!==arguments[1]&&arguments[1],t=2<arguments.length&&void 0!==arguments[2]&&arguments[2],r=3<arguments.length&&void 0!==arguments[3]?arguments[3]:"",n="/search?q=".concat(0<arguments.length&&void 0!==arguments[0]?arguments[0]:"");return r&&(n+="&page=".concat(r)),e&&(n+="&ignore_diacritics=1"),t&&(n+="&include_related=1"),n}function c(){return"https://www.google.com/search?q=".concat(0<arguments.length&&void 0!==arguments[0]?arguments[0]:"")}function l(){return"http://www.perseus.tufts.edu/hopper/morph?l=".concat(0<arguments.length&&void 0!==arguments[0]?arguments[0]:"","&la=greek")}function i(){return"https://logeion.uchicago.edu/".concat(0<arguments.length&&void 0!==arguments[0]?arguments[0]:"")}r.d(t,"f",(function(){return n})),r.d(t,"d",(function(){return a})),r.d(t,"e",(function(){return o})),r.d(t,"a",(function(){return c})),r.d(t,"c",(function(){return l})),r.d(t,"b",(function(){return i}))},282:function(e,t,r){"use strict";r.d(t,"a",(function(){return o})),r.d(t,"h",(function(){return c})),r.d(t,"g",(function(){return l})),r.d(t,"f",(function(){return i})),r.d(t,"b",(function(){return d})),r.d(t,"d",(function(){return u})),r.d(t,"e",(function(){return s})),r.d(t,"c",(function(){return m}));var n={};function a(e){var t=0<arguments.length&&void 0!==e?e:window.location.hostname;return t in n?n[t]:""}function o(){for(var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:"",t="",r=arguments.length,n=new Array(1<r?r-1:0),o=1;o<r;o++)n[o-1]=arguments[o];return 0<n.length&&e?(t=n.join("/"),"".concat(a(),"/api/work/").concat(e,"/").concat(t)):"".concat(a(),"/api/work/").concat(e)}function c(e){return"".concat(a(),"/api/work_info/").concat(e)}function l(e){var t=1<arguments.length&&void 0!==arguments[1]?arguments[1]:100;return"".concat(a(),"/api/work_image/").concat(e,"?width=").concat(t)}function i(e){var t=1<arguments.length&&void 0!==arguments[1]?arguments[1]:"epub";return"".concat(a(),"/api/download/work/").concat(e,"?format=").concat(t)}function d(e,t){return"".concat(a(),"/api/resolve_reference/?work=").concat(e,"&ref=").concat(t)}function u(e){return"".concat(a(),"/api/word_parse/").concat(e)}function s(){return"".concat(a(),"/api/works")}function m(e){var t=1<arguments.length&&void 0!==arguments[1]?arguments[1]:1,r=0;2<arguments.length&&void 0!==arguments[2]&&arguments[2]&&(r=1);var n=0;return 3<arguments.length&&void 0!==arguments[3]&&arguments[3]&&(n=1),"".concat(a(),"/api/search/").concat(encodeURIComponent(e),"?page=").concat(t,"&related_forms=").concat(r,"&ignore_diacritics=").concat(n)}},284:function(e,t,r){"use strict";var n=r(0),a=r.n(n),o=r(6),c=r.n(o),l=r(272),i=r(278);function d(e){var t=e.title,r=e.description,n=e.message,o=e.inverted;return a.a.createElement(l.a,{color:"red",inverted:o},a.a.createElement(i.a,{as:"h3"},t),r&&r,n&&r&&a.a.createElement("div",{style:{marginBottom:12}}),n)}d.propTypes={title:c.a.string.isRequired,description:c.a.string,message:c.a.string.isRequired,inverted:c.a.bool},d.defaultProps={description:null,inverted:!1},t.a=d},286:function(e,t,r){"use strict";function n(e){var t=e.children,r=e.onClickBack,n=e.inverted,a=e.backTitle;return o.a.createElement(c.a,null,o.a.createElement(l.a,{compact:!0,style:g,onClick:r,inverted:n},o.a.createElement("div",{style:f},o.a.createElement(i.a,{name:"arrow left",corner:"top left",fitted:!0})),o.a.createElement("div",{style:b},o.a.createElement(d.a,{inverted:n,as:"h4"},a))),o.a.createElement(u.a,{style:{marginTop:0}}),o.a.createElement(l.a,{compact:!0,style:v,inverted:n},t))}var a=r(0),o=r.n(a),c=r(275),l=r(272),i=r(35),d=r(278),u=r(315),s=r(6),m=r.n(s),f={display:"inline-block",fontSize:16,textAlign:"middle"},g={cursor:"pointer",marginBottom:0},b={display:"inline-block",fontSize:12,verticalAlign:"top",paddingLeft:12,color:"white"},v={marginTop:0};n.propTypes={children:m.a.object.isRequired,inverted:m.a.bool,onClickBack:m.a.func,backTitle:m.a.string},n.defaultProps={inverted:!1,onClickBack:function(){},backTitle:"Back"},t.a=n},356:function(e,t,r){var n=r(132),a=r(357);"string"==typeof(a=a.__esModule?a.default:a)&&(a=[[e.i,a,""]]);var o=(n(a,{insert:"head",singleton:!1}),a.locals?a.locals:{});e.exports=o},357:function(e,t,r){(t=r(133)(!1)).push([e.i,"b.match{font-weight:bold}.term0{background-color:#c9ddfa}.term1{background-color:#e6d8fa}.term2{background-color:#cee4fa}.term3{background-color:#ede3ec}.term4{background-color:#f8e9db}.term5{background-color:#e4ddfa}.term6{background-color:#e5d0fa}.term7{background-color:#e2e1f9}.term8{background-color:#d4cbfa}.term9{background-color:#cbdffa}.term10{background-color:#d8c9fa}.term11{background-color:#e1eaf1}.term12{background-color:#cbd5fa}.term13{background-color:#eff4d9}.term14{background-color:#f0cbfa}.term15{background-color:#cee1fa}.term16{background-color:#f9d8eb}.term17{background-color:#e3f1e8}.term18{background-color:#e5d4fa}.term19{background-color:#e3ccfa}.term20{background-color:#daf1f1}.term21{background-color:#eacffa}.term22{background-color:#faf2d0}.term23{background-color:#f5f4d3}.term24{background-color:#f5ecdb}.term25{background-color:#f5dfe8}.term26{background-color:#dcdffa}.term27{background-color:#e6dcfa}.term28{background-color:#e3dffa}.term29{background-color:#cdedfa}.term30{background-color:#f8ecd8}.term31{background-color:#e5e0f7}.term32{background-color:#ccd8fa}.term33{background-color:#e2e7f3}.term34{background-color:#f6ecda}.term35{background-color:#e8e4f0}.term36{background-color:#d7d0fa}.term37{background-color:#d1edfa}.term38{background-color:#ebfad7}.term39{background-color:#ccf5fa}.term40{background-color:#d7d6fa}.term41{background-color:#ecebe5}.term42{background-color:#dfe7f6}.term43{background-color:#f4dfe9}.term44{background-color:#e7d5fa}.term45{background-color:#cadafa}.term46{background-color:#eed2fa}.term47{background-color:#d2cdfa}.term48{background-color:#d0ebfa}.term49{background-color:#efcefa}.term50{background-color:#d3e6fa}.inverted>.term0{background-color:#543496}.inverted>.term1{background-color:#5f8273}.inverted>.term2{background-color:#91467d}.inverted>.term3{background-color:#344696}.inverted>.term4{background-color:#8a8e3c}.inverted>.term5{background-color:#7f6f66}.inverted>.term6{background-color:#6d6f78}.inverted>.term7{background-color:#328396}.inverted>.term8{background-color:#5f8273}.inverted>.term9{background-color:#8a3c8e}.inverted>.term10{background-color:#505696}.inverted>.term11{background-color:#2a4e96}.inverted>.term12{background-color:#69707b}.inverted>.term13{background-color:#542996}.inverted>.term14{background-color:#4c4296}.inverted>.term15{background-color:#43957c}.inverted>.term16{background-color:#7d3a96}.inverted>.term17{background-color:#4b5896}.inverted>.term18{background-color:#737b66}.inverted>.term19{background-color:#848e42}.inverted>.term20{background-color:#81686b}.inverted>.term21{background-color:#2f9590}.inverted>.term22{background-color:#933f82}.inverted>.term23{background-color:#533496}.inverted>.term24{background-color:#748858}.inverted>.term25{background-color:#3d3696}.inverted>.term26{background-color:#864a84}.inverted>.term27{background-color:#5d8275}.inverted>.term28{background-color:#5a4796}.inverted>.term29{background-color:#2d4796}.inverted>.term30{background-color:#2b8296}.inverted>.term31{background-color:#5c7286}.inverted>.term32{background-color:#6a5296}.inverted>.term33{background-color:#422c96}.inverted>.term34{background-color:#71548f}.inverted>.term35{background-color:#8d6d5a}.inverted>.term36{background-color:#7d7265}.inverted>.term37{background-color:#5e3d96}.inverted>.term38{background-color:#96506e}.inverted>.term39{background-color:#362f96}.inverted>.term40{background-color:#897f4c}.inverted>.term41{background-color:#8e6d59}.inverted>.term42{background-color:#2d4c96}.inverted>.term43{background-color:#948a36}.inverted>.term44{background-color:#342f96}.inverted>.term45{background-color:#468886}.inverted>.term46{background-color:#327096}.inverted>.term47{background-color:#864688}.inverted>.term48{background-color:#835f72}.inverted>.term49{background-color:#3a9684}.inverted>.term50{background-color:#4f4496}\n",""]),e.exports=t},526:function(e,t,r){"use strict";r.r(t);var n=r(0),a=r.n(n),o=r(6),c=r.n(o),l=r(269),i=r(528),d=r(524),u=r(35),s=r(275),m=r(508),f=r(277),g=r(509),b=r(316),v=r.n(b),h=r(355),k=r.n(h);function p(e,t){return function(e){if(Array.isArray(e))return e}(e)||function(e,t){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e)){var r=[],n=!0,a=!1,o=void 0;try{for(var c,l=e[Symbol.iterator]();!(n=(c=l.next()).done)&&(r.push(c.value),!t||r.length!==t);n=!0);}catch(e){a=!0,o=e}finally{try{n||null==l.return||l.return()}finally{if(a)throw o}}return r}}(e,t)||function(e,t){if(e){if("string"==typeof e)return y(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(r):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?y(e,t):void 0}}(e,t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function y(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n}var E={fill:"#006dcc",background:"#2B2B2E",lineColor:"#DDD",tickColor:"#DDD",text:"#DDD"},w={fill:"#006dcc",background:"#FFF",lineColor:"#000",tickColor:"#000",text:"#000"};function C(e){var t=e.results,r=e.title,n=e.noDataMessage,o=e.width,c=e.inverted,l=[],i=[];t&&(i=Object.entries(t).map((function(e){var t=p(e,2),r=t[0],n=t[1];return l.push(r),n})));var d=w;c&&(d=E);var u={colors:[d.fill],chart:{type:"bar",backgroundColor:d.background,width:o},title:{text:r,style:{color:d.text}},legend:{enabled:!1},xAxis:{categories:l,title:{text:null},labels:{style:{color:d.text}},lineColor:d.lineColor,tickColor:d.tickColor},yAxis:{min:0,title:{text:"Count",align:"high"},labels:{overflow:"justify",style:{color:d.text}}},plotOptions:{bar:{dataLabels:{enabled:!1}}},credits:{enabled:!1},series:[{name:"Count",data:i}]};return a.a.createElement(a.a.Fragment,null,0<=i.length&&a.a.createElement(k.a,{highcharts:v.a,options:u}),0===i.length&&n)}C.propTypes={results:c.a.shape({title:c.a.string,value:c.a.string}).isRequired,title:c.a.string.isRequired,noDataMessage:c.a.string,width:c.a.number,inverted:c.a.bool},C.defaultProps={noDataMessage:"No data matched",width:null,inverted:!1};var S=C,j=r(520),O=r(272);function x(e){function t(e){var t="";return u&&(t="inverted"),a.a.createElement("div",{className:t,dangerouslySetInnerHTML:{__html:e}})}var r=e.results,n=e.page,o=e.lastPage,c=e.goBack,l=e.goNext,i=e.matchCount,d=e.resultCount,u=e.inverted,s=e.as;return a.a.createElement(a.a.Fragment,null,"table"===s&&a.a.createElement(a.a.Fragment,null,a.a.createElement(j.a,{celled:!0,collapsing:!0,inverted:u},r.map((function(e){return a.a.createElement(j.a.Row,{key:e.url},a.a.createElement(j.a.Cell,null,a.a.createElement("strong",null,a.a.createElement("a",{href:e.url},e.work," ",e.description))),a.a.createElement(j.a.Cell,null,t(e.highlights)))}))),a.a.createElement(f.a.Group,{attached:"bottom"},a.a.createElement(f.a,{inverted:u,active:n<=1,onClick:function(){return c()}},"Back"),a.a.createElement(f.a,{inverted:u,active:o<=n,onClick:function(){return l()}},"Next"))),"segment"===s&&a.a.createElement(O.a.Group,null,r.map((function(e){return a.a.createElement(O.a,{style:{padding:8},inverted:u,key:e.url},a.a.createElement("div",null,a.a.createElement("strong",null,a.a.createElement("a",{href:e.url},e.work," ",e.description))),t(e.highlights))})),a.a.createElement(f.a.Group,{attached:"bottom"},a.a.createElement(f.a,{inverted:u,active:n<=1,onClick:function(){return c()}},"Back"),a.a.createElement(f.a,{inverted:u,active:o<=n,onClick:function(){return l()}},"Next"))),a.a.createElement("div",null,"Page ",n," of ",o," (",i," word matches in ",d," verses)"))}x.propTypes={results:c.a.arrayOf(c.a.shape).isRequired,matchCount:c.a.number.isRequired,resultCount:c.a.number.isRequired,page:c.a.number.isRequired,lastPage:c.a.number.isRequired,goBack:c.a.func.isRequired,goNext:c.a.func.isRequired,inverted:c.a.bool,as:c.a.string},x.defaultProps={inverted:!1,as:"table"};var _=x,T=r(523);function N(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n}function A(e){function t(e,t){var r=t.index;s(i===r?-1:r)}var r=e.inverted,o={marginLeft:32,fontFamily:"monospace"},c={marginTop:10},l=function(e,t){return function(e){if(Array.isArray(e))return e}(e)||function(e,t){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e)){var r=[],n=!0,a=!1,o=void 0;try{for(var c,l=e[Symbol.iterator]();!(n=(c=l.next()).done)&&(r.push(c.value),!t||r.length!==t);n=!0);}catch(e){a=!0,o=e}finally{try{n||null==l.return||l.return()}finally{if(a)throw o}}return r}}(e,t)||function(e,t){if(e){if("string"==typeof e)return N(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(r):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?N(e,t):void 0}}(e,t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}(Object(n.useState)(null),2),i=l[0],s=l[1],m="";return r&&(m="inverted"),a.a.createElement(T.a,{inverted:r},a.a.createElement(T.a.Title,{active:0===i,index:0,onClick:t},a.a.createElement(u.a,{name:"dropdown"}),"How do I search?"),a.a.createElement(T.a.Content,{active:0===i},"The search language used by TextCritical.net allows several operations. Here are some common ones:",a.a.createElement("div",{style:c},"Search for verses with both ἱστορίας and νόμον:",a.a.createElement("div",{style:o},"ἱστορίας νόμον")),a.a.createElement("div",{style:c},'Search for verses with the phrase "ἱστορίας νόμον":',a.a.createElement("div",{style:o},'"ἱστορίας νόμον"')),a.a.createElement("div",{style:c},"Search for verses with the word ἱστορίας or νόμον:",a.a.createElement("div",{style:o},"ἱστορίας OR νόμον")),a.a.createElement("div",{style:c},"Search for verses with the word συγγνώμην provided they do not include either ἱστορίας or νόμον:",a.a.createElement("div",{style:o},"συγγνώμην NOT (ἱστορίας OR νόμον)")),a.a.createElement("div",{style:c},"The search engine accepts beta-code representations of Greek words. Thus, a search for no/mon is equivalent to a search for νόμον:",a.a.createElement("div",{style:o},"no/mon")),a.a.createElement(d.a,{info:!0,className:m,content:"If you are searching using beta-code, make sure to put your search query in single quotes (e.g. 'no/mon')"})),a.a.createElement(T.a.Title,{active:1===i,index:1,onClick:t},a.a.createElement(u.a,{name:"dropdown"}),"How do I search for related forms?"),a.a.createElement(T.a.Content,{active:1===i},"Searching for related forms causes the search engine to look for all other variations of a word. For example, a search for ἀδελφός would also search for ἀδελφοί, ἀδελφοῦ, ἀδελφοί, etc.",a.a.createElement(d.a,{info:!0,className:m,content:"Searching for related forms is considerably slower than searching for a particular form. "})),a.a.createElement(T.a.Title,{active:2===i,index:2,onClick:t},a.a.createElement(u.a,{name:"dropdown"}),"What fields can be searched?"),a.a.createElement(T.a.Content,{active:2===i},"Several fields exist that can be be searched. Just append the field name to the search with a colon to search it (e.g. work:new-testament). Below are the available fields:",a.a.createElement(j.a,{inverted:r},a.a.createElement(j.a.Header,null,a.a.createElement(j.a.Row,null,a.a.createElement(j.a.HeaderCell,null,"Field"),a.a.createElement(j.a.HeaderCell,null,"Description"),a.a.createElement(j.a.HeaderCell,null,"Example"))),a.a.createElement(j.a.Body,null,a.a.createElement(j.a.Row,null,a.a.createElement(j.a.Cell,null,"work"),a.a.createElement(j.a.Cell,null,"Search for items within a particular work (New Testament, Agammenon, etc.)"),a.a.createElement(j.a.Cell,null,'work:"New Testament"')),a.a.createElement(j.a.Row,null,a.a.createElement(j.a.Cell,null,"no_diacritics"),a.a.createElement(j.a.Cell,null,"Search for words disregarding the diacritical marks. Searching for no_diacritics:και will match on καὶ and καῖ"),a.a.createElement(j.a.Cell,null,"no_diacritics:ευαγγελιον")),a.a.createElement(j.a.Row,null,a.a.createElement(j.a.Cell,null,"section"),a.a.createElement(j.a.Cell,null,"Search for items within a section (chapter, division, book, etc.)"),a.a.createElement(j.a.Cell,null,'section:"Matthew 5"')),a.a.createElement(j.a.Row,null,a.a.createElement(j.a.Cell,null,"author"),a.a.createElement(j.a.Cell,null,"Search for verses within works created by a particular author."),a.a.createElement(j.a.Cell,null,'author:"Flavius Josephus"'))))))}A.propTypes={inverted:c.a.bool},A.defaultProps={inverted:!1};var R=A,q=r(284),I=r(286),B=r(282),P=r(280);function D(e){return function(e){if(Array.isArray(e))return H(e)}(e)||function(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}(e)||F(e)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function M(e,t){return function(e){if(Array.isArray(e))return e}(e)||function(e,t){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e)){var r=[],n=!0,a=!1,o=void 0;try{for(var c,l=e[Symbol.iterator]();!(n=(c=l.next()).done)&&(r.push(c.value),!t||r.length!==t);n=!0);}catch(e){a=!0,o=e}finally{try{n||null==l.return||l.return()}finally{if(a)throw o}}return r}}(e,t)||F(e,t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function F(e,t){if(e){if("string"==typeof e)return H(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(r):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?H(e,t):void 0}}function H(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n}r(356);var G={marginTop:12,marginRight:12,marginBottom:12};function L(e,t,r,n){var a=3<arguments.length&&void 0!==n?n:null,o=e.get(t);return o?0===a?parseInt(o,10):(1!==a||"0"!==o)&&(1===a||o):r}function U(e){var t=e.inverted,r=e.history,o=e.location,c=new URLSearchParams(Object(l.g)().search),b=M(Object(n.useState)(L(c,"q","")),2),v=b[0],h=b[1],k=M(Object(n.useState)(null),2),p=k[0],y=k[1],E=M(Object(n.useState)(null),2),w=E[0],C=E[1],j=M(Object(n.useState)(L(c,"ignore_diacritics",!1,1)),2),O=j[0],x=j[1],T=M(Object(n.useState)(L(c,"include_related",!1,1)),2),N=T[0],A=T[1],F=M(Object(n.useState)(!1),2),H=F[0],U=F[1],J=M(Object(n.useState)(L(c,"page",1,0)),2),$=J[0],z=J[1],K=M(Object(n.useState)(null),2),W=K[0],Q=K[1],V=M(Object(n.useState)(null),2),X=V[0],Y=V[1],Z="";t&&(Z="inverted");var ee=1;function te(e){var t,n,a,o;t=v,n=e,a=O,o=N,r.push(Object(P.e)(t,a,o,n))}function re(){1<$&&te($-1)}function ne(){$<ee&&te($+1)}p&&(ee=Math.ceil(p.result_count/10)),Object(n.useEffect)((function(){var e;o.key!==W&&(Q(o.key),e=L(c,"page",$,0),U(!0),C(null),z(e),fetch(Object(B.c)(v,e,O,N)).then((function(e){return e.json()})).then((function(e){y(e),U(!1),C(null)})).catch((function(e){C(e.toString()),U(!1),y(null)}))),!X&&o.state&&o.state.work&&Y(P.d.apply(void 0,[o.state.work].concat(D(o.state.divisions))))}));var ae=0;H?ae=1:w?ae=2:p&&0===p.result_count?ae=3:p&&0<p.result_count&&(ae=4);var oe="";t&&(oe=" inverted");var ce=[{menuItem:"Results",render:function(){return e=ae,r=p,n=$,o=ee,c=re,l=ne,s=w,f="",(m=t)&&(f="inverted"),a.a.createElement(i.a.Pane,{inverted:m},1===e&&a.a.createElement(d.a,{icon:!0,className:f},a.a.createElement(u.a,{name:"circle notched",loading:!0}),a.a.createElement(d.a.Content,null,a.a.createElement(d.a.Header,null,"Just one second"),"Performing the search...")),2===e&&a.a.createElement(q.a,{title:"Unable to perform the search",description:"The search could not be executed.",message:s,inverted:m}),3===e&&a.a.createElement(d.a,{className:f},a.a.createElement(d.a.Header,null,"No Results Found"),a.a.createElement("p",null,"No Results were found for the given search.")),4===e&&a.a.createElement(_,{results:r.results,matchCount:r.match_count,resultCount:r.result_count,page:n,lastPage:o,goBack:function(){return c()},goNext:function(){return l()},inverted:m}),0===e&&a.a.createElement(d.a,{className:f},a.a.createElement(d.a.Header,null,"Enter a search"),a.a.createElement("p",null,"Enter a search term to get started.")));var e,r,n,o,c,l,s,m,f}},{menuItem:"Matched words",render:function(){return a.a.createElement(i.a.Pane,{inverted:t},p&&0<Object.keys(p.matched_terms).length&&a.a.createElement(S,{results:p.matched_terms,title:"Frequency of matched words",noDataMessage:"No data available on matched terms",inverted:t}),(!p||0===Object.keys(p.matched_terms).length)&&a.a.createElement(d.a,{info:!0,className:oe},"No data available on matched terms"))}},{menuItem:"Matched works",render:function(){return a.a.createElement(i.a.Pane,{inverted:t},p&&0<Object.keys(p.matched_works).length&&a.a.createElement(S,{results:p.matched_works,title:"Frequency of matched works",noDataMessage:"No data available on matched works",inverted:t}),(!p||0===Object.keys(p.matched_works).length)&&a.a.createElement(d.a,{info:!0,className:oe},"No data available on matched works"))}},{menuItem:"Matched sections",render:function(){return a.a.createElement(i.a.Pane,{inverted:t},p&&0<Object.keys(p.matched_sections).length&&a.a.createElement(S,{results:p.matched_sections,title:"Frequency of matched sections",noDataMessage:"No data available on matched sections",inverted:t}),(!p||0===Object.keys(p.matched_sections).length)&&a.a.createElement(d.a,{info:!0,className:oe},"No data available on matched sections"))}},{menuItem:"Help",render:function(){return a.a.createElement(i.a.Pane,{inverted:t},a.a.createElement(R,{inverted:t}))}}];return a.a.createElement(I.a,{inverted:t,onClickBack:function(){X?r.push(X):r.push(Object(P.d)())},backTitle:"Back to the Library"},a.a.createElement(s.a,null,a.a.createElement(m.a,{action:a.a.createElement(f.a,{onClick:function(){return te(1)},basic:!0,inverted:t},"Go"),inverted:t,placeholder:"Enter the text to search for (e.g. νόμου or no/mou)",value:v,onChange:function(e,t){return h(t.value)},onKeyPress:function(e){"Enter"===e.key&&te(1)},style:{width:"100%"}}),a.a.createElement(g.a,{className:Z,style:G,label:"Search ignoring diacritics",checked:O,onChange:function(e,t){return x(t.checked)}}),a.a.createElement(g.a,{className:Z,style:G,label:"Search related Greek forms (slower but more thorough)",checked:N,onChange:function(e,t){return A(t.checked)}}),a.a.createElement(i.a,{className:Z,panes:ce})))}U.propTypes={history:c.a.object.isRequired,location:c.a.object.isRequired,inverted:c.a.bool},U.defaultProps={inverted:!1},t.default=Object(l.h)(U)}}]);
//# sourceMappingURL=4.js.map