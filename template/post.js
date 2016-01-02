
function time_difference(date) {

  var minute = 60;
  var hour = minute * 60;
  var day = hour * 24;
  var week = day * 7;
  var month = day * 30;
  var year = month * 12;

  var elapsed = (Date.now() * 0.001) - date;

  var factor = 1;
  var unit = '';

  console.log(elapsed);

  if(elapsed < minute)
    return 'a few seconds ago';

  if(elapsed < hour) {
    factor = minute;
    unit = 'minute';
  } else if(elapsed < day) {
    factor = hour;
    unit = 'hour';
  } else if(elapsed < month) {
    factor = week;
    unit = 'week';
  } else if(elapsed < year) {
    factor = month;
    unit = 'month';
  } else {
    factor = year;
    unit = 'year';
  }

  var value = Math.round(elapsed / factor)
  var plural = 's';
  
  if(value == 1) plural = ''
    
  return value + ' ' + unit + plural + ' ago'
}

function replace_time() {
  $('h3.date').each(function() {
    var el = $(this);
    el.text(time_difference(el.data('epoch')));
  });
}

replace_time()
