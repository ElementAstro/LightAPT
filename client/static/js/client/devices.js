/*
 * Copyright(c) 2022-2023 Max Qian
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */

// ----------------------------------------------------------------
// Basic Interface
// ----------------------------------------------------------------

/**
 * Print Error Messages In Screen 
 * @param {string} _err
 */
function onError(_err) {
    $("#errorMessage").text(_err);
    $("#centralModalDanger").modal("show");
}

/**
 * Hide message modal
 */
function onErrorHide() {
    $("#centralModalDanger").modal("hide");
}

/**
 * Double check for better safety
 */
function onWarning() {
    $("#centralModalDanger").modal("show");
}

/**
 * Hide the warning message
 */
function onWarningHide() {
    $("#centralModalDanger").modal("hide");
}

/**
 * Print Normal Messages
 * @param {string} _info
 */
function onInfo(_info) {
    $("#infoModalMessage").text(_info);
    $("#infoModalGeneric").modal("show");
}

/**
 * Hide the modal message at a proper time
 */
function onInfoHide(){
    setTimeout(function () {
        $("#infoModalGeneric").modal("hide");
    }, 600);
}

/**
 * Tiny single line logging system
 * @param {string} msg 
 */
function logText(msg){
    $("#generalLogText").text(msg)
}

// ----------------------------------------------------------------
// Event handlers on loading finished
// ----------------------------------------------------------------

var ready=callback=>{
    "loading"!=document.readyState?callback():document.addEventListener("DOMContentLoaded",callback)
};

ready(()=>{
    // We need to run this function to check if the server is ready started.
    getStatus();
    // Bind events with server_command
    document.getElementById("server_command").addEventListener("click", toggle_server)
    // Bind events with client_command , NOTE : This client does not mean INDI client,
    // this is connecting to another standalone server as a better INDI interface
    // If you are using ASCOM as your server , just avoid this .
    // Before the INDI server is started , we can not connect to client
    $('#client_command').addClass("disabled");
    document.getElementById("client_command").addEventListener("click", toggle_client)
});

// ----------------------------------------------------------------
// Device Hub Interface
// ----------------------------------------------------------------

/**
 * Start or stop the server and all of the drivers that started by this server
 */
function toggle_server(){
    var status = $.trim($("#server_command").text());
    if (status == "启动" || status == "start" || status == "Start") {
        onInfo("连接中,请稍后...")
        $.ajax({
            type: 'POST',
            url: "/devices/api/start",
            contentType: "application/json; charset=utf-8",
            data : JSON.stringify({
                camera : $("#camera").val(),
                telescope : $("#telescope").val(),
                focuser : $("#focuser").val(),
                filterwheel : $("#filterwheel").val(),
                solver : $("solver").val(),
                guider : $("#guider").val(),
                plugins : $("#plugins").val()
            }),
            success: function () {
                onInfoHide();
                getStatus();
            },
            error: function () {
                onInfoHide();
                onError("启动设备失败");
            }
        });
    } else {
        $.ajax({
            type: 'GET',
            url: "/devices/api/stop",
            success: function () {
                getStatus();
            },
            error: function () {
                onError("停止设备失败")
            }
        });
    }
};

/**
 * Get the status of the server 
 */
function getStatus() {
    $.getJSON("/devices/api/status", function (data) {
        if (data.status == "True")
            getActiveDrivers();
        else {
            $("#server_command").html("<i class='fas fa-light-switch-on'></i> 启动");
            $("#server_notify").html("<p class='alert alert-info'>服务器空闲中</p>");

            $("#server_command").removeClass('btn-outlinedanger');
            $("#server_command").addClass('btn-outline-primary');
        }
    });
};

/**
 * Get all of the active drivers and modifiers html whit a success symbol
 */
function getActiveDrivers() {
    $.getJSON("/devices/api/drivers", function (data) {
        $("#server_command").html("<i class='fas fa-close'></i> 停止");
        $("#server_command").addClass('btn-outline-info');
        $("#server_command").removeClass('btn-outline-danger');

        $("#server_notify").html("<p class='alert alert-info'>设备启动成功！</p>");

        $("#client_command").removeClass("disabled");
    })
};

