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


function resolve_path( reference ){

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

function go_to_chapter( reference ){
	document.location = resolve_path(reference);
}