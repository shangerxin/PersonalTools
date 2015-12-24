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
    #end return;
#end}

function foo(){#start
    function foo(){#start
        function foo(){#start
            #end return 'ok';
        #end}
    #end}
    #end return 1;
#end}

function foo(i){#start
    switch(i){
        case 0:
            #end return;
        case 1:
            #end return;
        case 2:
            #end return;
    }
#end}

(function (){#start
    window.abc = window.abc||{};

    window.def.efg = {
        pp:function(){#start
            var e = function(){#start
                if(True){
                    #end return;
                }
            #end}
        #end},
        dd:function(a){#start

        #end}
    };
#end});


