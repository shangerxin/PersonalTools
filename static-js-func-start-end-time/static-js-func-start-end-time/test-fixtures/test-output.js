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
 console.log('end');  console.log('end'); #console.log('end');enconsole.log('end');d console.log('end');return;
#endconsole.log('end');}

function foo(){console.log('start');#start
    function foo(){console.log('start');#start
        function foo(){console.log('start');#start
 console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end'); #console.log('end');enconsole.log('end');d console.log('end');return 'ok';
        #endconsole.log('end');}
    #endconsole.log('end');}
 console.log('end');  console.log('end'); #console.log('end');enconsole.log('end');d console.log('end');return 1;
#endconsole.log('end');}

function foo(i){console.log('start');#start
    switch(i){
        case 0:
 console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end'); #console.log('end');enconsole.log('end');d console.log('end');return;
        case 1:
 console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end'); #console.log('end');enconsole.log('end');d console.log('end');return;
        case 2:
 console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end');  console.log('end'); #console.log('end');enconsole.log('end');d console.log('end');return;
    }
#endconsole.log('end');}


