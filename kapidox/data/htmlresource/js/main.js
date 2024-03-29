/** copied from develop.kde.org */
(function($){'use strict';$(function(){$('[data-toggle="tooltip"]').tooltip();$('[data-toggle="popover"]').popover();$('.popover-dismiss').popover({trigger:'focus'})});function bottomPos(element){return element.offset().top+element.outerHeight();}
$(function(){var promo=$(".js-td-cover");if(!promo.length){return}
var promoOffset=bottomPos(promo);var navbarOffset=$('.js-navbar-scroll').offset().top;var threshold=Math.ceil($('.js-navbar-scroll').outerHeight());if((promoOffset-navbarOffset)<threshold){$('.js-navbar-scroll').addClass('navbar-bg-onscroll');}
$(window).on('scroll',function(){var navtop=$('.js-navbar-scroll').offset().top-$(window).scrollTop();var promoOffset=bottomPos($('.js-td-cover'));var navbarOffset=$('.js-navbar-scroll').offset().top;if((promoOffset-navbarOffset)<threshold){$('.js-navbar-scroll').addClass('navbar-bg-onscroll');}else{$('.js-navbar-scroll').removeClass('navbar-bg-onscroll');$('.js-navbar-scroll').addClass('navbar-bg-onscroll--fade');}});});}(jQuery));function getOffsetSum(elem){var top=0,left=0
while(elem){top=top+parseInt(elem.offsetTop)
left=left+parseInt(elem.offsetLeft)
elem=elem.offsetParent}
return{top:top,left:left}}
function setActiveMenuItem(li){var isMenuItem=li.matches('#TableOfContents > ul > li')
var isSubMenuItem=li.matches('#TableOfContents > ul > li > ul > li')
var wasActive=li.classList.contains('active')
if(isMenuItem||!wasActive){var menuItem=document.querySelector('#TableOfContents > ul > li.active')
if(menuItem){menuItem.classList.remove('active')}
var menuItem=document.querySelector('#TableOfContents > ul > li > ul > li.active')
if(menuItem){menuItem.classList.remove('active')}}
li.classList.add('active')
if(isMenuItem){var firstSubMenuItem=li.querySelector('ul > li')
if(firstSubMenuItem){firstSubMenuItem.classList.add('active')}}else if(isSubMenuItem){var menuItem=li.parentNode.parentNode
menuItem.classList.add('active')}}
function getMenuItemElement(li){var id=li.querySelector('a').href.split('#',2)[1]
return document.getElementById(id)}
function updateTOC(){var viewTop=window.scrollY
var tocList=document.querySelectorAll('#TableOfContents li')
for(var i=0;i<tocList.length;i++){var curMenuItem=tocList[i]
var curElement=getMenuItemElement(curMenuItem)
var offset=getOffsetSum(curElement)
var offsetDiff=viewTop-offset.top
if(offsetDiff<0){if(i<=1){setActiveMenuItem(curMenuItem)}else{var prevMenuItem=tocList[i-1]
var prevElement=getMenuItemElement(prevMenuItem)
var prevOffset=getOffsetSum(prevElement)
var prevOffsetDiff=viewTop-prevOffset.top
var sectionReadRatio=(prevOffsetDiff)/prevMenuItem.offsetHeight
if(sectionReadRatio>=0.7){setActiveMenuItem(curMenuItem)}else{setActiveMenuItem(prevMenuItem)}}
break}else if(i==tocList.length-1){setActiveMenuItem(curMenuItem)}}}
var updating=false
function queueUpdateTOC(){if(!updating){updating=true
requestAnimationFrame(function(){updateTOC()
updating=false})}}
queueUpdateTOC()
window.addEventListener('scroll',queueUpdateTOC);(function($){'use strict';$(function(){var article=document.getElementsByTagName('main')[0];if(!article){return;}
var headings=article.querySelectorAll('h1, h2, h3, h4, h5, h6');headings.forEach(function(heading){if(heading.id){var a=document.createElement('a');a.style.visibility='hidden';a.setAttribute('aria-hidden','true');a.innerHTML=' <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" width="24" height="24" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"/><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/></svg>';a.href='#'+heading.id;heading.insertAdjacentElement('beforeend',a);heading.addEventListener('mouseenter',function(){a.style.visibility='initial';});heading.addEventListener('mouseleave',function(){a.style.visibility='hidden';});}});});}(jQuery));;(function($){'use strict';$(document).ready(function(){const $searchInput=$('.td-search-input');$searchInput.data('html',true);$searchInput.data('placement','bottom');$searchInput.data('template','<div class="popover offline-search-result" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>');$searchInput.on('change',(event)=>{render($(event.target));$searchInput.blur();});$searchInput.closest('form').on('submit',()=>{return false;});let idx=null;const resultDetails=new Map();$.ajax($searchInput.data('offline-search-index-json-src')).then((data)=>{idx=lunr(function(){this.ref('ref');this.field('title',{boost:2});this.field('body');data.forEach((doc)=>{this.add(doc);resultDetails.set(doc.ref,{title:doc.title,excerpt:doc.excerpt,});});});$searchInput.trigger('change');});const render=($targetSearchInput)=>{$targetSearchInput.popover('dispose');if(idx===null){return;}
const searchQuery=$targetSearchInput.val();if(searchQuery===''){return;}
const results=idx.query((q)=>{const tokens=lunr.tokenizer(searchQuery.toLowerCase());tokens.forEach((token)=>{const queryString=token.toString();q.term(queryString,{boost:100,});q.term(queryString,{wildcard:lunr.Query.wildcard.LEADING|lunr.Query.wildcard.TRAILING,boost:10,});q.term(queryString,{editDistance:2,});});}).slice(0,10);const $html=$('<div>');$html.append($('<div>').css({display:'flex',justifyContent:'space-between',marginBottom:'1em',}).append($('<span>').text('Search results').css({fontWeight:'bold'})).append($('<i>').addClass('fas fa-times search-result-close-button').css({cursor:'pointer',})));const $searchResultBody=$('<div>').css({maxHeight:`calc(100vh - ${
$targetSearchInput.offset().top-
$(window).scrollTop()+
180
}px)`,overflowY:'auto',});$html.append($searchResultBody);if(results.length===0){$searchResultBody.append($('<p>').text(`No results found for query "${searchQuery}"`));}else{results.forEach((r)=>{const $cardHeader=$('<div>').addClass('card-header');const doc=resultDetails.get(r.ref);const href=$searchInput.data('offline-search-base-href')+
r.ref.replace(/^\//,'');$cardHeader.append($('<a>').attr('href',href).text(doc.title));const $cardBody=$('<div>').addClass('card-body');$cardBody.append($('<p>').addClass('card-text text-muted').text(doc.excerpt));const $card=$('<div>').addClass('card');$card.append($cardHeader).append($cardBody);$searchResultBody.append($card);});}
$targetSearchInput.on('shown.bs.popover',()=>{$('.search-result-close-button').on('click',()=>{$targetSearchInput.val('');$targetSearchInput.trigger('change');});});$targetSearchInput.data('content',$html[0].outerHTML).popover('show');};});})(jQuery);
