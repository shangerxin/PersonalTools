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
    #end console.log('end');return;
#endconsole.log('end');}

function foo(){console.log('start');#start
    function foo(){console.log('start');#start
        function foo(){console.log('start');#start
            #end console.log('end');return 'ok';
        #endconsole.log('end');}
    #endconsole.log('end');}
    #end console.log('end');return 1;
#endconsole.log('end');}

function foo(i){console.log('start');#start
    switch(i){
        case 0:
            #end console.log('end');return;
        case 1:
            #end console.log('end');return;
        case 2:
            #end console.log('end');return;
    }
#endconsole.log('end');}

(function (){console.log('start');#start
    window.abc = window.abc||{};

    window.def.efg = {
        pp:function(){console.log('start');#start
            var e = function(){console.log('start');#start
                if(True){
                    #end console.log('end');return;
                }
            #endconsole.log('end');}
        #endconsole.log('end');},
        dd:function(a){console.log('start');#start

        #endconsole.log('end');}
    };
#endconsole.log('end');});

(function () {console.log('start');#start

    var a = " function abc ";
#endconsole.log('end');})();


function(){console.log('start');#start
    $.onevent({}).click(function(){console.log('start');#start #endconsole.log('end');});
#endconsole.log('end');}

(function () {

    var LoadRunnerRunLogicUtils = {

        getActionsArray: function (xmlDocElement) {
            var actionSteps = TC_NS.find("xpath:descendant-or-self::step[@action='action' and @actionName!='']", xmlDocElement);
            return actionSteps.map(function (actionStep) {
                return actionStep.getAttribute("actionName");
            });
        }
    };
})();


