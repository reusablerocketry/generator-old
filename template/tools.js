function update_time() {
  $('#current-time').text(Math.round(Date.now() * 0.001));
}

$(window).focus(function() {
  update_time();
});

update_time()
