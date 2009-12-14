google.load("jquery", "1");
google.load("jqueryui", "1");


// Global error indicator
function init_error_indicator() {
  $("body").ajaxError(function(event, request, settings){
    var err_msg;
    switch(request.status) {
      case 404:
        err_msg = "Oops! Got 404 NOT FOUND, this should be a bug, you may notify the problem generator, the creator of Twimonial.";
        break;
      case 500:
        err_msg = "It is 500! Server does not want to serve you! :-)";
        break;
      default:
        err_msg = "Unknown problem!";
      }
    humanMsg.displayMsg(err_msg, 'error');
    });
  }


function agree(id) {
  var query_url = window.location.protocol + '//' + window.location.host + '/';
  if (id == '#')
    return;
  $.getJSON(query_url + 'agree.json?id=' + id + '&callback=?', function(json) {
    if (json.error == 0) {
      $("a.agree-button").each(function(){
        var $ele = $(this);
        if ($ele.attr('href').indexOf("(" + json.id + ")") >= 0) {
          humanMsg.displayMsg(json.message, 'message');
          $ele.fadeOut('fast').remove();
          return false;
          }
        });
      }
    else
      humanMsg.displayMsg(json.message, 'error');
    });
  }


// Read Twimonials of a Twitter
function f1() {
  var screen_name = $('#f1_screen_name').val().replace('@', '');
  if (screen_name.replace(/[_a-zA-Z0-9]/g, '')) {
    humanMsg.displayMsg(screen_name + ' is not a valid screen name!', 'error');
    return
    }
  var url = window.location.protocol + '//' + window.location.host + '/';
  window.location = url + 'user/' + screen_name;
  }

// List most agreed over time
function f2() {
  var screen_names = $('#f2_screen_names').val().replace('@', '').split(/ +/);
  for (var i=0; i<screen_names.length; i++)
    if (screen_names[i].replace(/[_a-zA-Z0-9]/g, '')) {
      humanMsg.displayMsg(screen_names[i] + ' is not a valid screen name!', 'error');
      return
      }
  var url = window.location.protocol + '//' + window.location.host + '/';
  window.location = url + 'list/' + screen_names.slice(0, 10).sort().join('-');
  }

// List Twimonials written by screen_name
function f3() {
  var screen_name = $('#f3_screen_name').val().replace('@', '');
  if (screen_name.replace(/[_a-zA-Z0-9]/g, '')) {
    humanMsg.displayMsg(screen_name + ' is not a valid screen name!', 'error');
    return
    }
  var screen_names = $('#f3_screen_names').val().replace('@', '').split(/ +/);
  for (var i=0; i<screen_names.length; i++)
    if (screen_names[i].replace(/[_a-zA-Z0-9]/g, '')) {
      humanMsg.displayMsg(screen_names[i] + ' is not a valid screen name!', 'error');
      return
      }
  var url = window.location.protocol + '//' + window.location.host + '/';
  window.location = url + 'userlist/' + screen_name + '/' + screen_names.slice(0, 10).sort().join('-');
  }

function go_jmp() {
  $.getJSON('http://api.j.mp/shorten?version=2.0.1&longUrl=' + encodeURI(window.location.href) + '&login=livibetter&apiKey=' + 'R_78405bb48525800fb880b41721029724&callback=?', function(json) {
    if (json.errorCode == 0) {
      for (var r in json.results) {
        result = json.results[r];
        break;
        }
      $('#jmp').replaceWith('<div id="jmp">' + result['shortUrl'] + '</div>');
      $('span.page-uri').text(result['shortUrl']);
      }
    else
      humanMsg.displayMsg(json.errorMessage, 'error');
    });
  }

google.setOnLoadCallback(function () {
  var messages = window.lso_messages;
  if (messages)
    for (i=0; i<messages.length; i++)
      humanMsg.displayMsg(messages[i][1], messages[i][0]);
  init_error_indicator();
  $('.jquery-ui-tabs').tabs();
  $('a.agree-button').attr('title', 'Click to agree this twimonial');
  $('#jmp').click(go_jmp).css('cursor', 'pointer').attr('title', 'Click to get a shortened url of this page');
  $('span.screen-name').each(function(index){
    var ele = $(this);
    var t = $('<a href="http://twitter.com/"' + ele.text() + '"><img src="/img/twitter.png" title="Go to ' + ele.text() + '\'s Twitter profile page"/></a>');
    t.fadeTo('fast', 0.5)
      .mouseenter(function() $(this).fadeTo('normal', 1.0))
      .mouseleave(function() $(this).fadeTo('normal', 0.5));
    ele.after(t);
    });
  $('span.page-uri').text(window.location.href);
  });

// vim:ts=2:sw=2:et:
