var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'))
var collapseList = collapseElementList.map(function (collapseEl) {
  return new bootstrap.Collapse(collapseEl)
})

var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'))
var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
  return new bootstrap.Dropdown(dropdownToggleEl)
})

function submit_No_Button() {
    document.getElementById ("submitNoButton").submit();
}

function submit_post_delete(posts_hex_cd) {
    document.getElementById ("delete_" + posts_hex_cd).submit();
}

function link_copy_Function(mask) {
  /* Get the text field */
    var link = mask + "_link";
    var copyText = document.getElementById(link);

  /* Select the text field */
    copyText.select();
    copyText.setSelectionRange(0, 99999); /* For mobile devices */

   /* Copy the text inside the text field */
    navigator.clipboard.writeText(copyText.value);

  /* Alert the copied text */
    const toastTrigger = document.getElementById(mask)
    const toastLiveExample = document.getElementById('liveToast')

    const toast = new bootstrap.Toast(toastLiveExample)
    toast.show()
}

function select_collapse_Function() {
    var select_form = document.getElementById("select_form");
    var text_post_Collapse = new bootstrap.Collapse(document.getElementById("text_post_collapse"), {toggle: false});
    var text_form_El = document.getElementById("text_content")
    var media_post_Collapse = new bootstrap.Collapse(document.getElementById("media_post_collapse"), {toggle: false});
    var media_form_El = document.getElementById("file_content")
    var shared_link_post_Collapse = new bootstrap.Collapse(document.getElementById("shared_link_post_collapse"), {toggle: false});
    var shared_link_form_El = document.getElementById("link_content")
    var form_El = document.getElementById("post_form")
    var file_confirm_El = document.getElementById("file_confirm")

    switch (select_form.value) {
        case "text_post":
            text_post_Collapse.show();
            media_post_Collapse.hide();
            shared_link_post_Collapse.hide();
            text_form_El.disabled = false;
            media_form_El.disabled = true;
            shared_link_form_El.disabled = true;
            file_confirm_El.disabled = true;
            form_El.enctype = "application/x-www-form-urlencoded";
            break;
        case "media_post":
            media_post_Collapse.show();
            shared_link_post_Collapse.hide();
            text_post_Collapse.hide();
            media_form_El.disabled = false;
            text_form_El.disabled = true;
            shared_link_form_El.disabled = true;
            file_confirm_El.disabled = false;
            form_El.enctype = "multipart/form-data";
            break;
        case "shared_link_post":
            shared_link_post_Collapse.show();
            media_post_Collapse.hide();
            text_post_Collapse.hide();
            shared_link_form_El.disabled = false;
            text_form_El.disabled = true;
            media_form_El.disabled = true;
            file_confirm_El.disabled = true;
            form_El.enctype = "application/x-www-form-urlencoded";
            break;
        default:
            alert("Error");
    }
}

function video_player_Function(mask) {

    const video_id = document.getElementById("video_" + mask);
    const content_collapse = document.getElementById("multiCollapseExample_" + mask);
    const icon_change = document.getElementById("video_svg_" + mask);

    content_collapse.addEventListener('shown.bs.collapse', event => {
        video_id.play();
    })

    content_collapse.addEventListener('hidden.bs.collapse', event => {
        video_id.pause();
    })

}