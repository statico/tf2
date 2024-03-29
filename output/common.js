$(function() {

  var b = $(document.body);
  if (/Android|iPhone/.test(navigator.userAgent)) {
    b.addClass('mobile');
  }
  var w = $(window);
  w.on('resize', function() {
    if (w.width() < 800)
      b.addClass('mobile');
    else
      b.removeClass('mobile');
  });

  var div = $(
    '<div id="calculator">' +
    '<table>' +
      '<tr><th>ref</th><td><input type="text" class="ref"/></td></tr>' +
      '<tr><th>key</th><td><input type="text" class="key"/></td></tr>' +
      '<tr><th>bill</th><td><input type="text" class="bill"/></td></tr>' +
      '<tr><th>bud</th><td><input type="text" class="bud"/></td></tr>' +
      '<tr><th>cc</th><td><input type="text" class="cc"/></td></tr>' +
      '<tr><th>US$</th><td><input type="text" class="usd"/></td></tr>' +
    '</table>' +
    '</div>'
  );

  function do_calc(field, ref) {
    var key = ref / key_price;
    var bill = ref / (bill_price * key_price);
    var bud = ref / (bud_price * key_price);
    var usd = bud * bud_dollars; // seems low?
    var cc = key * key_credits;
    if (field !== 'ref') div.find('.ref').val(ref.toFixed(2));
    if (field !== 'key') div.find('.key').val(key.toFixed(2));
    if (field !== 'bill') div.find('.bill').val(bill.toFixed(2));
    if (field !== 'bud') div.find('.bud').val(bud.toFixed(2));
    if (field !== 'usd') div.find('.usd').val(usd.toFixed(2));
    if (field !== 'cc') div.find('.cc').val(Math.ceil(cc));
  }

  function val(el) {
    return parseFloat($(el).val(), 10) || parseInt($(el).val(), 10);
  }

  div.on('keyup', '.ref', function() {
    do_calc('ref', val(this));
  });
  div.on('keyup', '.key', function() {
    do_calc('key', val(this) * key_price);
  });
  div.on('keyup', '.bill', function() {
    do_calc('bill', val(this) * key_price * bill_price);
  });
  div.on('keyup', '.bud', function() {
    do_calc('bud', val(this) * key_price * bud_price);
  });
  div.on('keyup', '.usd', function() {
    do_calc('usd', val(this) / bud_dollars * key_price * bud_price);
  });
  div.on('keyup', '.cc', function() {
    do_calc('cc', val(this) / key_credits * key_price);
  });

  div.appendTo(document.body);
  do_calc(null, key_price);

  $(document).on('click', '.name', function() {
    var query = $(this).text();
    window.open('http://wiki.teamfortress.com/w/index.php?title=Special%3ASearch&go=Go&search=' + query, '_blank');
    //window.open('https://www.google.com/search?q=site%3Ahttp%3A%2F%2Fbackpack.tf%2Fvote%2F+"Price+Suggestion"+' + query);
  });

});

