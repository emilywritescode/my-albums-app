$(function(){
        $('#insertBtn').click(function(){               
                $.ajax({
                        url : '/insertrecord',
                        data : $('#insertform').serialize(),
                        type : 'POST',
                        success : function(response) {
                                console.log(response);
                        },
                        error : function(error){
                                console.log(error);
                        }
                });
        });

});
