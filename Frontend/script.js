// Code by Get Code Snippets - https://getcodesnippets.com/ 

jQuery(".form-tab-nav").on("click", function () {
    $(".form-tab-nav").removeClass("active");
    $(this).addClass("active");
    var dataId = $(this).data("id");
    $(".form-tab-content").removeClass("active");
    $("#" + dataId).addClass("active");
    if (dataId === "signup") {
      $(".form-title").html("<h2>Sign Up</h2>");
    } else {
      $(".form-title").html("<h2>Sign In</h2>");
    }
  });
