(window.webpackJsonp=window.webpackJsonp||[]).push([[8],{283:function(e,t,n){"use strict";function r(e){return e.replace(/\w\S*/g,(function(e){return e.charAt(0).toUpperCase()+e.substr(1).toLowerCase()}))}function c(e,t){return e.length>t?"".concat(e.substring(0,t-3),"..."):e}function o(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"click";window.addEventListener(t,e)}function i(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"click";window.removeEventListener(t,e)}function a(e){var t={x:e.offsetLeft,y:e.offsetTop};if(e.offsetParent){var n=a(e.offsetParent);t.x+=n.x,t.y+=n.y}return t}function u(e){var t=document.getElementById(e);t&&t.scrollIntoView({behavior:"smooth",block:"start",inline:"nearest"})}function l(e,t){return e.findIndex((function(e){return!!e&&0===e.localeCompare(t,void 0,{sensitivity:"base"})}))}function d(e){return 0===e.length?e:"?".concat(e)}function s(e,t){return e.length>0?"&".concat(t):t}n.d(t,"h",(function(){return r})),n.d(t,"i",(function(){return c})),n.d(t,"a",(function(){return o})),n.d(t,"f",(function(){return i})),n.d(t,"d",(function(){return a})),n.d(t,"g",(function(){return u})),n.d(t,"e",(function(){return l})),n.d(t,"c",(function(){return d})),n.d(t,"b",(function(){return s}))},285:function(e,t,n){"use strict";n.d(t,"g",(function(){return c})),n.d(t,"a",(function(){return o})),n.d(t,"e",(function(){return i})),n.d(t,"f",(function(){return a})),n.d(t,"b",(function(){return u})),n.d(t,"d",(function(){return l})),n.d(t,"c",(function(){return d}));var r=n(286);function c(){return"/"}function o(){return"/beta_code_converter"}function i(){for(var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,n="",c=arguments.length,o=new Array(c>2?c-2:0),i=2;i<c;i++)o[i-2]=arguments[i];var a=o.filter((function(e){return e}));return o.length>0&&e?(n=a.join("/"),"".concat("/work","/").concat(e,"/").concat(n).concat(Object(r.c)(t))):"".concat("/work","/").concat(e)}function a(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=arguments.length>2&&void 0!==arguments[2]&&arguments[2],c=arguments.length>3&&void 0!==arguments[3]?arguments[3]:"";return"".concat("/search").concat(Object(r.d)(e,t,n,c))}function u(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("https://www.google.com/search").concat(Object(r.a)(e))}function l(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("http://www.perseus.tufts.edu/hopper/morph").concat(Object(r.b)(e))}function d(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return"".concat("https://logeion.uchicago.edu","/").concat(e)}},286:function(e,t,n){"use strict";n.d(t,"d",(function(){return c})),n.d(t,"c",(function(){return o})),n.d(t,"b",(function(){return i})),n.d(t,"a",(function(){return a}));var r=n(283);function c(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=arguments.length>2&&void 0!==arguments[2]&&arguments[2],c=arguments.length>3&&void 0!==arguments[3]?arguments[3]:"",o="";return e&&(o+=Object(r.b)(o,"q=".concat(e))),c&&(o+=Object(r.b)(o,"page=".concat(c))),t&&(o+=Object(r.b)(o,"ignore_diacritics=1")),n&&(o+=Object(r.b)(o,"include_related=1")),Object(r.c)(o)}function o(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:null,t="";return e&&(t+=Object(r.b)(t,"parallel=".concat(e))),Object(r.c)(t)}function i(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t="";return e&&(t+="l=".concat(e,"&la=greek")),Object(r.c)(t)}function a(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",t="";return e&&(t="q=".concat(e)),Object(r.c)(t)}},290:function(e,t,n){"use strict";var r=n(0),c=n.n(r),o=n(277),i=n(274),a=n(35),u=n(280),l=n(303),d=n(6),s=n.n(d),f={display:"inline-block",fontSize:16,textAlign:"middle"},v={cursor:"pointer",marginBottom:0},h={display:"inline-block",fontSize:12,verticalAlign:"top",paddingLeft:12,color:"white"},b={marginTop:0},p=function(e){var t=e.children,n=e.onClickBack,r=e.inverted,d=e.backTitle;return c.a.createElement(o.a,null,c.a.createElement(i.a,{compact:!0,style:v,onClick:n,inverted:r},c.a.createElement("div",{style:f},c.a.createElement(a.a,{name:"arrow left",corner:"top left",fitted:!0})),c.a.createElement("div",{style:h},c.a.createElement(u.a,{inverted:r,as:"h4"},d))),c.a.createElement(l.a,{style:{marginTop:0}}),c.a.createElement(i.a,{compact:!0,style:b,inverted:r},t))};p.propTypes={children:s.a.object.isRequired,inverted:s.a.bool,onClickBack:s.a.func,backTitle:s.a.string},p.defaultProps={inverted:!1,onClickBack:function(){},backTitle:"Back"},t.a=p},303:function(e,t,n){"use strict";var r=n(2),c=n.n(r),o=n(3),i=n.n(o),a=n(0),u=n.n(a),l=n(16),d=n(76),s=n(77),f=n(5);function v(e){var t=e.children,n=e.className,r=e.clearing,o=e.content,a=e.fitted,h=e.hidden,b=e.horizontal,p=e.inverted,g=e.section,m=e.vertical,k=i()("ui",Object(l.a)(r,"clearing"),Object(l.a)(a,"fitted"),Object(l.a)(h,"hidden"),Object(l.a)(b,"horizontal"),Object(l.a)(p,"inverted"),Object(l.a)(g,"section"),Object(l.a)(m,"vertical"),"divider",n),j=Object(d.a)(v,e),w=Object(s.a)(v,e);return u.a.createElement(w,c()({},j,{className:k}),f.a.isNil(t)?o:t)}v.handledProps=["as","children","className","clearing","content","fitted","hidden","horizontal","inverted","section","vertical"],v.propTypes={},t.a=v},520:function(e,t,n){"use strict";n.r(t);var r=n(0),c=n.n(r),o=n(277),i=n(274),a=n(280),u=n(6),l=n.n(u),d=n(270),s=n(285),f=n(290),v=function(e){var t=e.inverted,n=e.history;return c.a.createElement(f.a,{inverted:t,onClickBack:function(){n.push(Object(s.e)())},backTitle:"Back to the Library"},c.a.createElement(o.a,null,c.a.createElement(i.a,{inverted:t},c.a.createElement(a.a,{as:"h1"},"About TextCritical.net"),"TextCritical.net is a website that provides ancient Greek texts and useful analysis tools.",c.a.createElement(a.a,{as:"h2"},"Source Code"),"This site is open source. See"," ",c.a.createElement("a",{target:"blank",href:"https://lukemurphey.net/projects/ancient-text-reader/"},"LukeMurphey.net"),"for information regarding how to get access to the source code and how to set up your own instance of the site for development purposes.")))};v.propTypes={history:l.a.object.isRequired,inverted:l.a.bool},v.defaultProps={inverted:!1},v.defaultProps={inverted:!1},t.default=Object(d.h)(v)}}]);
//# sourceMappingURL=8.js.map