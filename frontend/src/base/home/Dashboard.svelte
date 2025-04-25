<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        Spinner, Heading, Span, Select, Label, Button, Tooltip as FlowbiteTooltip, Input,
    } from 'flowbite-svelte';
    import { RefreshOutline } from 'flowbite-svelte-icons';

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
    import { classModalLabel } from '../Style.js';
    import { tq } from '../../util/translate.js';
    import { arraysEqual } from '../../util/main.js';
    import { type formChoiceType } from '../Types.js';
    import { classFooterSpacing } from '../Style.js';
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

    const CHART_TIME_MAX_DATAPOINTS = 200;
    let updateLoop: number = $state(0);

    const PERIOD_CHOICES: formChoiceType[] = [
        {name: t('db.time.minutes'), value: 'm'},
        {name: t('db.time.hours'), value: 'h'},
        {name: t('db.time.days'), value: 'd'},
        {name: t('db.time.weeks'), value: 'w'},
        {name: t('db.time.months'), value: 'M'},
    ];
    let statsPeriodValue: number = $state(1);
    let statsPeriodKind: string = $state('d');

    interface statsJobsMapping {
        jobs: any
        users: any
        status: any
        stats: any
        host_stats: any
    }
    type statsExecutionHost = [
        string,  // 0 hostname
        number,  // 1 unreachable (0/1 boolean)
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
        number,  // 5 failed (0/1 boolean)
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
    let loaded = $state(false);

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
    let chartDataExecOverTimeJobs: string[] = $state([]);
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
            if (s[5] == 1) {
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
                    label: `✅ ${t('jobs.info.succeeded')}`,
                    data: Object.values(counters).map((item) => item.success),
                    backgroundColor: new Array(len).fill(CHART_COLOR_SUCCESS),
                },
                {
                    label: `❌ ${t('jobs.info.failed')}`,
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
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: t('db.chart.exec_results_by_job'),
                    }
                }
            }
        }
        chartDataExecResults = new Chart(document.getElementById('chart-exec-results'), c);
    }

    function getExecByUserChartData() : chartData {
        let data = {};

        for (let s of statsJobsData['stats']) {
            let n = t('jobs.info.scheduled');
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
                label: t('db.runs'),
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
                // maintainAspectRatio: false,
                plugins: {
                    /*
                    legend: {
                        position: 'top',
                    },
                    */
                    title: {
                        display: true,
                        text: t('db.chart.exec_by_user'),
                    }
                }
            }
        }
        chartDataExecByUser = new Chart(document.getElementById('chart-exec-by-user'), c);
    }

    function getExecOverTimeData() : [boolean, chartDataTime] {
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
                // console.log("INVALID TIME:", s);
                continue;
            }
            if (s[5] == 1) {
                jobs_failed[n].push({x: s[4] * 1000, y: s[3]});
            } else {
                jobs_success[n].push({x: s[4] * 1000, y: s[3]});
            }
            i += 1;
        }

        let dataset_keys = [];
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
            let d = `✅ ${k}`;
            datasets.push({
                label: d,
                data: v,
                pointBackgroundColor: getRandomTailwindColorPositive(),
                ...defaults,
            })
            dataset_keys.push(d);
        }
        for (let [k, v] of Object.entries(jobs_failed)) {
            let d = `❌ ${k}`;
            datasets.push({
                label: d,
                data: v,
                pointBackgroundColor: getRandomTailwindColorNegative(),
                ...defaults,
            })
            dataset_keys.push(d);
        }

        let changed = !arraysEqual(dataset_keys.sort(), chartDataExecOverTimeJobs);
        if (changed) {
            chartDataExecOverTimeJobs = dataset_keys;
        }
        return [changed, {datasets: datasets}];
    }

    function addExecOverTimeChart() {
        let [_, data] = getExecOverTimeData();
        let c = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        text: t('db.chart.exec_over_time'),
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label
                            },
                            afterLabel: function(context) {
                                return `${t('jobs.info.duration')}: ${context.parsed.y} s`;  // run time; todo: seconds to minutes
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
                            text: t('logs.time')
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: t('jobs.info.duration')
                        },
                        min: -1,
                    }
                },
            },
        };
        chartDataExecOverTime = new Chart(document.getElementById('chart-exec-over-time'), c);
    }

    function getExecHostChartData() : chartData {
        let counters = {};

        for (let s of statsJobsData['stats']) {
            for (let hs of s[6]) {
                let h = hs[0];
                if (!counters[h]) {
                    counters[h] = {'failed': 0, 'success': 0, 'unreachable': 0, 'changed': 0};
                }
                if (s[5] == 1) {
                    counters[h]['failed'] += 1;
                } else if (hs[1] == 1) {
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
                    label: `✅ ${t('jobs.info.succeeded')}`,
                    data: Object.values(counters).map((item) => item.success),
                    backgroundColor: new Array(len).fill(CHART_COLOR_SUCCESS),
                },
                {
                    label: `🔁 ${t('jobs.info.changed')}`,
                    data: Object.values(counters).map((item) => item.changed),
                    backgroundColor: new Array(len).fill(CHART_COLOR_CHANGED),
                },
                {
                    label: `⚫ ${t('jobs.info.unreachable')}`,
                    data: Object.values(counters).map((item) => item.unreachable),
                    backgroundColor: new Array(len).fill(CHART_COLOR_UNREACHABLE),
                },
                {
                    label: `❌ ${t('jobs.info.failed')}`,
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
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: t('db.chart.exec_results_by_host'),
                    }
                }
            }
        }
        chartDataExecHostResults = new Chart(document.getElementById('chart-exec-host-results'), c);
    }

    function createUpdateChartData() {
        if (!chartDataExecOverTime) {
            addExecOverTimeChart();
        } else {
            let [changed, n] = getExecOverTimeData();

            // only replace the whole dataset if jobs change (reloads whole chart)
            if (changed) {
                chartDataExecOverTime.data.datasets = n.datasets;

            } else if (chartDataExecOverTime !== undefined) {
                for (let i = 0; i < n.datasets.length; i++) {
                    chartDataExecOverTime.data.datasets[i].data = n.datasets[i].data;
                }
            }
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

    function loadJobStats(j: any) {
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
            loaded = true;
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
        } else if (statsPeriodValue != 0) {
            limit = `limit_time=${statsPeriodValue}${statsPeriodKind}`;
        }
        apiGet(`stats/jobs?${limit}`, loadJobStats);
    }

    function updateStatsPeriod() {
        statsJobsData.stats = [];
        lastExecTime = 0;
        loaded = false;
        buildJobStats();
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

<div class="flex justify-between max-sm:flex-wrap">
    <div>
        <Heading tag="h1" class="mb-4 mt-10 md:mt-8" customSize="text-5xl font-extrabold md:text-6xl">
            <Span gradient gradientClass="text-transparent bg-clip-text bg-gradient-to-r to-yellow-400 from-primary-600">
                {t('db.stats')}
            </Span>
        </Heading>
    </div>
    <div>
        <div class="max-w-72">
            <Label class="{classModalLabel} mb-2">{t('db.time.select')}</Label>
            <div class="flex">
                <div class="shrink">
                    <Input type="number" bind:value={statsPeriodValue} />
                </div>
                <div class="shrink">
                    <Select items={PERIOD_CHOICES} bind:value={statsPeriodKind} />
                </div>
                <div class="shrink ml-2">
                    <Button on:click={() => {updateStatsPeriod()}}><RefreshOutline/></Button>
                    <FlowbiteTooltip>{t('btn.update')}</FlowbiteTooltip>
                </div>
            </div>
        </div>
    </div>
</div>

{#if !loaded}
    <div class="text-center mt-20">
        <Spinner/>
    </div>
{/if}

<div class="flex justify-center mb-20 mt-10">
    <div class="w-full min-h-[300px] sm:max-h-[30rem]">
        <canvas id="chart-exec-over-time"></canvas>
    </div>
</div>
<div class="flex justify-center mb-20 mt-10">
    <div class="w-full grow min-h-[300px] sm:max-h-[30rem]">
        <canvas id="chart-exec-results"></canvas>
    </div>
</div>
<div class="flex justify-center mb-20 mt-10">
    <div class="w-full grow min-h-[300px] sm:max-h-[30rem]">
        <canvas id="chart-exec-host-results"></canvas>
    </div>
</div>
<div class="flex justify-center mb-20 mt-10">
    <div class="my-auto max-w-[70%] sm:w-80">
        <canvas id="chart-exec-by-user"></canvas>
    </div>
</div>

<!--
    IDEAS:
        * stats of failed jobs (for all readable - user can narrow it down to single jobs)
        * stats of changed items
        * stats per host (allow user to select single host)
          * changed items
          * when did which playbook target the host; who executed it

    todo: allow users to choose stats time (hours, days, weeks, months)
        
-->

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
