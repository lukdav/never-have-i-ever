$(document).ready(function () {
  $('.sidenav').sidenav({
    edge: "right"
  });
  $('.collapsible').collapsible();
});


document.getElementById("add_requirements").onclick = function () {

  var node = document.createElement("Li");
  var text = document.getElementById("new_requirements").value;
  var textnode = document.createTextNode(text);
  node.appendChild(textnode);
  document.getElementById("game_requirements").appendChild(node);
  document.getElementById("new_requirements").value="";
}

document.getElementById("add_rule").onclick = function () {

  var node = document.createElement("Li");
  var text = document.getElementById("new_rule").value;
  var textnode = document.createTextNode(text);
  node.appendChild(textnode);
  document.getElementById("game_rules").appendChild(node);
  document.getElementById("new_rule").value="";
}





// document.getElementById("add_rule").addEventListener("keydown", function (event) {
//   if (event.key == "Enter") {
//     submitGame();
//   }
