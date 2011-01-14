function setExpanded(event){
	event.preventDefault();
	var parent=jq(this).parent();
	var ul=parent.children('ul');
	if (ul.hasClass('hiddenMembers')) {
		ul.removeClass('hiddenMembers');
		jq(ul).hide();
	}
	jq(ul).slideToggle(200);
	jq(this).toggleClass('collapsedButton');
	jq(this).toggleClass('expandedButton');
}


jq(document).ready(function() {
	var blocks=jq('ul.roomGroupMembers');
	var groups=jq('a.groupName');
	jq(groups).each(function(i){
		jq(this).addClass('collapsedButton');
		jq(this).bind('click', setExpanded);
	});
});

