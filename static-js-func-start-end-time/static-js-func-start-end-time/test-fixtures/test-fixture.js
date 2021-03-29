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
            #end return x.map(function (actiont) {#start
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
    };$
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

    #end return this.endExecute(n.o.r,
    { args : args, arg : args["Text"] !== undefined && !validIndexes.length ? "Text" : "Ordinal" });$


    function(attrName) {#start #end return function() {#start
        #end return this.getAttribute(attrName);$ #end};$
    #end}

    #end return this.end(n.t.RETCODE_FAILED, {
        extRetInfo : n.t.e,
        arguments : [ "Question List - " + n.s.e ]
    });$

    #end return this.end(n.t.r, { originalErrorEvent : origErrEvent ,
        extRetInfo : e.retCode == n.t.r ?
            e.extRetInfo : n.t.EXT_RET_INFO_ERROR_IN_ANOTHER_t } );$

    if (!this.firstChild.obj) { 
        #end return n.I10nUtils.linkAction(getL10NStrP('tLabel.If2Wait/Empty Template', '<t="true">[s]</t>'))
$    }

    var isCandidate = function(obj) {#start
        if (this.e && this.e[0] && this.e[0].descriptor)
            #end return this.e[0].calc(obj, this.e[0].descriptor)
$        #end return false;$
    #end}

    if (!isSuccess)
        #end return this.end(n.t.RETCODE_FAILED, { extRetInfo : "Exception During Argument Evaluation",
            argName : "Condition", error : argVal });$

    get obj () {#start
        #end return this._obj;$
    #end}

    set obj(v) {#start
        #end return this._obj;$
    #end}

    var transName = "\"" + content[i] + "\"";

    #end return function (func) {#start
        timeouts.push(func);
        window.postMessage(msgId, "*");
        #end}
$#end})();


function(){#start
    var h = function(e) {#start
        #end return n.t(n.o.g(), "Add Tab", 
            e.uri != 'about:blank' ?  { "Location" : e.uri } : null);$ #end}

    if (this.getAttribute("catch"))
        #end return n.I10nUtils.genMarkup('Catch', String(this.getUnevaledArg("Error Type") || '"Any"').xmlEncode(), 'Error Type')
$    else (this.section)
        #end return "Section <action>".concat(this.section.xmlEncode(), "</action>");$

        
    {	description	: "Generate 'Add Tab' on browsers",
        selector	: null,
        eventTypes	: "browser/addTab",
        handler		: function(e) {#start 
            #end return n.t(n.o.g(), "Add Tab", 
				e.uri != 'about:blank' ?  { "Location" : e.uri } : null);$ #end}
    }
#end}

function(){#start
    #end return n.find("xpath:string(ancestor::t[@type='library']/@action)", this)[0] ||
    n.find("xpath:string((ancestor::t[@actionName])[last()]/@actionName)", this)[0];$

    #end return n.find('xpath:descendant::*[translate(string(@id), "0123456789", "")="'
				+ this._noNumberId.replace(/"/g, '&quot;') + '"]', ctx);$

    #end return this.createCompunde(obj, 
					[
						{p: "pathname", op: "equalsIgnoreDigits"}, 
						{p: "protocol", op: "equalsIgnoreCase"}, 
						{p: "host", op: "equalsIgnoreCase"},
						{p: "url", op: "equalsIgnoreDigits"}
					]);$

    #end return "<action>Call </action>action <arg name='Action Name'>".concat(
				String(this.getUnevaledArg("Condition") || "").xmlEncode(),
				"</arg>");$

    #end return (d && d[s] && 
				d[s][keyName] &&
				d[s][keyName].value) || defaultValue;$

    #end return [
			tEditorSectionSettings_tAttr,
			tEditorSectionSettings_arg,
			tEditorSectionSettings_obj,
			tEditorSectionSettings_trans
    ];$

    #end return n.find("xpath:normalize-space(descendant::" + this.value.tagName + "[1])", obj)[0]
				== this.value.text ? 0.3 : 0;$
#end}