// ----------------------------------------------------------------
// Websocket Connection Options
// ----------------------------------------------------------------

var websocket;
var is_connected = false;

/**
 * Toggles the client connection.
 * This function is used to set up a websocket connection with the server.
 * The server is built-in and not INDI server at all.
 */
function toggle_client(){
    var status = $.trim($("#client_command").text());
    if (status == "连接" || status == "start" || status == "Start") {
        // Create a new websocket connection
        websocket = new WebSocket("ws://localhost:5000")
        websocket.onopen = function(event) {on_open(event)}
        websocket.onclose = function(event) {on_close(event)}
        websocket.onmessage = function(event) {on_message(event)}
        websocket.onerror = function(event) {on_error(event)}
    }else{
        websocket.close()
    }
};

/**
 * Wesocket On open event
 * @param {*} event 
 */
function on_open(event) {
    is_connected = true;
    $("#client_command").html("<i class='fas fa-close'></i> 断连");
    $("#client_notify").html("<p class='alert alert-info'>与服务器建立连接</p>");
    SendRemoteDashboardSetup();
}

/**
 * Websocket On close event
 * @param {*} event 
 */
function on_close(event) {
    is_connected = false;
    $("#client_command").html("<i class='fas fa-link'></i> 连接");
    $("#client_notify").html("<p class='alert alert-warning'>暂无连接</p>");
}

/**
 * Websocket On message event
 * When a message is received , first we will check if the message format is JSON
 * and if it is correct , the parser_json() will be called to parse the message
 * @param {*} event 
 */
function on_message(event) {
    try{
        var message = JSON.parse(event.data.replace(/\bNaN\b/g,"null"))
    }
    catch(e){
        console.error("Not a valid JSON message : " + e)
    }
    "RemotePolling" !== message.event && parser_json(message)
}

/**
 * Websocket On error event
 * @param {*} event 
 */
function on_error(event) {
    console.debug("websocket error")
    onError("Websocket连接错误")
}

/**
 * Send message to the websocket server
 * @param {string} message
 */
function on_send(message){
    // send message to server
    console.debug("send message : " + message)
    if(is_connected){
        websocket.send(message + "\r\n")
    }
}

// ----------------------------------------------------------------
// Websocket event handlers
// ----------------------------------------------------------------

function SendRemoteDashboardSetup(){
    // Send setup command to remote server
    let request = {
        event: "RemoteDashboardSetup",
        params : {}
    }
    on_send(JSON.stringify(request))
}


// ----------------------------------------------------------------
// Image Viewer
// ----------------------------------------------------------------

window.onload = function () {
    'use strict';

    var Viewer = window.Viewer;
    var console = window.console || { log: function () { } };
    var pictures = document.querySelector('.docs-pictures');
    var toggles = document.querySelector('.docs-toggles');
    var buttons = document.querySelector('.docs-buttons');
    var options = {
        // inline: true,
        url: 'data-original',
        ready: function (e) {
        },
        show: function (e) {
        },
        shown: function (e) {
        },
        hide: function (e) {
        },
        hidden: function (e) {
        },
        view: function (e) {
        },
        viewed: function (e) {
        },
        move: function (e) {
        },
        moved: function (e) {
        },
        rotate: function (e) {
        },
        rotated: function (e) {
        },
        scale: function (e) {
        },
        scaled: function (e) {
        },
        zoom: function (e) {
        },
        zoomed: function (e) {
        },
        play: function (e) {
        },
        stop: function (e) {
        }
    };
    var viewer = new Viewer(pictures, options);

    function toggleButtons(mode) {
        var targets;
        var target;
        var length;
        var i;

        if (/modal|inline|none/.test(mode)) {
            targets = buttons.querySelectorAll('button[data-enable]');

            for (i = 0, length = targets.length; i < length; i++) {
                target = targets[i];
                target.disabled = true;

                if (String(target.getAttribute('data-enable')).indexOf(mode) > -1) {
                    target.disabled = false;
                }
            }
        }
    }
};