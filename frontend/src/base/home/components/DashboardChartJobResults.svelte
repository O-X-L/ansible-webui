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

    // Register necessary components and charts for ECharts
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
    import type { statsJobs } from '../Types.js';
    import { tq } from '../../../util/translate.js';
    import { getDarkLightMode } from '../../DarkLightMode.js';
    import { CHART_COLOR_SUCCESS, CHART_COLOR_FAILED } from '../../../util/colors.js'; //

    let { data }: { data: statsJobs } = $props(); //

    let chartContainer: HTMLElement;
    let jobResultsChart: ECharts | null = null;

    function t(code: string) : string {
        return tq($share, code);
    }

    /**
     * Calculates the execution count for succeeded and failed jobs.
     */
    function getExecResultChartData() : { labels: string[], successData: number[], failedData: number[] } {
        let counters: { [key: string]: { failed: number, success: number } } = {};

        for (let s of data['stats']) { //
            let n = data['mapping']['jobs'][s[0]];
            if (!counters[n]) {
                counters[n] = { failed: 0, success: 0 };
            }
            if (s[5] == 1) {
                counters[n]['failed'] += 1;
            } else {
                counters[n]['success'] += 1;
            }
        }

        const labels = Object.keys(counters);
        const successData = labels.map(name => counters[name].success);
        const failedData = labels.map(name => counters[name].failed);
        
        return { labels, successData, failedData };
    }

    /**
     * Initializes the ECharts instance and sets up the chart options.
     */
    function addExecResultChart() {
        const isDark = getDarkLightMode() == 'dark';
        const textColor = isDark ? '#ADBABD' : '#333';
        
        if (!chartContainer) return;
        jobResultsChart = init(chartContainer, isDark ? 'dark' : 'light');

        const { labels, successData, failedData } = getExecResultChartData();

        const option: EChartsOption = {
            title: {
                // text: t('db.chart.exec_results_by_job'),
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
                data: [t('jobs.info.succeeded'), t('jobs.info.failed')],
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
                name: t('jobs.job'),
                nameLocation: 'end',
                axisLabel: {
                    color: textColor,
                    interval: 0,
                    formatter: (value) => {
                        // Truncate long labels
                        return value.length > 30 ? value.substring(0, 27) + '...' : value;
                    }
                },
            },
            series: [
                {
                    name: `✅ ${t('jobs.info.succeeded')}`,
                    type: 'bar',
                    stack: 'total',
                    data: successData,
                    itemStyle: {
                        color: CHART_COLOR_SUCCESS
                    },
                    label: {
                        show: true,
                        position: 'insideRight',
                        color: 'white',
                    },
                },
                {
                    name: `❌ ${t('jobs.info.failed')}`,
                    type: 'bar',
                    stack: 'total',
                    data: failedData,
                    itemStyle: {
                        color: CHART_COLOR_FAILED
                    },
                    label: {
                        show: true,
                        position: 'insideRight',
                        color: 'white',
                    },
                }
            ]
        };
        jobResultsChart.setOption(option);
        window.addEventListener('resize', resizeChart);
    }

    function resizeChart() {
        jobResultsChart?.resize();
    }

    /**
     * Updates the chart data, and refreshes the chart.
     */
    function createUpdateChart() {
        if (!jobResultsChart) {
            addExecResultChart(); //
            return;
        }
        
        const { labels, successData, failedData } = getExecResultChartData(); //

        // Update option for data
        jobResultsChart.setOption({
            yAxis: {
                data: labels
            },
            series: [
                {
                    data: successData,
                },
                {
                    data: failedData,
                }
            ]
        }, false);
    }

    $effect(() => {
        data;
        createUpdateChart();
    });

    onMount(() => {
        addExecResultChart();
    });

    onDestroy(() => {
        window.removeEventListener('resize', resizeChart);
        jobResultsChart?.dispose();
    });
</script>

<div bind:this={chartContainer} id="chart-exec-results" class="h-96 w-full" role="img" aria-label="{t('db.chart.exec_results_by_job')} Chart"></div>