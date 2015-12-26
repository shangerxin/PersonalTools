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

(function () {#start

    var a = " function abc ";
    var b = "/* abcd */";
    var e = "// abcddefg";
    var f = "function (){def;";
#end})();


function(){#start
    $.onevent({}).click(function(){#start #end});
#end}

(function () {#start

    var a = {

        g: function (x) {#start
            var a = n.f("''@xadfwerq]", xmlDocElement);
            #end return x.map(function (actionStep) {#start
                #end return x.getAttribute("actionName");
            #end});
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


// (c) Copyright 2012 Hewlett-Packard Development Company, L.P.

(function () {
    "use strict";

    Object.extend(window.TC_NS.Utils, {
        generateUUID: function () {
            function S4() {
                return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
            }

            return "{".concat(S4(), S4(), "-", S4(), "-", S4(), "-", S4(), "-", S4(), S4(), S4(), "}");
        },

        isValidXPathExpr: function (expr) {
            try {
                document.createExpression(expr, null);
            } catch (ex) { 
                return false; 
            }
            return true;
        },

        loadScript: function (url, obj) {
        },

        setMouseHook: function (enable) {
            // done using the native code !
            return;
        },

        getBrowsers: function () {
            if (window.TC_NS.BrowserMgr) { // false in the agent...
                return TC_NS.BrowserMgr.browsers;
            }
            TC_NS.Log.error("Inside the agent you can not call the TC_NS.Utils.getBrowsers() method!");
            return [];
        },

        generateSnapshot: function (objRect, callback,drawWatermark) {
            chrome.tabs.captureVisibleTab(TC_NS.BrowserMgr.activeBrowserId, {format: "png" }, function (dataUrl) {
                if (chrome.runtime.lastError) {
                    // Exception will be raised when tab crashes(not process crashes), invoke callback with empty dataUrl
                    TC_NS.Log.error("Failed to generate snapshot. " + chrome.runtime.lastError.message);
                    callback && callback();
                    return;
                }

                if (objRect || drawWatermark){
                    var img = new Image();
                    img.onload = function() {			
                        var canvas = document.createElementNS("http://www.w3.org/1999/xhtml", "canvas"); //create element with namespace
                        var ctx = canvas.getContext("2d");
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);

                        if (objRect) {

                            ctx.fillStyle = "rgba(200, 0, 0, 0.2)";
                            ctx.fillRect(objRect.left, objRect.top, objRect.right - objRect.left, objRect.bottom - objRect.top);
                            ctx.strokeStyle = "rgb(255, 0, 0)";
                            ctx.strokeRect(objRect.left, objRect.top, objRect.right - objRect.left, objRect.bottom - objRect.top);
                        }

                        if (drawWatermark){
                            ctx.font="16px Arial";
                            ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
                            ctx.fillText("TruClient Chromium",20,20);
                        }
                        dataUrl = canvas.toDataURL();

                        callback && callback(dataUrl);
                        return;
                    }
                    img.src = dataUrl;
                }
                else {
                    callback && callback(dataUrl);
                }
            });
        },

        generateSnapshotNative: function(snapShotPath) {
            var request = {
                path: snapShotPath,
                callback: function (msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "generateSnapshot", "path": msg.path }, "res", function (response) { setResponse(response); });

                }.toString()
            };

            return TC_NS.Utils.commonSendSync(request);
        },

        generateIcon: function (obj, canvas) {},

        setMouseHover : function(obj) {},

        nodeToXml : function(node) {
            return (xmlSerializer.serializeToString(node));
        },

        formatXml: function (xml) {
            var reg = /(>)(<)(\/*)/g;
            var wsexp = / *(.*) +\n/g;
            var contexp = /(<.+>)(.+\n)/g;
            xml = xml.replace(reg, '$1\n$2$3');
            // xml = xml.replace(wsexp, '$1\n'); // comment out this line, because it doesn't do much and causes us to stuck in case of very long link(bug #84313)
            xml = xml.replace(contexp, '$1\n$2');
            var pad = 0;
            var formatted = '';
            var lines = xml.split('\n');
            var indent = 0;
            var lastType = 'other';
            // 4 types of tags - single, closing, opening, other (text, doctype, comment) - 4*4 = 16 transitions
            var transitions = {
                'single->single': 0,
                'single->closing': -1,
                'single->opening': 0,
                'single->other': 0,
                'closing->single': 0,
                'closing->closing': -1,
                'closing->opening': 0,
                'closing->other': 0,
                'opening->single': 1,
                'opening->closing': 0,
                'opening->opening': 1,
                'opening->other': 1,
                'other->single': 0,
                'other->closing': -1,
                'other->opening': 0,
                'other->other': 0
            };

            for (var i = 0; i < lines.length; i++) {
                var ln = lines[i];
                var single = Boolean(ln.match(/<.+\/>/)); // is this line a single tag? ex. <br />
                var closing = Boolean(ln.match(/<\/.+>/)); // is this a closing tag? ex. </a>
                var opening = Boolean(ln.match(/<[^!].*>/)); // is this even a tag (that's not <!something>)
                var type = single ? 'single' : closing ? 'closing' : opening ? 'opening' : 'other';
                var fromTo = lastType + '->' + type;
                lastType = type;
                var padding = '';

                indent += transitions[fromTo];
                for (var j = 0; j < indent; j++) {
                    padding += '\t';
                }
                if (fromTo == 'opening->closing')
                    formatted = formatted.substr(0, formatted.length - 1) + ln + '\n'; // substr removes line break (\n) from prev loop
                else
                    formatted += padding + ln + '\n';
            }

            return formatted;
        },	

        // Ga Ga Ga - Looking to see if obj is a Window without using instanceof (we are not in the same global context)
        isDuckWindow: function (obj) {
            return obj.alert && obj.document ? true : false;
        },
	
        handlerExistForObject: function (obj, type) {
            var types = type.split(/\s+/);
            if (obj.getAttribute === undefined) {
                if (obj.nodeType == 9) { // obj is a document
                    var docElement = obj.documentElement;
                    for (var i = 0; i < types.length; i++) {
                        var ret = obj["on" + types[i]]; // Check the document
                        if (ret) {
                            return true;
                        }
                        var attribName = 'hp_doc_trak_' + types[i];
                        var handlersNum = docElement.getAttribute(attribName); // Check the documentElement
                        if (Number(handlersNum)) {
                            return true;
                        }
                    }
                }
                return false;
            }
		
            for (var i = 0; i < types.length; i++) {
                var ret = obj.getAttribute("on" + types[i]);
                if (ret) {
                    return true;
                }
                var attribName = 'hp_trak_' + types[i];
                var handlersNum = obj.getAttribute(attribName);
                if (Number(handlersNum)) {
                    return true;
                }
            }
            return false;
        },
	

        commonSendSync: function(req){
            var request = req; // necessary for proper debugger execution
            var response = {};
            if (!local_TC_NS.isMain)
                local_TC_NS.Event.dispatch("TC.reportStartDelay", null, { startTime: new Date().getTime() });
            debugger;
            if (!local_TC_NS.isMain)
                local_TC_NS.Event.dispatch("TC.reportEndDelay", null, { endTime: new Date().getTime() });
            return response;
        },
	
        getProcessId: function() {
            if (processId)
                return processId;
			
            var request = {
                callback: function(msg){
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "getProcessId" },  "processId", function(response) { setResponse(response);});

                }.toString()
            };
		
            processId = TC_NS.Utils.commonSendSync(request); 
            return processId;
        },

        getChromeMainProcessId: function(){
            if (chromeMainProcessId){
                return chromeMainProcessId;
            }

            var request = {
                callback: function (msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "getChromeMainProcessId" }, "processId", function (response) { setResponse(response); });

                }.toString()
            };

            chromeMainProcessId = TC_NS.Utils.commonSendSync(request);
            return chromeMainProcessId;
        },
	
        getChromeExtensionProcessId: function(){
            if (chromeExtensionProcessId){
                return chromeExtensionProcessId;
            }

            var request = {
                callback: function (msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "getChromeExtensionProcessId" }, "processId", function (response) { setResponse(response); });

                }.toString()
            };

            chromeExtensionProcessId = TC_NS.Utils.commonSendSync(request);
            return chromeExtensionProcessId;
        },

        getRREVersion: function() {
            if (this.rreVersion)
                return this.rreVersion;

            var request = {
                versionFilePath: TC_NS.Ambiance.getStringVal("ExtensionRoot") + "\\RRE\\content",
                callback: function(msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "getRREVersion", versionFilePath: msg.versionFilePath },  "rreVersion", function(response) { setResponse(response);});
                }.toString()
            };

            this.rreVersion = TC_NS.Utils.commonSendSync(request);
            return this.rreVersion;
        },
    
        extendLoaderBaseUrlPath: function (baseUrlPath) {
            // Each browser should extend the base url path and give his own implementation 
            var baseFolder = TC_NS.Ambiance.getStringVal("ExtensionRoot");
            return baseFolder + baseUrlPath; // Remove ".." form the start which exist in IE browser specific loader
        },


        resizeAUTWindowNative: function(left, top, width, height) {
            var request = {
                left: left,
                top: top,
                width: width,
                height: height,
                callback: function(msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "resizeAUTWindow", "left": msg.left, "top": msg.top, "width": msg.width, "height": msg.height},  "res", function(response) { setResponse(response);});
                }.toString()
            };

            TC_NS.Utils.commonSendSync(request);
        },

        saveGlobalSettingsToRTS: function(){
            var request = {
                globalSettingsFilename: TC_NS.LRSettings.browserFilepath,
                isLoadMode: TC_NS.Ambiance.getBoolVal("LOAD_MODE"),
                scriptPath: TC_NS.Ambiance.getStringVal("SCRIPT_PATH"),
                callback: function(msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "saveGlobalSettingsToRTS", "globalSettingsFilename": msg.globalSettingsFilename, "isLoadMode" : msg.isLoadMode, "scriptPath" : msg.scriptPath},  "res", function(response) { setResponse(response);});
                }.toString()
            };


            TC_NS.Utils.commonSendSync(request);
        },

        setAuthPrompRegVal : function( val){
            var request = {
                val: val,
                callback: function(msg) {
                    TC_NS.NativeBridge.sendMsgAsync({ msgType: "setPromptUserPassRegistryValue", "val": msg.val},  "res", function(response) { setResponse(response);});
                }.toString()
            };

            TC_NS.Utils.commonSendSync(request);
        }

    });

    var xmlSerializer = new XMLSerializer();
    var processId = 0;
    var chromeMainProcessId = 0;
    var chromeExtensionProcessId = 0;

    var local_TC_NS = TC_NS;

})();
