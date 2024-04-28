$(document).ready(function () {

  $('#upload-container').click(function () {
    $('.upload-container').show();
    $('.text-container').hide();
    $('.sd-container').hide();
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
  });

  $('#text-container').click(function () {
    $('.upload-container').hide();
    $('.text-container').show();
    $('.sd-container').hide();
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
  });

  $('#sd-container').click(function () {
    $('.upload-container').hide();
    $('.text-container').hide();
    $('.sd-container').show();
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
  });
});

function dropHandler(event) {
  event.preventDefault();
  var file = event.dataTransfer.files[0];
  var form = new FormData();
  form.append('file', file);
  uploadFile(form);
}

function uploadHandler(event) {
  event.preventDefault();
  var file = event.target.files[0];
  var form = new FormData();
  form.append('file', file);
  uploadFile(form);
}

uploadFile = function (form) {
  $.ajax({
    url: '/upload',
    type: 'POST',
    data: form,
    cache: false,
    contentType: false,
    processData: false,
    success: function (data) {
      $(document).find('body').html(data);
      console.log('upload success');
    }
  });
}