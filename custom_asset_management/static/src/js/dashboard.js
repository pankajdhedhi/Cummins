odoo.define('custom_asset_management.Dashboard',function(require){
"use strict";

var AbstractAction = require('web.AbstractAction');
//var ajax = require('web.ajax');
var core = require('web.core');
//var Dialog = require('web.Dialog');
//var field_utils = require('web.field_utils');
var session = require('web.session');
//var web_client = require('web.web_client');
var Widget = require('web.Widget');
var rpc = require('web.rpc');

var _t = core._t;
var QWeb = core.qweb;

var Dashboard = AbstractAction.extend({
    hasControlPanel: true,
    contentTemplate: 'custom_asset_management.Dashboard',

    events: {
        'click .list-click': 'onclick_list',
        'click .count-box': 'onclick_box',
        'change .tech_user': 'on_change_filter',
        'change .plants': 'on_change_filter',
        'change .state': 'on_change_filter',
        'change .work_centers': 'on_change_filter',
        'change .period': 'on_change_filter',
        'click .zoom': 'on_change_filter',
    },
//    jsLibs: [
//        '/web/static/lib/Chart/Chart.js',
//    ],

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboard_asset_templates = ['custom_asset_management.dashboard_view'];
        //this.list_order_template = ['custom_asset_management.assets'];
        this.js_domain = null;
    },
    willStart: function() {
        var self = this;
        this._super.apply(this, arguments)
            return self.fetch_data();
    },

    start: function() {
        var self = this;
        self.render_dashboards();
        $(self.$el).find('.o_content').css("background", "url(/custom_asset_management/static/description/img/cummins_dashboard.jpg)");
        $(self.$el).find('.o_content').css("background-size", "100%");
        $(self.$el).find('.o_content').css("background-repeat", "no-repeat");
        return this._super();
    },

    fetch_data: function() {
        var self = this;
        var prom = this._rpc({
            route: '/asset/fetch/dashboard',
        });
        prom.then(function(result) {
            self.order_ids = result['order_ids'];
            self.users = result['users'];
            self.plants = result['plants'];
            self.plant_ids = result['plant_ids']
            //self.order_user_inprogress = result['order_user_inprogress'];
            //self.order_user_complete = result['order_user_complete'];

            self.order_user_created = result['order_user_created'];
            self.order_user_assign = result['order_user_assign'];
            self.order_user_validate = result['order_user_validate'];
            self.order_user_inprogress = result['order_user_inprogress'];
            self.order_user_apporve = result['order_user_apporve'];
            self.order_user_close = result['order_user_close'];
            self.order_user_reject = result['order_user_reject'];

            self.order_total = result['order_total']
            self.order_created = result['order_created']
            self.order_assigned = result['order_assigned']
            self.order_inprocess = result['order_inprocess']
            self.order_validate = result['order_validate']
            self.order_apporve = result['order_apporve']
            self.order_closed = result['order_closed']
            self.order_reject = result['order_reject']

            self.is_not_local_finance = result['is_not_local_finance']
            self.work_centers = result['work_centers']
            self.sel_day = result['sel_day_str']
            self.sel_plant = result['sel_plant_str']
            self.dash_init = result['dash_init']
            // Assets
            self.asset_total = result['asset_total']
            self.verified_asset = result['verified_asset']
            self.pending_asset = result['asset_total'] - result['verified_asset']
        });
        return prom;
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboard_asset_templates, function(template) {
            self.$('.o_dashboard_stage').append(QWeb.render(template, {widget: self}));
        });
        _.each(this.list_order_template, function(template) {
            self.$('.o_dashboard_value').append(QWeb.render(template, {widget: self}));
        });

        self.render_dashboard_chart(self.order_user_created, "Created", "#chart_created");
        self.render_dashboard_chart(self.order_user_assign, "Assign", "#chart_assign");
        self.render_dashboard_chart(self.order_user_validate, "Completed", "#chart_validate");
        self.render_dashboard_chart(self.order_user_inprogress, "In-Progress", "#chart_in_progress");
        self.render_dashboard_chart(self.order_user_apporve, "Approved", "#chart_apporve");
        self.render_dashboard_chart(self.order_user_close, "Close", "#chart_close");
        self.render_dashboard_chart(self.order_user_reject, "Reject", "#chart_reject");
    },

    render_dashboard_chart: function(order_user, name, template){
        var self = this;
        const DATA_COUNT = 7;
        let keys = Object.keys(order_user);
        let value_data = Object.values(order_user);
        const NUMBER_CFG = {count: DATA_COUNT, min: 1, max: 100};
        
        var backgroundColor = new Array();
        var borderColor = new Array();
        for (var i=0;i<keys.length;i++){
            var r = Math.floor(Math.random() * 255);
            var g = Math.floor(Math.random() * 255);
            var b = Math.floor(Math.random() * 255);
            backgroundColor.push("rgb(" + r + "," + g + "," + b + ")");
            borderColor.push("rgb(" + r + "," + g + "," + b + ")");
        }
        
        const labels = keys;
        const data = {
            labels: labels,
            datasets: [
                {
                    label: 'User vs Assigned Orders (' + name +')',
                    data: value_data,
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
                    borderWidth: 1
                },
            ]
        };
        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Assets Orders'
                    }
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            stepSize: 1,
                            beginAtZero:true
                        }
                    }]
                }
            },
        };
        //var chart = new Chart(self.$('.o_dashboard_value').find(template), config);
    },

    // Filter Code
    on_change_filter: function (ev){
        var self = this;

        var $link = $('.zoom');
        if (ev.currentTarget.firstElementChild && ev.currentTarget.firstElementChild.firstElementChild){
            state = ev.currentTarget.firstElementChild.firstElementChild.innerText;
        }
        var tech_user = $(".tech_user option:selected").val();
        var plants = $(".plants option:selected").val();
        var state = $(".state option:selected").val();
        var work_centers = $(".work_centers option:selected").val();
        var period = $(".period option:selected").val();
        
        rpc.query({
            model: 'order.order',
            method: 'get_dashboard_filter_data',
            args: [1, tech_user, plants, state, work_centers, period],
        }).then(function( value ){
            self.data = value;
            _.each(self.list_order_template, function(template) {
                self.$('.o_dashboard_value').html(QWeb.render(template, {widget: value}));
            });
            _.each(self.dashboard_asset_templates, function(template) {
                self.js_domain = value['js_domain']
                self.assets_js_domain = value['assets_js_domain']
                self.$('.o_dashboard_stage').html(QWeb.render(template, {widget: value}));
            });
            //self.render_dashboard_chart(self.data.order_user_inprogress, "In-Progress", "#chart_in_progress");
            //self.render_dashboard_chart(self.data.order_user_complete, "Completed", "#chart_complete");

            self.render_dashboard_chart(self.order_user_created, "Created", "#chart_created");
            self.render_dashboard_chart(self.order_user_assign, "Assign", "#chart_assign");

            self.render_dashboard_chart(self.order_user_validate, "Completed", "#chart_validate");
            self.render_dashboard_chart(self.order_user_inprogress, "In-Progress", "#chart_in_progress");

            self.render_dashboard_chart(self.order_user_apporve, "Approved", "#chart_apporve");
            self.render_dashboard_chart(self.order_user_close, "Close", "#chart_close");

            self.render_dashboard_chart(self.order_user_reject, "Reject", "#chart_reject");
        });
    },

    onclick_list: function (ev){
        var self = this;
        var id;
        var $link = $('.zoom');
        // if (ev.currentTarget){
        //  id = ev.currentTarget.innerText;
        // }
        id = Number($(ev.currentTarget).data('order_id'))
        self.do_action({
            name: 'Orders',
            views: [[false, 'form']],
            domain: [["id", "=", id]],
            res_id: id,
            view_mode: 'form',
            res_model: 'order.order',
            type: 'ir.actions.act_window',
            target: 'current',
        });
//        return {
//                type: 'ir.actions.act_window',
//                name: _t('Employee Termination'),
//                res_model: 'order.order',
//                views: [[false, 'form']],
//                domain: [["id", "=", name]],
//                view_mode: 'form',
//                target: 'new',
//                context: {
//                    'active_id': name,
//                    'toggle_active': true,
//                }
//                }

    },

    onclick_box: function (ev){
        var self = this;
        var stage_name;
        var state = '';
        var $link = $('.zoom');
        if (ev.currentTarget.firstElementChild && ev.currentTarget.firstElementChild.firstElementChild){
            stage_name = ev.currentTarget.firstElementChild.firstElementChild.innerText;
        }
        console.log('-------------',self.assets_js_domain)
        console.log('-------------',self.js_domain)
        var meged_domain = new Array();
        state = stage_name//.toLowerCase();

        if ($.trim(state) == 'Total Order'){
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[0] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[1] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[0].includes('plant_id')){
                        meged_domain[0][2] = parseInt(meged_domain[0][2])
                    } else if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[0][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[0] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[1] = js_domain
                }
            }
            console.log(' DOMANI ', meged_domain)
            self.do_action({
                name: 'Total Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }

        if ($.trim(state) == 'Closed Order'){
            meged_domain[0] = ['state', '=', 'close']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Closed Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }

        if ($.trim(state) == 'Inprogress Order'){
            meged_domain[0] = ['state', '=', 'inprogress']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Inprogress Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }

        if ($.trim(state) == 'Completed Order'){
            meged_domain[0] = ['state', '=', 'validate']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Completed Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }

        if ($.trim(state) == 'Assigned Order'){
            meged_domain[0] = ['state', '=', 'assign']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Assigned Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }
        if ($.trim(state) == 'Created Order'){
            meged_domain[0] = ['state', '=', 'order_created']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Created Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }

        if ($.trim(state) == 'Approved Order'){
            meged_domain[0] = ['state', '=', 'apporve']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Approved Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }

        if ($.trim(state) == 'Rejected Order'){
            meged_domain[0] = ['state', '=', 'reject']
            if(self.js_domain){
                if(self.js_domain.split('], [').length > 1){
                    var domains = self.js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.js_domain.split(',')[0] !== '[]'){
                    var js_domain = self.js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[2] = js_domain
                }
            }
            self.do_action({
                name: 'Rejected Order',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'order.order',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }
        var meged_domain = new Array();
        if ($.trim(state) == 'Total Assets'){
            if(self.assets_js_domain){
                if(self.assets_js_domain.split('], [').length > 1){
                    var domains = self.assets_js_domain.split('], [');
                    meged_domain[0] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[1] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[0].includes('plant_id')){
                        meged_domain[0][2] = parseInt(meged_domain[0][2])
                    } else if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[0][2])
                    }
                } else if (self.assets_js_domain.split(',')[0] !== '[]'){
                    var assets_js_domain = self.assets_js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[0] = ['plant_id', 'in', self.plant_ids]
                    meged_domain[1] = assets_js_domain
                }
            }
            self.do_action({
                name: 'Total Assets',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'asset.management',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }
        if ($.trim(state) == 'Assets Verified'){
            meged_domain[0] = ['physical_count', '>', 0]
            if(self.assets_js_domain){
                if(self.assets_js_domain.split('], [').length > 1){
                    var domains = self.assets_js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.assets_js_domain.split(',')[0] !== '[]'){
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    var assets_js_domain = self.assets_js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[2] = assets_js_domain
                }
            }
            self.do_action({
                name: 'Assets Verified',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'asset.management',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }
        if ($.trim(state) == 'Assets Pending for Verification'){
            meged_domain[0] = ['physical_count', '<=', 0]
            if(self.assets_js_domain){
                if(self.assets_js_domain.split('], [').length > 1){
                    var domains = self.assets_js_domain.split('], [');
                    meged_domain[1] = domains[0].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    meged_domain[2] = domains[1].replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',');
                    if(meged_domain[1].includes('plant_id')){
                        meged_domain[1][2] = parseInt(meged_domain[1][2])
                    } else if(meged_domain[2].includes('plant_id')){
                        meged_domain[2][2] = parseInt(meged_domain[2][2])
                    }
                } else if (self.assets_js_domain.split(',')[0] !== '[]'){
                    meged_domain[1] = ['plant_id', 'in', self.plant_ids]
                    var assets_js_domain = self.assets_js_domain.replaceAll("'", "").replaceAll('[','').replaceAll(']','').replaceAll(' ','').split(',')
                    meged_domain[2] = assets_js_domain
                }
            }
            self.do_action({
                name: 'Assets Pending for Verification',
                views: [[false, 'list'], [false, 'form']],
                domain: meged_domain,
                res_model: 'asset.management',
                type: 'ir.actions.act_window',
                target: 'current',
            });
        }
    },
});

core.action_registry.add('asset_dashboard', Dashboard);

return Dashboard;
});
