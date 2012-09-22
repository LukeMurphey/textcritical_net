/* Author:

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
	
	var id = "verse_" + verse_number
	
	// Update the URL
	
	// Remove existing highlights
	$('.verse_container').removeClass('highlighted');
	$('.verse.number').removeClass('label-info');
	
	
	// Highlight the verse
	$('#' + id).addClass('highlighted');
	$('#' + id + '.verse.number').addClass('label-info');
	
	// Scroll to the verse
	scrolltoAnchor(id);
	
	return false; // Stop the page from reloading
	
}

function loadStoreSettings(){
	
	var defaults = {
		"break_verses": false
	};
	
	settings = new Store("settings");
	
	break_verses = settings.get("break_verses", defaults);
	
	if( break_verses ){
		setFormatBreakLine();
		
	}
}