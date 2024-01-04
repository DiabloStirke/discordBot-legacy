
function editHandler(id, cancel=false) {
    if (!cancel) {
        $('.cancel-btn:visible').click()
    }
    const table_row = $('#tr-dc-' + id);
    const edit_form = $('#tr-edit-dc-' + id);
    table_row.prop('hidden', !cancel);
    edit_form.prop('hidden', cancel);
}

$('.edit-btn').each(function(idx, obj) {
    let id = $(obj).attr('id');
    id = id.replace("edit-btn-dc-", "")
    $(obj).click(function() {
        editHandler(id);
    });
});

$('.cancel-btn').each(function(idx, obj) {
    let id = $(obj).attr('id');
    id = id.replace("cancel-btn-dc-", "")
    $(obj).click(function() {
        editHandler(id, true);
    });
});