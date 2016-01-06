function foo() {console.log('start');#start
    
#endconsole.log('end');}

function foo() {console.log('start');#start #endconsole.log('end');}

function foo()
{console.log('start');#start

#endconsole.log('end');}

function foo() {console.log('start');#start
    ;
    if (true) {
        ;
    }
    else {
        pass
    }
    ;
#endconsole.log('end');}

function foo(a, b, c) {console.log('start');#start

#endconsole.log('end');}

(function foo() {console.log('start');#start

#endconsole.log('end');})();

(function foo() {console.log('start');#start
    var a = function () {console.log('start');#start #endconsole.log('end');};

    a();
#endconsole.log('end');})(null);

var dummy = {
    a: function () {console.log('start');#start #endconsole.log('end');},
    b: function b() {console.log('start');#start

    #endconsole.log('end');}
};

function foo() {console.log('start');#start
    function foo() {console.log('start');#start
        function foo() {console.log('start');#start

        #endconsole.log('end');}
    #endconsole.log('end');}
#endconsole.log('end');}

function foo(){console.log('start');#start 
    #end {console.log('end');return;}$
#endconsole.log('end');}

function foo(){console.log('start');#start
    function foo(){console.log('start');#start
        function foo(){console.log('start');#start
            #end {console.log('end');return 'ok';}$
        #endconsole.log('end');}
    #endconsole.log('end');}
    #end {console.log('end');return 1;}$
#endconsole.log('end');}

function foo(i){console.log('start');#start
    switch(i){
        case 0:
            #end {console.log('end');return;}$
        case 1:
            #end {console.log('end');return;}$
        case 2:
            #end {console.log('end');return;}$
    }
#endconsole.log('end');}

(function (){console.log('start');#start
    window.abc = window.abc||{};

    window.def.efg = {
        pp:function(){console.log('start');#start
            var e = function(){console.log('start');#start
                if(True){
                    #end {console.log('end');return;}$
                }
            #endconsole.log('end');}
        #endconsole.log('end');},
        dd:function(a){console.log('start');#start

        #endconsole.log('end');}
    };
#endconsole.log('end');});

(function () {console.log('start');#start

    var a = " function abc ";
    var b = "/* abcd */";
    var e = "// abcddefg";
    var f = "function (){def;";
    var r = /abcde\/defg/g;
    var regex_with_comment_start = /(>)(<)(\/*)/g;
    var regex_with_string = /","/g;
#endconsole.log('end');})();


function(){console.log('start');#start
    o.onevent({}).click(function(){console.log('start');#start #endconsole.log('end');});
#endconsole.log('end');}

(function () {console.log('start');#start

    var a = {

        g: function (x) {console.log('start');#start
            var a = n.f("''@xadfwerq]", xmlDocElement);
            #end {console.log('end');return x.map(function (actionStep) {console.log('start');#start
                #end {console.log('end');return x.getAttribute("actionName");}$
            #endconsole.log('end');});}$
        #endconsole.log('end');}
    };
#endconsole.log('end');})();

(function(){console.log('start');#start
    Object.apply(a, {
        n : function(i) {console.log('start');#start
            if (True) {
                a.s(i, "xxx", {
                }, function (response) {console.log('start');#start
                #endconsole.log('end');});
            }
        #endconsole.log('end');}
    });

#endconsole.log('end');})();

function (){console.log('start');#start
    var returnAbc = 0;
    if(true)
        #end {console.log('end');return 0;}$
    else
        #end {console.log('end');return 1;}$


    for(var i = 0; i < 10; i++)
        #end {console.log('end');return 0;}$

    while(False)
        #end {console.log('end');return;}$

    #end {console.log('end');return {
        a:b,
        c:function (){console.log('start');#start

        #endconsole.log('end');},
        def:{
            dummy:1,
            foo:function a(x){console.log('start');#start 
                #end {console.log('end');return x;}$
            #endconsole.log('end');}
        }
    }}$;
    #end {console.log('end');return 1==0%}
    var s = s.l.f().f(function(e) {console.log('start');#start #end {console.log('end');return e.id === "uid-lib-new-section";}$ #endconsole.log('end');});
    {#end {console.log('end');return e.id === "uid-record-section" %}}

    #end {console.log('end');return function(){console.log('start');#start 
        #end {console.log('end');return;}$
    #endconsole.log('end');}%}

    #end {console.log('end');return ab?
        def:
        gh;}$
    #end {console.log('end');return abc
    ? def:
      gh;}$
#endconsole.log('end');}
