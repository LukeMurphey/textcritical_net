/* Author: Luke Murphey

*/

var TextCritical = {};

/**
 * Causes the verses to break onto separate lines. 
 **/
TextCritical.setFormatBreakLine = function(){
	$('.verse_container').addClass("block");
	$('#align_break').addClass('active');
}

/**
 * Causes the verses to not break onto separate lines. 
 **/
TextCritical.unSetFormatBreakLine = function(){
	$('.verse_container').removeClass("block");
	$('#align_break').removeClass('active');
}

/**
 * Toggles the table-of-contents.
 **/
TextCritical.toggleTOC = function(){
	$('.table_of_contents').toggle('fast', 'swing');
}

/**
 * TOggles the verse breaks.
 **/
TextCritical.toggleVerseBreak = function(){
	break_verses = !break_verses;
	
	if( break_verses ){
		TextCritical.setFormatBreakLine();
	}
	else{
		TextCritical.unSetFormatBreakLine();
	}
	
	settings.set("break_verses", break_verses);
}

/**
 * Scrolls to the given anchor.
 **/
TextCritical.scrolltoAnchor = function(id){
	$('html,body').animate({scrollTop: $("#"+id).offset().top},'slow');
}

/**
 * Highlight a selected verse without performing a request to the server.
 **/
TextCritical.scrollToVerse = function(verse_number){

	
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
	TextCritical.scrolltoAnchor(id);
	
	return false; // Stop the page from reloading
	
}

/**
 * Loads the client-saved settings.
 **/
TextCritical.loadStoreSettings = function(){
	/*
	 * Load the user's settings from local storage.
	 */
	
	var defaults = {
		"break_verses": false
	};
	
	settings = new Store("settings");
	
	break_verses = settings.get("break_verses", defaults);
	
	if( break_verses ){
		TextCritical.setFormatBreakLine();
		
	}
}

/**
 * Determines the path that corresponds to the given reference.
 **/
TextCritical.resolve_path = function( reference ){

    // Break up the path
    var path_array = window.location.pathname.split( '/' );
    var path = [];
    
    for( i = 0; i < path_array.length; i++){
    	if( path_array[i].length > 0 ){
    		path.push(path_array[i]);
    	}
    	
    	if( path.length >= 2 ){
    	   break;
    	}
    }
    
    // Break up the reference entry
    refs = reference.split(/[- :._]+/);
    
    // Make the path
    return "/" + path.concat(refs).join("/");
}

/**
 * Opens the view to the given chapter reference.
 **/
TextCritical.go_to_chapter = function( reference ){
	document.location = TextCritical.resolve_path(reference);
}