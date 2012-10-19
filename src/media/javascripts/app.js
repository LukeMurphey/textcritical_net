/* Author: Luke Murphey

*/


function setFormatBreakLine(){
	$('.verse_container').addClass("block");
	$('#align_break').addClass('active');
}

function unSetFormatBreakLine(){
	$('.verse_container').removeClass("block");
	$('#align_break').removeClass('active');
}

function toggleTOC(){
	$('.table_of_contents').toggle('fast', 'swing');
}

function toggleVerseBreak(){
	break_verses = !break_verses;
	
	if( break_verses ){
		setFormatBreakLine();
	}
	else{
		unSetFormatBreakLine();
	}
	
	settings.set("break_verses", break_verses);
}

function scrolltoAnchor(id){
	$('html,body').animate({scrollTop: $("#"+id).offset().top},'slow');
}

function scrollToVerse(verse_number){
	/*
	 * This function allows users to highlight a verse without performing a request to the server. 
	 */
	
	// The ID of the verse number element
	var id = "verse_" + verse_number
	
	// Update the URL
	title = document.title;
	path = window.location.pathname;
	history.pushState( {verse: verse_number}, title, path + "?verse=" + verse_number);
	
	// Remove existing highlights
	$('.verse_container').removeClass('highlighted');
	$('.verse.number').removeClass('label-info');
	
	// Highlight the new verse
	$('#' + id).addClass('highlighted');
	$('#' + id + ' .label').addClass('label-info');
	
	// Scroll to the verse
	scrolltoAnchor(id);
	
	return false; // Stop the page from reloading
	
}

function loadStoreSettings(){
	/*
	 * Load the user's settings from local storage.
	 */
	
	var defaults = {
		"break_verses": false
	};
	
	settings = new Store("settings");
	
	break_verses = settings.get("break_verses", defaults);
	
	if( break_verses ){
		setFormatBreakLine();
		
	}
}