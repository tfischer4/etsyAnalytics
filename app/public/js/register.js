document.addEventListener("DOMContentLoaded", function() {

  // JavaScript form validation

  var checkPassword = function(str)
  {
    var re = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}$/;
    return re.test(str);
  };

  var checkForm = function(e)
  {
    if(document.getElementById("field_username").value == "") {
      alert("Error: Username cannot be blank!");
      document.getElementById("field_username").focus();
      e.preventDefault(); // equivalent to return false
      return;
    }
    re = /.{6,}/;
    if(!re.test(document.getElementById("field_username").value)) {
      alert("Error: Username must contain only letters, numbers and underscores!");
      document.getElementById("field_username").focus();
      e.preventDefault();
      return;
    }
    if(document.getElementById("field_pwd1").value != "" && document.getElementById("field_pwd1").value == document.getElementById("field_pwd2").value) {
      if(!checkPassword(document.getElementById("field_pwd1").value)) {
        alert("The password you have entered is not valid!");
        tdocument.getElementById("field_pwd1").focus();
        e.preventDefault();
        return;
      }
    } else {
      alert("Error: Please check that you've entered and confirmed your password!");
      document.getElementById("field_pwd1").focus();
      e.preventDefault();
      return;
    }
  };

  var myForm = document.getElementById("regForm");
  myForm.addEventListener("submit", checkForm, true);

  // HTML5 form validation

  var supports_input_validity = function()
  {
    var i = document.createElement("input");
    return "setCustomValidity" in i;
  }

  if(supports_input_validity()) {
    var usernameInput = document.getElementById("field_username");
    usernameInput.setCustomValidity(usernameInput.title);

    var pwd1Input = document.getElementById("field_pwd1");
    pwd1Input.setCustomValidity(pwd1Input.title);

    var pwd2Input = document.getElementById("field_pwd2");

    // input key handlers

    usernameInput.addEventListener("keyup", function() {
      usernameInput.setCustomValidity(this.validity.patternMismatch ? usernameInput.title : "");
    }, false);

    pwd1Input.addEventListener("keyup", function() {
      this.setCustomValidity(this.validity.patternMismatch ? pwd1Input.title : "");
      if(this.checkValidity()) {
        pwd2Input.pattern = this.value;
        pwd2Input.setCustomValidity(pwd2Input.title);
      } else {
        pwd2Input.pattern = this.pattern;
        pwd2Input.setCustomValidity("");
      }
    }, false);

    pwd2Input.addEventListener("keyup", function() {
      this.setCustomValidity(this.validity.patternMismatch ? pwd2Input.title : "");
    }, false);

  }

}, false);