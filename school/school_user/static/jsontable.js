$('.test').click( function() {
  var table = $('#inventory').tableToJSON();
  console.log(table);
  alert(JSON.stringify(table));  
});