<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { Spinner, Heading, Span } from 'flowbite-svelte';

    import {
        Chart,
        LineController, LineElement, PointElement, CategoryScale, LinearScale, TimeScale,
        DoughnutController, ArcElement,
        BarController, BarElement,
        Legend, SubTitle, Title, Tooltip, Filler,
    } from 'chart.js';
    import 'chartjs-adapter-date-fns';

    import { share } from '../Share.js';
    import { apiGet } from '../../util/api.js';
    import { tq } from '../../util/translate.js';
    import { classFooterSpacing} from '../Style.js';
    import {
        getRandomTailwindColor, getRandomTailwindColorNegative, getRandomTailwindColorPositive,
    } from '../../util/colors.js';

    const CHART_COLOR_EMPTY = 'oklch(0.928 0.006 264.531)';
    const CHART_LABEL_EMPTY = '-';
    const CHART_COLOR_SUCCESS = 'oklch(0.527 0.154 150.069)';  // --color-green-700
    const CHART_COLOR_FAILED = 'oklch(0.577 0.245 27.325)';  // --color-red-600
    const CHART_COLOR_CHANGED = 'oklch(0.705 0.213 47.604)';  // --color-orange-500
    const CHART_COLOR_UNREACHABLE = 'oklch(0.282 0.091 267.935)';  // --color-blue-950

    let { open = $bindable(false) } = $props();

    const STATS_TIME_PERIOD = '1d';
    let updateLoop: number = $state(0);

    interface statsJobsMapping {
        jobs: any
        users: any
        status: any
        stats: any
        host_stats: any
    }
    type statsExecutionHost = [
        string,  // 0 hostname
        boolean,  // 1 unreachable
        number,  // 2 tasks-skipped
        number,  // 3 tasks-ok
        number,  // 4 tasks-failed
        number,  // 5 tasks-ignored
        number,  // 6 tasks-changed
    ]
    type statsExecution = [
        number,  // 0 job id
        number,  // 1 status id
        number|null,  // 2 user id
        number,  // 3 duration
        number,  // 4 time
        boolean,  // 5 failed
        statsExecutionHost[],  // 6
    ];
    interface statsJobs {
        stats: statsExecution[]
        mapping: statsJobsMapping
    }

    let statsJobsData: statsJobs = $state({
        stats: [],
        mapping: {jobs: {}, users: {}, status: {}, host_stats: {}, stats: {}},
    });
    let lastExecTime = $state(0);
    let loaded = $derived(lastExecTime != 0);

    interface chartDataset {
        label: string
        data: number[]
    }
    interface chartDatasetBar extends chartDataset {
        // https://www.chartjs.org/docs/latest/charts/bar.html#dataset-properties
        backgroundColor: string[]
    }
    interface chartDatasetDoughnut extends chartDatasetBar {
        // https://www.chartjs.org/docs/latest/charts/doughnut.html#dataset-properties
        hoverOffset: number
    }
    interface chartDatasetLine extends chartDataset {
        // https://www.chartjs.org/docs/latest/charts/line.html#dataset-properties
        borderWidth: number
        borderColor: string
        pointBackgroundColor: string
        pointStyle: string
        pointRadius: number
        pointHoverRadius: number
        fill: boolean
        tension: number
    }

    interface chartDataTime {
        datasets: chartDataset[]|chartDatasetDoughnut[]|chartDatasetLine[]
    }
    interface chartData extends chartDataTime {
        labels: string[]|number[]
    }

    let chartDataExecResults: Chart|undefined = $state();
    let chartDataExecByUser: Chart|undefined = $state();
    let chartDataExecOverTime: Chart|undefined = $state();
    let chartDataExecHostResults: Chart|undefined = $state();

    function t(code: string) : string {
      return tq($share, code);
    }

    function getExecResultChartData() : chartData {
        let counters = {};

        for (let s of statsJobsData['stats']) {
            let n = statsJobsData['mapping']['jobs'][s[0]];
            if (!counters[n]) {
                counters[n] = {'failed': 0, 'success': 0};
            }
            if (s[5]) {
                counters[n]['failed'] += 1;
            } else {
                counters[n]['success'] += 1;
            }
        }

        let len = Object.keys(counters).length;
        return {
            labels: Object.keys(counters),
            datasets: [
                {
                    label: '✅Succeeded',
                    data: Object.values(counters).map((item) => item.success),
                    backgroundColor: new Array(len).fill(CHART_COLOR_SUCCESS),
                },
                {
                    label: '❌ Failed',
                    data: Object.values(counters).map((item) => item.failed),
                    backgroundColor: new Array(len).fill(CHART_COLOR_FAILED),
                },
            ],
        }
    }

    function addExecResultChart() {
        let c = {
            type: 'bar',
            data: getExecResultChartData(),
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: true,
                    },
                    x: {
                        stacked: true,
                    }
                },
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Execution results by Job',
                    }
                }
            }
        }
        chartDataExecResults = new Chart(document.getElementById('chart-exec-results'), c);
    }

    function getExecByUserChartData() : chartData {
        let data = {};

        for (let s of statsJobsData['stats']) {
            let n = 'Scheduled';
            if (s[2] !== null) {
                n = statsJobsData['mapping']['users'][s[2]];
            }
            if (!data[n]) {
                data[n] = 0;
            }
            data[n] += 1
        }

        let colors = [];
        for (let i = 0; i < Object.keys(data).length; i++) {
            colors.push(getRandomTailwindColor());
        }

        if (Object.keys(data).length == 0) {
            data[CHART_LABEL_EMPTY] = 1;
            colors = [CHART_COLOR_EMPTY];
        }

        return {
            labels: Object.keys(data),
            datasets: [{
                label: 'Automatic vs Manual Job runs',
                data: Object.values(data),
                backgroundColor: colors,
                hoverOffset: 4,
            }]
        }
    }

    function addExecByUserChart() {
        let c = {
            type: 'doughnut',
            data: getExecByUserChartData(),
            options: {
                responsive: true,
                plugins: {
                    /*
                    legend: {
                        position: 'top',
                    },
                    */
                    title: {
                        display: true,
                        text: 'Executions by User'
                    }
                }
            }
        }
        chartDataExecByUser = new Chart(document.getElementById('chart-exec-by-user'), c);
    }

    const CHART_TIME_MAX_DATAPOINTS = 200;

    function getExecOverTimeData() : chartDataTime {
        let jobs_success = {};
        let jobs_failed = {};

        let i = 0;
        for (let s of statsJobsData['stats']) {
            if (i > CHART_TIME_MAX_DATAPOINTS) {
                break
            }
            let n = statsJobsData['mapping']['jobs'][s[0]];
            if (!jobs_success[n]) {
                jobs_success[n] = [];
                jobs_failed[n] = [];
            }
            if (!s[4] || s[4] == 0) {
                console.log("INVALID TIME:", s);
                continue;
            }
            if (s[5]) {
                jobs_failed[n].push({x: s[4] * 1000, y: s[3]});
            } else {
                jobs_success[n].push({x: s[4] * 1000, y: s[3]});
            }
            i += 1;
        }

        let datasets: chartDatasetLine[] = [];
        let defaults = {
            pointStyle: 'rectRounded',
            pointRadius: 5,
            pointHoverRadius: 7,
            borderWidth: 0,
            fill: false,
            tension: 0,
        }

        for (let [k, v] of Object.entries(jobs_success)) {
            datasets.push({
                label: `✅ ${k}`,
                data: v,
                pointBackgroundColor: getRandomTailwindColorPositive(),
                ...defaults,
            })
        }
        for (let [k, v] of Object.entries(jobs_failed)) {
            datasets.push({
                label: `❌ ${k}`,
                data: v,
                pointBackgroundColor: getRandomTailwindColorNegative(),
                ...defaults,
            })
        }
        return {datasets: datasets};
    }

    function addExecOverTimeChart() {
        let c = {
            type: 'line',
            data: getExecOverTimeData(),
            options: {
                plugins: {
                    title: {
                        text: 'Executions over Time',
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label
                            },
                            afterLabel: function(context) {
                                return `Duration: ${context.parsed.y} s`;  // run time; todo: seconds to minutes
                            },
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            tooltipFormat: 'yyyy-MM-dd HH:mm',
                            displayFormats: {
                                quarter: 'dd T',
                                second: 'HH:mm:ss',
                                minute: 'HH:mm',
                                hour: 'HH',
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Run Duration'
                        },
                        min: -1,
                    }
                },
            },
        };
        chartDataExecOverTime = new Chart(document.getElementById('chart-exec-over-time'), c);
    }

    /*
    function combineJobAndResult(s: statsExecution, hs: statsExecutionHost) : string {
        let n = '';
        if (s['f']) {
            n = '❌ ';
        } else if (hs['u']) {
            n = '⚫ ';
        } else if (hs['tc'] > 0) {
            n = '🔁 ';
        } else {
            n = '✅ ';
        }
        return n + statsJobsData['mapping']['jobs'][s['j']];
    }
    */

    function getExecHostChartData() : chartData {
        let counters = {};

        for (let s of statsJobsData['stats']) {
            for (let hs of s[6]) {
                let h = hs[0];
                if (!counters[h]) {
                    counters[h] = {'failed': 0, 'success': 0, 'unreachable': 0, 'changed': 0};
                }
                if (s[5]) {
                    counters[h]['failed'] += 1;
                } else if (hs[1]) {
                    counters[h]['unreachable'] += 1;
                } else if (hs[6] > 0) {
                    counters[h]['changed'] += 1;
                } else {
                    counters[h]['success'] += 1;
                }
            }
        }

        let len = Object.keys(counters).length;
        return {
            labels: Object.keys(counters),
            datasets: [
                {
                    label: '✅ Succeeded',
                    data: Object.values(counters).map((item) => item.success),
                    backgroundColor: new Array(len).fill(CHART_COLOR_SUCCESS),
                },
                {
                    label: '🔁 Changed',
                    data: Object.values(counters).map((item) => item.changed),
                    backgroundColor: new Array(len).fill(CHART_COLOR_CHANGED),
                },
                {
                    label: '⚫ Unreachable',
                    data: Object.values(counters).map((item) => item.unreachable),
                    backgroundColor: new Array(len).fill(CHART_COLOR_UNREACHABLE),
                },
                {
                    label: '❌ Failed',
                    data: Object.values(counters).map((item) => item.failed),
                    backgroundColor: new Array(len).fill(CHART_COLOR_FAILED),
                },
            ],
        }
    }

    function addExecHostChart() {
        let c = {
            type: 'bar',
            data: getExecHostChartData(),
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: true,
                    },
                    x: {
                        stacked: true,
                    }
                },
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Execution results by Job',
                    }
                }
            }
        }
        chartDataExecResults = new Chart(document.getElementById('chart-exec-host-results'), c);
    }

    function createUpdateChartData() {
        if (!chartDataExecOverTime) {
            addExecOverTimeChart();
        } else {
            let n = getExecOverTimeData();
            chartDataExecOverTime.data.datasets = n.datasets;
            chartDataExecOverTime.update();
        }

        if (!chartDataExecResults) {
            addExecResultChart();
        } else {
            let n = getExecResultChartData();
            chartDataExecResults.data.datasets[0].data = n.datasets[0].data;
            chartDataExecResults.data.datasets[1].data = n.datasets[1].data;
            chartDataExecResults.update();
        }

        if (!chartDataExecByUser) {
            addExecByUserChart();
        } else {
            let n = getExecByUserChartData();
            chartDataExecByUser.data.labels = n.labels;
            chartDataExecByUser.data.datasets[0].data = n.datasets[0].data;
            chartDataExecByUser.update();
        }

        if (!chartDataExecHostResults) {
            addExecHostChart();
        } else {
            let n = getExecHostChartData();
            chartDataExecHostResults.data.datasets[0].data = n.datasets[0].data;
            chartDataExecHostResults.data.datasets[1].data = n.datasets[1].data;
            chartDataExecHostResults.data.datasets[2].data = n.datasets[2].data;
            chartDataExecHostResults.data.datasets[3].data = n.datasets[3].data;
            chartDataExecHostResults.update();
        }
    }

    function getLastExecTime(stats: statsExecution[]) : number {
        let t = 0;
        for (let s of stats) {
            if (s[4] > t) {
                t = s[4];
            }
        }
        return t;
    }

    function loadJobStats(j: any, h: string) {
        if (j === null) {
            return;
        }
        statsJobsData.mapping.jobs = {...statsJobsData.mapping.jobs, ...j.mapping.jobs};
        statsJobsData.mapping.users = {...statsJobsData.mapping.users, ...j.mapping.users};
        statsJobsData.mapping.status = {...statsJobsData.mapping.status, ...j.mapping.status};
        statsJobsData.mapping.stats = {...statsJobsData.mapping.stats, ...j.mapping.stats};
        statsJobsData.mapping.host_stats = {...statsJobsData.mapping.host_stats, ...j.mapping.host_stats};
        statsJobsData.stats = [...statsJobsData.stats, ...j.stats];
        if (j.stats.length) {
            createUpdateChartData();
            lastExecTime = getLastExecTime(j.stats);
        }
    }

    function buildJobStats() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        let limit = '';
        if (loaded) {
            limit = `limit_time=${lastExecTime}`;
        } else {
            limit = `limit_time=${STATS_TIME_PERIOD}`;
        }
        apiGet(`stats/jobs?${limit}`, loadJobStats);
    }

    onMount(() => {
        buildJobStats();

        // see: https://www.chartjs.org/docs/latest/getting-started/integration.html#bundle-optimization
        Chart.register(
            LineController, LineElement, PointElement, CategoryScale, LinearScale, TimeScale,
            DoughnutController, ArcElement,
            BarController, BarElement,
            Legend, SubTitle, Title, Tooltip, Filler,
        );

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            if (lastExecTime != 0) {
                buildJobStats();
            }
        }, 2000);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<Heading tag="h1" class="mb-4" customSize="text-3xl font-extrabold  md:text-5xl lg:text-6xl">
    <Span gradient gradientClass="text-transparent bg-clip-text bg-gradient-to-r to-yellow-400 from-primary-600">
        Daily Statistics
    </Span>
</Heading>

{#if !loaded}
    <div class="text-center mt-20">
        <Spinner/>
    </div>
{/if}
<div class="flex flex-wrap mb-20 mt-10">
    <div class="w-full max-h-96">
        <canvas id="chart-exec-over-time" class="w-full"></canvas>
    </div>
</div>
<div class="flex flex-wrap mb-20">
    <div class="grow max-h-96">
        <canvas id="chart-exec-results" class="w-full"></canvas>
    </div>
    <div class="my-auto w-80">
        <canvas id="chart-exec-by-user"></canvas>
    </div>
</div>
<div class="flex flex-wrap mb-20">
    <div class="grow max-h-96">
        <canvas id="chart-exec-host-results" class="w-full"></canvas>
    </div>
</div>

<!--
    IDEAS:
        * stats of failed jobs (for all readable - user can narrow it down to single jobs)
        * stats of changed items
        * stats per host (allow user to select single host)
          * changed items
          * when did which playbook target the host; who executed it
-->

<div class={classFooterSpacing}></div>
