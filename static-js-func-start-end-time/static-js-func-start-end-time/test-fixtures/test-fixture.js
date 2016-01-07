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
    var s = s.l.f().f(function(e) {#start #end return e.id === "uid-lib-new-section";$ #end});
    {#end return e.id === "uid-record-section" %}

    #end return function(){#start 
        #end return;$
    #end};$

    #end return ab?
        def:
        gh;$
    #end return abc
    ? def:
      gh;$
#end}

(function () {#start
    "use strict";
	
    if(t){
        this.push({m: msg.id, cb: (function () {#start self.s(msg, id); #end})});
    }
#end});

(function() {#start
    t.("r", function() {#start
        tr("c", function(e) {#start
            if (s != f && !v("l")) {
                e.d("r", {}, { c: true, i: e.type, c: function () {#start
                    e.t.u();
                #end}});
            }
        #end}, true);

    #end}, true);

    toString : function() {#start #end return "sss" #end$}

    #end return this.endExecute(TC_NS.TestObject.RETCODE_INVALID_ARGUMENTS_RUNTIME,
    { args : args, arg : args["Text"] !== undefined && !validIndexes.length ? "Text" : "Ordinal" });$


    function(attrName) {#start #end return function() {#start
        #end return this.getAttribute(attrName);$ #end};$
    #end}

    #end return this.end(TC_NS.Step.RETCODE_FAILED, {
        extRetInfo : TC_NS.Step.EXT_RET_INFO_INVALID_ARGUMENTS,
        arguments : [ "Question List - " + TC_NS.Schema.ERROR_VALUE_LENGTH_BELOW_MIN ]
    });$

    #end return this.end(TC_NS.Step.RETCODE_ABORTED_FAILED, { originalErrorEvent : origErrEvent ,
        extRetInfo : e.retCode == TC_NS.Step.RETCODE_ABORTED_FAILED ?
            e.extRetInfo : TC_NS.Step.EXT_RET_INFO_ERROR_IN_ANOTHER_STEP } );$

    if (!this.firstChild.obj) { 
        #end return TC_NS.I10nUtils.linkAction(getL10NStrP('StepLabel.If2Wait/Empty Template', '<testObj notset="true">[object not set]</testObj>'))
    %}

    var isCandidate = function(obj) {#start
        if (this.expression && this.expression[0] && this.expression[0].descriptor)
            #end return this.expression[0].calc(obj, this.expression[0].descriptor)$
        #end return false;$
    #end}

    if (!isSuccess)
        #end return this.end(TC_NS.Step.RETCODE_FAILED, { extRetInfo : "Exception During Argument Evaluation",
            argName : "Condition", error : argVal });$

    get obj() {#start
        #end return this._obj;$
    #end}

    var transName = "\"" + content[i] + "\"";

    #end return function (func) {#start
        timeouts.push(func);
        window.postMessage(msgId, "*");
        #end}$
#end})();
