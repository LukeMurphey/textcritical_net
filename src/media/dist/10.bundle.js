(window.webpackJsonp=window.webpackJsonp||[]).push([[10],{283:function(e,t,n){"use strict";n.d(t,"g",(function(){return r})),n.d(t,"a",(function(){return a})),n.d(t,"e",(function(){return i})),n.d(t,"f",(function(){return o})),n.d(t,"b",(function(){return l})),n.d(t,"d",(function(){return u})),n.d(t,"c",(function(){return d}));var c=n(285);function r(){return"/"}function a(){return"/beta_code_converter"}function i(){for(var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,n="",r=arguments.length,a=new Array(r>2?r-2:0),i=2;i<r;i++)a[i-2]=arguments[i];var o=a.filter((function(e){return e}));return a.length>0&&e?(n=o.join("/"),"".concat("/work","/").concat(e,"/").concat(n).concat(Object(c.c)(t))):"".concat("/work","/").concat(e)}function o(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=arguments.length>2&&void 0!==arguments[2]&&arguments[2],r=arguments.length>3&&void 0!==arguments[3]?arguments[3]:"";return"".concat("/search").concat(Object(c.d)(e,t,n,r))}function l(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("https://www.google.com/search").concat(Object(c.a)(e))}function u(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("http://www.perseus.tufts.edu/hopper/morph").concat(Object(c.b)(e))}function d(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("https://logeion.uchicago.edu","/").concat(e)}},285:function(e,t,n){"use strict";function c(e){return 0===e.length?e:"?".concat(e)}function r(e,t){return e.length>0?"&".concat(t):t}function a(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=arguments.length>2&&void 0!==arguments[2]&&arguments[2],a=arguments.length>3&&void 0!==arguments[3]?arguments[3]:"",i="";return e&&(i+=r(i,"q=".concat(e))),a&&(i+=r(i,"page=".concat(a))),t&&(i+=r(i,"ignore_diacritics=1")),n&&(i+=r(i,"include_related=1")),c(i)}function i(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:null,t="";return e&&(t+=r(t,"parallel=".concat(e))),c(t)}function o(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t="";return e&&(t+="l=".concat(e,"&la=greek")),c(t)}function l(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t="";return e&&(t="q=".concat(e)),c(t)}n.d(t,"d",(function(){return a})),n.d(t,"c",(function(){return i})),n.d(t,"b",(function(){return o})),n.d(t,"a",(function(){return l}))},289:function(e,t,n){"use strict";var c=n(0),r=n.n(c),a=n(277),i=n(274),o=n(35),l=n(281),u=n(302),d=n(6),s=n.n(d),f={display:"inline-block",fontSize:16,textAlign:"middle"},h={cursor:"pointer",marginBottom:0},v={display:"inline-block",fontSize:12,verticalAlign:"top",paddingLeft:12,color:"white"},g={marginTop:0},p=function(e){var t=e.children,n=e.onClickBack,c=e.inverted,d=e.backTitle;return r.a.createElement(a.a,null,r.a.createElement(i.a,{compact:!0,style:h,onClick:n,inverted:c},r.a.createElement("div",{style:f},r.a.createElement(o.a,{name:"arrow left",corner:"top left",fitted:!0})),r.a.createElement("div",{style:v},r.a.createElement(l.a,{inverted:c,as:"h4"},d))),r.a.createElement(u.a,{style:{marginTop:0}}),r.a.createElement(i.a,{compact:!0,style:g,inverted:c},t))};p.propTypes={children:s.a.object.isRequired,inverted:s.a.bool,onClickBack:s.a.func,backTitle:s.a.string},p.defaultProps={inverted:!1,onClickBack:function(){},backTitle:"Back"},t.a=p},302:function(e,t,n){"use strict";var c=n(2),r=n.n(c),a=n(3),i=n.n(a),o=n(0),l=n.n(o),u=n(16),d=n(76),s=n(77),f=n(5);function h(e){var t=e.children,n=e.className,c=e.clearing,a=e.content,o=e.fitted,v=e.hidden,g=e.horizontal,p=e.inverted,b=e.section,m=e.vertical,k=i()("ui",Object(u.a)(c,"clearing"),Object(u.a)(o,"fitted"),Object(u.a)(v,"hidden"),Object(u.a)(g,"horizontal"),Object(u.a)(p,"inverted"),Object(u.a)(b,"section"),Object(u.a)(m,"vertical"),"divider",n),j=Object(d.a)(h,e),w=Object(s.a)(h,e);return l.a.createElement(w,r()({},j,{className:k}),f.a.isNil(t)?a:t)}h.handledProps=["as","children","className","clearing","content","fitted","hidden","horizontal","inverted","section","vertical"],h.propTypes={},t.a=h},518:function(e,t,n){"use strict";n.r(t);var c=n(0),r=n.n(c),a=n(277),i=n(274),o=n(281),l=n(6),u=n.n(l),d=n(270),s=n(283),f=n(289),h=function(e){var t=e.inverted,n=e.history;return r.a.createElement(f.a,{inverted:t,onClickBack:function(){n.push(Object(s.e)())},backTitle:"Back to the Library"},r.a.createElement(a.a,null,r.a.createElement(i.a,{inverted:t},r.a.createElement(o.a,{as:"h1"},"Getting in Touch"),"If you found something that does not work, please"," ",r.a.createElement("a",{href:"https://github.com/LukeMurphey/textcritical_net/issues"},"create an issue"),".")))};h.propTypes={inverted:u.a.bool,history:u.a.object.isRequired},h.defaultProps={inverted:!1},t.default=Object(d.h)(h)}}]);
//# sourceMappingURL=10.js.map