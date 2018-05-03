/**
 * Created by Administrator on 2018/4/8.
 */

// 定义配置信息
var sniffer = {
    'report_url': 'http://127.0.0.1:9000/api/data/report',
    'bandwith_test_img': null,
    'site_id': 1,
    'collect': PerformanceCollect
};

//store all the performance data
var PerformanceData = {};


// 主执行函数
function PerformanceCollect(configs) {
    //获取所有静态文件时间
    getStaticResourceTiming();
    //通过浏览器接口获取页面加载各项时间
    timing.getTimes();
    //汇报前带上站点id
    PerformanceData.site_id = configs.site_id;
    console.log(PerformanceData);
    //汇报数据
    do_jsonp(configs.report_url, PerformanceData);
}

// 获取所有静态文件的下载时间
function getStaticResourceTiming() {
    PerformanceData['resources_load_time'] = {};
    var resourceList = window.performance.getEntriesByType("resource");
    //resourceList数据格式
    //  [PerformanceResource,PerformanceResource,PerformanceResource]
    //   PerformanceResource = {name:xxx,duration:xxx}
    for (i = 0;i < resourceList.length;i++){
        //PerformanceData['resource_load_time'][resourceList[i].name] = resourceList[i].duration;
        PerformanceData['resources_load_time'][resourceList[i].name] = resourceList[i].responseEnd - resourceList[i].startTime;
    }
}

// 获取页面加载的各项时间
(function(window) {
    'use strict';

    /**
     * Navigation Timing API helpers
     * timing.getTimes();
     **/
    window.timing = window.timing || {
        /**
         * Outputs extended measurements using Navigation Timing API
         * @param  opts Options (simple (bool) - opts out of full data view)
         * @return Object      measurements
         */
        getTimes: function(opts) {
            var performance = window.performance || window.webkitPerformance || window.msPerformance || window.mozPerformance;

            if (performance === undefined) {
                return false;
            }

            var timing = performance.timing;
            var api = {};
            opts = opts || {};

            if (timing) {
                if(opts && !opts.simple) {
                    for (var k in timing) {
                        if (timing.hasOwnProperty(k)) {
                            api[k] = timing[k];
                        }
                    }
                }

                // Time to first paint
                if (api.firstPaint === undefined) {
                    // All times are relative times to the start time within the
                    // same objects
                    var firstPaint = 0;

                    // Chrome
                    if (window.chrome && window.chrome.loadTimes) {
                        // Convert to ms
                        firstPaint = window.chrome.loadTimes().firstPaintTime * 1000;
                        api.firstPaintTime = firstPaint - (window.chrome.loadTimes().startLoadTime*1000);
                    }
                    // IE
                    else if (typeof window.performance.timing.msFirstPaint === 'number') {
                        firstPaint = window.performance.timing.msFirstPaint;
                        api.firstPaintTime = firstPaint - window.performance.timing.navigationStart;
                    }
                    // Firefox
                    // This will use the first times after MozAfterPaint fires
                    //else if (window.performance.timing.navigationStart && typeof InstallTrigger !== 'undefined') {
                    //    api.firstPaint = window.performance.timing.navigationStart;
                    //    api.firstPaintTime = mozFirstPaintTime - window.performance.timing.navigationStart;
                    //}
                    if (opts && !opts.simple) {
                        api.firstPaint = firstPaint;
                    }
                }

                // Total time from start to load
                api.loadTime = timing.loadEventEnd - timing.fetchStart;
                // Time spent constructing the DOM tree
                api.domReadyTime = timing.domComplete - timing.domInteractive;
                // Time consumed preparing the new page
                api.readyStart = timing.fetchStart - timing.navigationStart;
                // Time spent during redirection
                api.redirectTime = timing.redirectEnd - timing.redirectStart;
                // AppCache
                api.appcacheTime = timing.domainLookupStart - timing.fetchStart;
                // Time spent unloading documents
                api.unloadEventTime = timing.unloadEventEnd - timing.unloadEventStart;
                // DNS query time
                api.lookupDomainTime = timing.domainLookupEnd - timing.domainLookupStart;
                // TCP connection time
                api.connectTime = timing.connectEnd - timing.connectStart;
                // Time spent during the request
                api.requestTime = timing.responseEnd - timing.requestStart;
                // Request to completion of the DOM loading
                api.initDomTreeTime = timing.domInteractive - timing.responseEnd;
                // Load event time
                api.loadEventTime = timing.loadEventEnd - timing.loadEventStart;
                //below customization
                //navi type
                api.navigationType = window.performance.navigation.type;
            }
            PerformanceData.times = api; //把数据 存到全局数组
            return api;
        },
        /**
         * Uses console.table() to print a complete table of timing information
         * @param  Object opts Options (simple (bool) - opts out of full data view)
         */
        printTable: function(opts) {
            var table = {};
            var data  = this.getTimes(opts) || {};
            Object.keys(data).sort().forEach(function(k) {
                table[k] = {
                    ms: data[k],
                    s: +((data[k] / 1000).toFixed(2))
                };
            });
            console.table(table);
        },
        /**
         * Uses console.table() to print a summary table of timing information
         */
        printSimpleTable: function() {
            this.printTable({simple: true});
        }
    };

})(this);

// 执行jsonp跨域请求
function do_jsonp(url, data) {
    console.log("-->", url);
    var data_json = JSON.stringify(data);

    //生成url
    var url_with_data = url + "?callback=jsonpcallback" + "&data=" + data_json;

    //创建script调用标签
    var Script = document.createElement('script');
    console.log('src:' + url_with_data);
    Script.src = url_with_data;
    //document.body.appendChild(Scrip);
    document.body.appendChild(Script);
}

// jsonp回调函数,此处只用作测试，没有实际效果
function jsonpcallback(json) {
    console.log(json.Remark);//Object { email="中国", email2="中国222"}
}


// start
sniffer.collect(sniffer);