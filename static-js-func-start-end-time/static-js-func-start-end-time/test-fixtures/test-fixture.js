function foo() {#start
    
#end}

function foo() {#start #end}

function foo()
{#start

#end}

function foo() {#start
    ;
    if (true) {
        ;
    }
    else {
        pass
    }
    ;
#end}

function foo(a, b, c) {#start

#end}

(function foo() {#start

#end})();

(function foo() {#start
    var a = function () {#start #end};

    a();
#end})(null);

var dummy = {
    a: function () {#start #end},
    b: function b() {#start

    #end}
};

function foo() {#start
    function foo() {#start
        function foo() {#start

        #end}
    #end}
#end}

function foo(){#start 
    #end return;$
#end}

function foo(){#start
    function foo(){#start
        function foo(){#start
            #end return 'ok';$
        #end}
    #end}
    #end return 1;$
#end}

function foo(i){#start
    switch(i){
        case 0:
            #end return;$
        case 1:
            #end return;$
        case 2:
            #end return;$
    }
#end}

(function (){#start
    window.abc = window.abc||{};

    window.def.efg = {
        pp:function(){#start
            var e = function(){#start
                if(True){
                    #end return;$
                }
            #end}
        #end},
        dd:function(a){#start

        #end}
    };
#end});

(function () {#start

    var a = " function abc ";
    var b = "/* abcd */";
    var e = "// abcddefg";
    var f = "function (){def;";
    var r = /abcde\/defg/g;
    var regex_with_comment_start = /(>)(<)(\/*)/g;
    var regex_with_string = /","/g;
    /**** /comment contain regex statements/ ***/
#end})();


function(){#start
    o.onevent({}).click(function(){#start #end});
#end}

(function () {#start

    var a = {

        g: function (x) {#start
            var a = n.f("''@xadfwerq]", xmlDocElement);
            #end return x.map(function (actionStep) {#start
                #end return x.getAttribute("actionName");$
            #end});$
        #end}
    };
#end})();

(function(){#start
    Object.apply(a, {
        n : function(i) {#start
            if (True) {
                a.s(i, "xxx", {
                }, function (response) {#start
                #end});
            }
        #end}
    });

#end})();

function (){#start
    var returnAbc = 0;
    if(true)
        #end return 0;$
    else
        #end return 1;$


    for(var i = 0; i < 10; i++)
        #end return 0;$

    while(False)
        #end return;$

    #end return {
        a:b,
        c:function (){#start

        #end},
        def:{
            dummy:1,
            foo:function a(x){#start 
                #end return x;$
            #end}
        }
    }$;
    #end return 1==0%
    var s = s.l.f().f(function(e) {#start #end return e.id === "uid-lib-new-section";$ #end});
    {#end return e.id === "uid-record-section" %}

    #end return function(){#start 
        #end return;$
    #end}%

    #end return ab?
        def:
        gh;$
    #end return abc
    ? def:
      gh;$
#end}
