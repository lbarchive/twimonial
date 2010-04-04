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
          $ele.css('opacity', 1.0);
          $ele.unbind();
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
  var screen_name = $('#f1_screen_name').val().replace(/@/g, '');
  if (screen_name.replace(/[_a-zA-Z0-9]/g, '')) {
    humanMsg.displayMsg(screen_name + ' is not a valid screen name!', 'error');
    return
    }
  var url = window.location.protocol + '//' + window.location.host + '/';
  window.location = url + 'user/' + screen_name;
  }

// List most agreed over time
function f2() {
  var screen_names = $('#f2_screen_names').val().replace(/@/g, '').split(/ +/);
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
  var screen_name = $('#f3_screen_name').val().replace(/@/g, '');
  if (screen_name.replace(/[_a-zA-Z0-9]/g, '')) {
    humanMsg.displayMsg(screen_name + ' is not a valid screen name!', 'error');
    return
    }
  var screen_names = $('#f3_screen_names').val().replace(/@/g, '').split(/ +/);
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
      $('span.page-uri')
          .text(result['shortUrl'])
          .attr('title', '')
          .unbind('click', go_jmp)
          .removeClass('page-uri');
      }
    else
      humanMsg.displayMsg(json.errorMessage, 'error');
    });
  }

function update_count() {
    $('#fm-count').text(140 - $('#fm-testimonial').val().length - 13 - $('#fm-to').val().length);
    }

function tweet_testimonial() {
    if ($('#fm-testimonial').val() == '' ||  $('#fm-to').val() == '')
      return;
    var tweet = $('#fm-testimonial').val() + ' #twimonial @' + $('#fm-to').val();
    window.open('http://twitter.com/home?status=' + encodeURIComponent(tweet));
    }

function jumpto_relocate() {
  var window_top = $(window).scrollTop();
  var div_top = $('div.jumpto_anchor').offset().top;
  if (window_top > div_top) {
    $('div.jumpto').addClass('stick');
    }
  else{
    $('div.jumpto').removeClass('stick');
    }
  }

google.setOnLoadCallback(function () {
  var messages = window.lso_messages;
  if (messages)
    for (i=0; i<messages.length; i++)
      humanMsg.displayMsg(messages[i][1], messages[i][0]);
  init_error_indicator();
  $('.jquery-ui-tabs').tabs();
  $('a.agree-button')
      .attr('title', 'Click to agree with this testimonial')
      .css('background', 'url(/img/agree.png) no-repeat')
      .css('opacity', 0.5)
      .mouseenter(function() {$(this).fadeTo('normal', 1.0)})
      .mouseleave(function() {$(this).fadeTo('normal', 0.5)})
      ;
  
  $('#header').prepend('<div id="jmp"><span class="page-uri" title="Click to shortened URI of this page">j.mp</span></div>')
  $('pre.tweet span.page-uri').text(window.location.href);
  $('span.page-uri').click(go_jmp);

  $('span.screen-name').each(function(index){
    var ele = $(this);
    var t = $('<a href="' + SERVICE_URI + ele.text() + '"><img src="/img/' + SERVICE_NAME.toLowerCase() + '.png" title="Go to ' + ele.text() + "'s " + SERVICE_NAME + ' profile page"/></a>');
    t.fadeTo('fast', 0.5)
      .mouseenter(function() {$(this).fadeTo('normal', 1.0)})
      .mouseleave(function() {$(this).fadeTo('normal', 0.5)});
    ele.after(t);
    });
  if ($('#fm').length) {
    $('#fm-testimonial').keyup(update_count);
    $('#fm-testimonial').change(update_count);
    $('#fm-to').keyup(update_count);
    $('#fm-to').change(update_count);
    update_count();
    }

  $('#followday option:nth-child(' + String((new Date()).getDay() + 1) + ')').attr('selected', 'selected');
  
  $(window).scroll(jumpto_relocate);
  jump_relocate();
  });

// vim:ts=2:sw=2:et:
