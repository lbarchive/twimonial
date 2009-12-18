check_twitter_userpage();
window.addEventListener("focus", check_twitter_userpage);

function check_twitter_userpage() {
  if (document.body.id == 'profile') {
    var screen_name = window.location.href.replace('http://twitter.com/', '');
    chrome.extension.sendRequest({msg: "twimonialIcon", screen_name: screen_name});
	}
  }
