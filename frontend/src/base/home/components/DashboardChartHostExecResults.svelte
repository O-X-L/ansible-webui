<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { init, use, type ECharts, type ComposeOption } from 'echarts/core';
    import { BarChart } from 'echarts/charts';
    import type { BarSeriesOption } from 'echarts/charts';
    import {
        GridComponent,
        TooltipComponent,
        LegendComponent,
        TitleComponent,
        DatasetComponent,
    } from 'echarts/components';
    import type { 
        GridComponentOption, 
        TooltipComponentOption, 
        LegendComponentOption, 
        TitleComponentOption, 
        DatasetComponentOption,
    } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';

    use([
        TitleComponent,
        GridComponent,
        TooltipComponent,
        LegendComponent,
        DatasetComponent,
        BarChart,
        CanvasRenderer
    ]);

    type EChartsOption = ComposeOption<
        | BarSeriesOption
        | GridComponentOption
        | TitleComponentOption
        | TooltipComponentOption
        | LegendComponentOption
        | DatasetComponentOption
    >;

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { getDarkLightMode } from '../../DarkLightMode.js';
    import type { statsJobs, statsExecutionHost } from '../Types.js';
    import { 
        CHART_COLOR_SUCCESS, 
        CHART_COLOR_FAILED, 
        CHART_COLOR_CHANGED, 
        CHART_COLOR_UNREACHABLE,
        CHART_COLOR_SKIPPED,
    } from '../../../util/colors.js';

    let { data }: { data: statsJobs } = $props();

    let chartContainer: HTMLElement;
    let hostResultsChart: ECharts | null = null;

    function t(code: string) : string {
        return tq($share, code);
    }

    /**
     * Calculates the execution count for succeeded, changed, unreachable, and failed runs per host.
     */
    function getExecHostChartData() : { 
        labels: string[], 
        successData: number[], 
        changedData: number[],
        unreachableData: number[],
        failedData: number[],
        skippedData: number[],
    } {
        let counters: { [key: string]: { failed: number, success: number, unreachable: number, changed: number, skipped: number } } = {};

        for (let s of data['stats']) {
            const overallFailed = s[5] == 1;

            for (const hs of s[6] as statsExecutionHost[]) {
                const [h, tasks_unreachable, tasks_ok, tasks_failed, tasks_changed] = [hs[0], hs[1],  hs[3], hs[4], hs[7]];
                if (!counters[h]) {
                    counters[h] = { failed: 0, success: 0, unreachable: 0, changed: 0, skipped: 0 };
                }

                if (overallFailed) {
                    counters[h].failed += 1;

                } else if (tasks_unreachable == 1) {
                    counters[h].unreachable += 1;

                } else if (tasks_failed > 0) { 
                    counters[h].failed += 1;

                } else if (tasks_changed > 0) { 
                    counters[h].changed += 1;

                } else if (tasks_ok == 0) {
                    // nothing happened..
                    counters[h].skipped += 1;

                } else {
                    counters[h].success += 1;
                }
            }
        }

        const labels = Object.keys(counters);
        const successData = labels.map(name => counters[name].success);
        const changedData = labels.map(name => counters[name].changed);
        const unreachableData = labels.map(name => counters[name].unreachable);
        const failedData = labels.map(name => counters[name].failed);
        const skippedData = labels.map(name => counters[name].skipped);
        
        return { labels, successData, changedData, unreachableData, failedData, skippedData };
    }

    /**
     * Initializes the ECharts instance and sets up the chart options.
     */
    function addExecHostChart() {
        const isDark = getDarkLightMode() == 'dark';
        const textColor = isDark ? '#ADBABD' : '#333';
        
        if (!chartContainer) return;
        hostResultsChart = init(chartContainer, isDark ? 'dark' : 'light');

        const { labels, successData, changedData, unreachableData, failedData, skippedData } = getExecHostChartData();

        const option: EChartsOption = {
            title: {
                // text: t('db.chart.exec_results_by_host'),
                left: 'center',
                textStyle: {
                    color: textColor
                }
            },
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' }
            },
            legend: {
                data: [
                    t('jobs.info.succeeded'),
                    t('jobs.info.changed'),
                    t('jobs.info.unreachable'),
                    t('jobs.info.failed'),
                    t('jobs.info.skipped'),
                ],
                bottom: '0%',
                textStyle: {
                    color: textColor
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '10%',
                containLabel: true
            },
            xAxis: {
                type: 'value',
                name: t('db.runs'),
                axisLabel: {
                    color: textColor
                },
                splitLine: {
                    lineStyle: {
                        color: isDark ? '#333' : '#eee'
                    }
                }
            },
            yAxis: {
                type: 'category',
                data: labels,
                name: t('config.form.hostnames'),
                nameLocation: 'end',
                axisLabel: {
                    color: textColor,
                    interval: 0,
                    formatter: (value) => {
                        // Truncate long labels
                        return value.length > 20 ? value.substring(0, 20) + '...' : value;
                    }
                },
            },
            series: [
                {
                    name: t('jobs.info.succeeded'),
                    type: 'bar',
                    stack: 'total',
                    data: successData,
                    itemStyle: {
                        color: CHART_COLOR_SUCCESS
                    },
                    label: {
                        show: false,
                    },
                },
                {
                    name: t('jobs.info.changed'),
                    type: 'bar',
                    stack: 'total', 
                    data: changedData,
                    itemStyle: {
                        color: CHART_COLOR_CHANGED
                    },
                    label: {
                        show: false,
                    },
                },
                {
                    name: t('jobs.info.unreachable'),
                    type: 'bar',
                    stack: 'total', 
                    data: unreachableData,
                    itemStyle: {
                        color: CHART_COLOR_UNREACHABLE
                    },
                    label: {
                        show: false,
                    },
                },
                {
                    name: t('jobs.info.failed'),
                    type: 'bar',
                    stack: 'total', 
                    data: failedData,
                    itemStyle: {
                        color: CHART_COLOR_FAILED
                    },
                    label: {
                        show: false,
                    },
                },
                {
                    name: t('jobs.info.skipped'),
                    type: 'bar',
                    stack: 'total', 
                    data: skippedData,
                    itemStyle: {
                        color: CHART_COLOR_SKIPPED
                    },
                    label: {
                        show: false,
                    },
                },
            ]
        };
        hostResultsChart.setOption(option);
        window.addEventListener('resize', resizeChart);
    }

    function resizeChart() {
        hostResultsChart?.resize();
    }

    /**
     * Updates the chart data, and refreshes the chart.
     */
    function createUpdateChart() {
        if (!hostResultsChart) {
            addExecHostChart();
            return;
        }
        
        const { labels, successData, changedData, unreachableData, failedData, skippedData } = getExecHostChartData();

        // Update option for data
        hostResultsChart.setOption({
            yAxis: {
                data: labels
            },
            series: [
                {
                    name: t('jobs.info.succeeded'),
                    data: successData,
                },
                {
                    name: t('jobs.info.changed'),
                    data: changedData,
                },
                {
                    name: t('jobs.info.unreachable'),
                    data: unreachableData,
                },
                {
                    name: t('jobs.info.failed'),
                    data: failedData,
                },
                {
                    name: t('jobs.info.skipped'),
                    data: skippedData,
                },
            ]
        }, false);
    }

    $effect(() => {
        data;
        createUpdateChart();
    });

    onMount(() => {
        addExecHostChart();
    });

    onDestroy(() => {
        window.removeEventListener('resize', resizeChart);
        hostResultsChart?.dispose();
    });
</script>

<div bind:this={chartContainer} id="chart-exec-host-results" class="h-96 w-full" role="img" aria-label="{t('db.chart.exec_results_by_host')} Chart"></div>