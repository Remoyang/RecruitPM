$(function () {
    layui.use('form', function () {
        var form = layui.form;
        //监听提交
        form.on('submit(login)', function (data) {
            $.ajax({
                method: "POST",
                url: "/api/v1.0/sessions",
                contentType: 'application/json',
                data: JSON.stringify(data.field),
                success: function (res) {
                    console.log(res);
                    if (res.code == "0") {
                        location.href = '/index.html'
                    } else {
                        layer.msg(res.errmsg, {icon: 5})
                    }
                }});
            return false;
        });
    });
});
